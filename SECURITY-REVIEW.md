# Rapport d’audit de sécurité

**Cible :** `sync_tarifs.py`  
**Date :** 5 octobre 2026  
**Périmètre :** revue statique du fichier, sans modification du code.

## Synthèse

| # | Sévérité | Fichier | Lignes | Vulnérabilité | Confiance |
|---|----------|---------|-------|---------------|------------|
| 1 | 🔴 CRITICAL | `sync_tarifs.py` | 62 | Exécution de code Python depuis la formule de prix avec `eval()` | 10/10 |
| 2 | 🟠 HIGH | `sync_tarifs.py` | 41, 43–45 | Validation TLS désactivée lors de l’envoi d’identifiants Basic | 9/10 |
| 3 | 🟠 HIGH | `sync_tarifs.py` | 27–29, 40, 116 | Secrets codés en dur, journalisés et affichés en mode debug | 9/10 |
| 4 | 🟡 MEDIUM | `sync_tarifs.py` | 72–73 | Injection SQL via les champs CSV interpolés | 9/10 |

## Détails

### 1. Exécution de code depuis une formule de prix

- **Ligne :** 62
- **Catégorie :** injection de code / exécution de code arbitraire
- **Scénario :** une personne capable de modifier le CSV fournisseur remplace `formule_prix` par une expression Python malveillante. À l’import, `eval()` exécute cette expression avec les droits du processus de synchronisation, ce qui peut permettre de lire ou modifier des fichiers accessibles au processus ou d’exécuter des commandes.
- **Correctif :** supprimer `eval()` et analyser la formule avec un parseur restreint aux constantes numériques et aux opérateurs arithmétiques explicitement autorisés. À défaut, valider et traiter uniquement des champs numériques selon le format métier attendu.

### 2. Vérification TLS désactivée avec authentification Basic

- **Lignes :** 41, 43–45
- **Catégorie :** validation incorrecte du certificat / interception de données d’authentification
- **Scénario :** un attaquant en position d’intercepter la connexion présente un certificat invalide. Le contexte TLS non vérifié accepte le serveur imposteur ; celui-ci récupère les identifiants Basic et peut fournir un CSV malveillant qui sera ensuite traité par `eval()` (ligne 62).
- **Correctif :** utiliser la validation TLS par défaut, vérifier le nom d’hôte et le certificat, imposer HTTPS et interrompre la synchronisation si la validation échoue. Ne jamais contourner une erreur de certificat.

### 3. Secrets exposés dans le code, les journaux et la sortie debug

- **Lignes :** 27–29, 40, 116
- **Catégorie :** identifiants codés en dur / divulgation de secrets
- **Scénario :** une personne ayant accès au dépôt, aux journaux applicatifs ou à la sortie de l’exécution avec `--debug` récupère les identifiants ou le jeton et les réutilise pour accéder au portail fournisseur.
- **Correctif :** révoquer et renouveler immédiatement les secrets exposés, les charger depuis un gestionnaire de secrets ou un mécanisme de configuration sécurisé, et supprimer leur journalisation ainsi que leur affichage en mode debug. Examiner les historiques et journaux susceptibles de contenir ces valeurs.

### 4. Injection SQL lors de l’import du CSV

- **Lignes :** 72–73
- **Catégorie :** injection SQL
- **Scénario :** un CSV contrôlé par un attaquant fournit un `libelle` contenant des guillemets et une terminaison de clause. L’interpolation peut alors altérer les valeurs insérées ; combinée à `INSERT OR REPLACE`, une ligne forgée peut remplacer un produit existant par des données choisies par l’attaquant.
- **Correctif :** utiliser une requête paramétrée avec des paramètres `?` pour les valeurs `reference`, `libelle`, `prix` et `maj`. Ne jamais incorporer les champs CSV directement dans le texte SQL.

## Limites

Cette revue porte sur le fichier indiqué et les flux explicitement visibles dans celui-ci. Elle ne confirme pas les contrôles d’accès au dépôt, du portail fournisseur, du système de fichiers ni des journaux en production.
