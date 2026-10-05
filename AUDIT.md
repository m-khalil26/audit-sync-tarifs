# Audit de sync_tarifs.py
| # | Ligne | Problème | Scénario d’attaque concret | Gravité | Trouvé par |
|1|28 - 29|  Clé API et MDP de passe en clair | Penetration | Grave | L'Humain|
|1|43|  Clé API et MDP de passe en clair | Penetration | Grave | L'Humain|
|1|116|  Débug en affichant les MDP  en clair | Penetration | Grave | L'Humain|
|1|Un peu partout|  SQL problématique sans requete paramtrée | Injection SQL | Grave | L'Humain|
--- Bandit 
Test results:
>> Issue: [B403:blacklist] Consider possible security implications associated with pickle module.
   Severity: Low   Confidence: High
   CWE: CWE-502 (https://cwe.mitre.org/data/definitions/502.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle
   Location: .\sync_tarifs.py:18:0
17      import os
18      import pickle
19      import sqlite3

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'mr_tok_6Qz9Lk2Vb8Xn4Hs7Wd1Rf5Tg3Ym0Pc'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html
   Location: .\sync_tarifs.py:29:12
28      MOT_DE_PASSE = "Riviere2024!Achats"
29      TOKEN_API = "mr_tok_6Qz9Lk2Vb8Xn4Hs7Wd1Rf5Tg3Ym0Pc"
30

--------------------------------------------------
>> Issue: [B323:blacklist] By default, Python will create a secure, verified ssl context for use in such classes as HTTPSConnection. However, it still allows using an insecure context via the _create_unverified_context that  reverts to the previous behavior that does not validate certificates or perform hostname checks.
   Severity: Medium   Confidence: High
   CWE: CWE-295 (https://cwe.mitre.org/data/definitions/295.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b323-unverified-context
   Location: .\sync_tarifs.py:41:15
40          log.info(f"Connexion au portail avec {UTILISATEUR}:{MOT_DE_PASSE} (token {TOKEN_API})")
41          contexte = ssl._create_unverified_context()  # le certificat du portail pose problème
42          requete = urllib.request.Request(url)

--------------------------------------------------
>> Issue: [B310:blacklist] Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
   Severity: Medium   Confidence: High
   CWE: CWE-22 (https://cwe.mitre.org/data/definitions/22.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
   Location: .\sync_tarifs.py:45:9
44          requete.add_header("Authorization", f"Basic {identifiants}")
45          with urllib.request.urlopen(requete, context=contexte) as reponse:
46              with open(destination, "wb") as f:

--------------------------------------------------
>> Issue: [B307:blacklist] Use of possibly insecure function - consider using safer ast.literal_eval.
   Severity: Medium   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b307-eval
   Location: .\sync_tarifs.py:62:17
61          """Le fournisseur donne une formule de prix, par exemple 18.90*0.95."""
62          return round(eval(ligne["formule_prix"]), 2)
63

--------------------------------------------------
>> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection vector through string-based query construction.
   Severity: Medium   Confidence: Low
   CWE: CWE-89 (https://cwe.mitre.org/data/definitions/89.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html
   Location: .\sync_tarifs.py:83:16
82          """Renvoie les produits correspondant à une référence."""
83          requete = f"SELECT reference, libelle, prix_ht FROM produits WHERE reference = '{reference}'"
84          return connexion.execute(requete).fetchall()

--------------------------------------------------
>> Issue: [B605:start_process_with_a_shell] Starting a process with a shell, possible injection detected, security issue.
   Severity: High   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/plugins/b605_start_process_with_a_shell.html
   Location: .\sync_tarifs.py:91:4
90          nom = os.path.basename(fichier)
91          os.system(f"tar czf archives/{nom}.tar.gz {fichier}")
92

--------------------------------------------------
>> Issue: [B301:blacklist] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possiblesecurity issue.
   Severity: Medium   Confidence: High
   CWE: CWE-502 (https://cwe.mitre.org/data/definitions/502.html)
   More Info: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle
   Location: .\sync_tarifs.py:97:19
96              with open(CACHE, "rb") as f:
97                  return pickle.load(f)
98          return {}
---IA--

| # | Sévérité | Fichier | Lignes | Vulnérabilité | Confiance |
|---|----------|---------|-------|---------------|------------|
| 1 | 🔴 CRITICAL | `sync_tarifs.py` | 62 | Exécution de code Python depuis la formule de prix avec `eval()` | 10/10 |
| 2 | 🟠 HIGH | `sync_tarifs.py` | 41, 43–45 | Validation TLS désactivée lors de l’envoi d’identifiants Basic | 9/10 |
| 3 | 🟠 HIGH | `sync_tarifs.py` | 27–29, 40, 116 | Secrets codés en dur, journalisés et affichés en mode debug | 9/10 |
| 4 | 🟡 MEDIUM | `sync_tarifs.py` | 72–73 | Injection SQL via les champs CSV interpolés | 9/10 |