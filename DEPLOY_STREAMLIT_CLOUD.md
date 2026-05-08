# Déploiement sur Streamlit Community Cloud

Ce guide explique comment déployer l'application sur Streamlit Community Cloud pour avoir une URL permanente et gratuite.

---

## Étape 1 : Créer un compte Streamlit Cloud

1. Va sur [share.streamlit.io](https://share.streamlit.io)
2. Clique sur "Sign up" et crée un compte (tu peux utiliser GitHub)

---

## Étape 2 : Créer un repo GitHub

1. Va sur [github.com](https://github.com) et crée un nouveau repository
   - Nom : `gestion-salles` (ou ce que tu veux)
   - Visibility : **Private** (important pour ne pas exposer tes credentials)
   - Coche "Add a README file"

2. Upload ces fichiers dans le repo :
   - `app.py`
   - `checker.py`
   - `requirements.txt` (je te le crée ci-dessous)
   - `.streamlit/secrets.toml` (pas ce fichier ! on le configurera différemment)

3. Crée un dossier `salles/` et upload les 3 fichiers Excel de salles :
   - `SALLE_PRINCIPALE.xlsx`
   - `SALLE_DU_FOND.xlsx`
   - `Salle_du_Milieu.xlsx`

### Fichier requirements.txt à créer :

```txt
streamlit>=1.28.0
openpyxl>=3.1.0
gspread>=6.0.0
google-auth>=2.0.0
```

---

## Étape 3 : Configurer les Secrets sur Streamlit Cloud

Les secrets (credentials Google) ne doivent **jamais** être dans le code. Streamlit Cloud a une interface sécurisée pour ça.

1. Dans ton repo GitHub, crée un fichier `.streamlit/secrets.toml` (temporaire, local uniquement) :

```toml
[google_credentials]
type = "service_account"
project_id = "gestion-salles-app"
private_key_id = "TON_PRIVATE_KEY_ID"
private_key = """-----BEGIN PRIVATE KEY-----
TON_PRIVATE_KEY_ICI
-----END PRIVATE KEY-----"""
client_email = "salle-app-service@gestion-salles-app.iam.gserviceaccount.com"
client_id = "TON_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/salle-app-service%40gestion-salles-app.iam.gserviceaccount.com"

[app_config]
google_sheet_id = "1y6TKJvafvteEJlJEsU_yjKbORRoSePx1TiL6-Ser6k8"
```

2. Récupère les valeurs depuis ton fichier `credentials.json` :
   - Ouvre `/home/visiteur/projet_salles/credentials.json`
   - Copie chaque champ dans le format ci-dessus
   - **Important** : le `private_key` doit être entre triple guillemets `"""`

3. Une fois le fichier créé, **ne le commit pas sur GitHub** !

4. Sur Streamlit Cloud :
   - Va dans ton app → "Settings" → "Secrets"
   - Copie-colle le contenu de `secrets.toml`
   - Clique sur "Save"

---

## Étape 4 : Déployer l'application

1. Sur [share.streamlit.io](https://share.streamlit.io), clique sur "New app"
2. Sélectionne ton repo GitHub
3. Streamlit détecte automatiquement `app.py`
4. Clique sur "Deploy"

L'application sera construite et déployée. Tu recevras une URL permanente du type :
```
https://gestion-salles-votrenom.streamlit.app
```

---

## Étape 5 : Maintenir à jour

Quand tu modifies le code :
1. Fais un `git push` sur GitHub
2. Streamlit redéploie automatiquement

Quand tu modifies le Google Sheet :
- Les changements sont immédiatement visibles (pas besoin de redéployer)

---

## Problèmes connus

### Le déploiement échoue
- Vérifie que `requirements.txt` contient toutes les dépendances
- Vérifie que les fichiers Excel sont bien uploadés dans `salles/`

### Google Sheets ne fonctionne pas
- Vérifie que les secrets sont bien configurés
- Vérifie que le compte de service a toujours accès au Google Sheet

### L'app est lente au premier chargement
- Normal : Streamlit met l'app en veille après inactivité
- Le premier visiteur la réveille (prend ~10-30 secondes)
