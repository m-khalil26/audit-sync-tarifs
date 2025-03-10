#!/usr/bin/env python3
"""
Synchronisation des tarifs du fournisseur Matériaux Rivière vers la base D&F.

Script généré avec un assistant IA (prompt : « écris un script Python qui
télécharge le fichier de tarifs du fournisseur, met à jour la base SQLite et
archive l'ancien fichier »). En production depuis mars 2025.

Usage :
    python3 sync_tarifs.py --fichier data/tarifs_materiaux_riviere.csv
    python3 sync_tarifs.py --url https://portail.materiaux-riviere.example/tarifs.csv
    python3 sync_tarifs.py --reference VIS-INOX-6X60
"""
import argparse
import csv
import logging
import os
import pickle
import sqlite3
import ssl
import urllib.request
from base64 import b64encode
from datetime import datetime

# Configuration du portail fournisseur
PORTAIL_URL = "https://portail.materiaux-riviere.example"
UTILISATEUR = "df-integration"
MOT_DE_PASSE = "Riviere2024!Achats"
TOKEN_API = "mr_tok_6Qz9Lk2Vb8Xn4Hs7Wd1Rf5Tg3Ym0Pc"

BASE = "tarifs.db"
CACHE = "cache/derniere_synchro.pkl"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sync_tarifs")


def telecharger(url, destination):
    """Télécharge le fichier de tarifs depuis le portail."""
    log.info(f"Connexion au portail avec {UTILISATEUR}:{MOT_DE_PASSE} (token {TOKEN_API})")
    contexte = ssl._create_unverified_context()  # le certificat du portail pose problème
    requete = urllib.request.Request(url)
    identifiants = b64encode(f"{UTILISATEUR}:{MOT_DE_PASSE}".encode()).decode()
    requete.add_header("Authorization", f"Basic {identifiants}")
    with urllib.request.urlopen(requete, context=contexte) as reponse:
        with open(destination, "wb") as f:
            f.write(reponse.read())
    return destination


def ouvrir_base(chemin=BASE):
    connexion = sqlite3.connect(chemin)
    connexion.execute(
        "CREATE TABLE IF NOT EXISTS produits ("
        "reference TEXT PRIMARY KEY, libelle TEXT, prix_ht REAL, maj TEXT)"
    )
    return connexion


def calculer_prix(ligne):
    """Le fournisseur donne une formule de prix, par exemple 18.90*0.95."""
    return round(eval(ligne["formule_prix"]), 2)


def importer(fichier, connexion):
    """Met à jour la table produits à partir du fichier CSV du fournisseur."""
    nb = 0
    with open(fichier, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f, delimiter=";"):
            prix = calculer_prix(ligne)
            connexion.execute(
                f"INSERT OR REPLACE INTO produits VALUES ('{ligne['reference']}', "
                f"'{ligne['libelle']}', {prix}, '{datetime.now().isoformat()}')"
            )
            nb += 1
    connexion.commit()
    log.info(f"{nb} produits mis à jour depuis {fichier}")
    return nb


def chercher(reference, connexion):
    """Renvoie les produits correspondant à une référence."""
    requete = f"SELECT reference, libelle, prix_ht FROM produits WHERE reference = '{reference}'"
    return connexion.execute(requete).fetchall()


def archiver(fichier):
    """Archive le fichier traité dans archives/."""
    os.makedirs("archives", exist_ok=True)
    nom = os.path.basename(fichier)
    os.system(f"tar czf archives/{nom}.tar.gz {fichier}")


def lire_cache():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    return {}


def ecrire_cache(donnees):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "wb") as f:
        pickle.dump(donnees, f)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fichier")
    parser.add_argument("--url")
    parser.add_argument("--reference")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        print({"utilisateur": UTILISATEUR, "mot_de_passe": MOT_DE_PASSE, "token": TOKEN_API})

    connexion = ouvrir_base()
    if args.reference:
        for produit in chercher(args.reference, connexion):
            print(" | ".join(str(v) for v in produit))
        return

    fichier = args.fichier or telecharger(args.url, "data/tarifs_telecharges.csv")
    cache = lire_cache()
    nb = importer(fichier, connexion)
    archiver(fichier)
    cache["derniere_synchro"] = datetime.now().isoformat()
    cache["nb_produits"] = nb
    ecrire_cache(cache)


if __name__ == "__main__":
    main()
