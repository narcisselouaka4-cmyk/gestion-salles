# Déploiement sur Render.com

## Étape 1 : Connecter GitHub à Render

1. Va sur https://dashboard.render.com
2. Connecte-toi avec ton email : **narcisse.louaka4@gmail.com**
3. Clique sur "New Web Service"
4. Connecte ton compte GitHub : **narcisselouaka4-cmyk**
5. Sélectionne le repo : **gestion-salles**

## Étape 2 : Configuration Render

Render va détecter automatiquement le `render.yaml`. Vérifie ces paramètres :

| Paramètre | Valeur |
|-----------|--------|
| Name | `gestion-salles` (ou ce que tu veux) |
| Region | `Frankfurt (EU)` (le plus proche) |
| Branch | `main` |
| Runtime | `Python` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python -m streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true` |
| Plan | `Free` |

## Étape 3 : Variables d'environnement (CRUCIAL)

Dans le dashboard Render, va dans **Settings > Environment Variables** et ajoute :

```
GOOGLE_SHEET_ID=1y6TKJvafvteEJlJEsU_yjKbORRoSePx1TiL6-Ser6k8
GOOGLE_CREDENTIALS_TYPE=service_account
GOOGLE_CREDENTIALS_PROJECT_ID=gestion-salles-app
GOOGLE_CREDENTIALS_PRIVATE_KEY_ID=9756130a723707ee5407c2ef4b5d77e86d1c8bdf
GOOGLE_CREDENTIALS_CLIENT_EMAIL=cfpdc-nl@gestion-salles-app.iam.gserviceaccount.com
GOOGLE_CREDENTIALS_CLIENT_ID=116713971986219741127
```

**⚠️ IMPORTANT** : Pour `GOOGLE_CREDENTIALS_PRIVATE_KEY`, il faut la clé complète sur UNE SEULE LIGNE avec `\n` pour les retours à la ligne :

```
GOOGLE_CREDENTIALS_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5...\n...\n-----END PRIVATE KEY-----
```

## Étape 4 : Fichiers Excel (optionnel)

Pour que les plannings fixes fonctionnent, Render doit avoir les fichiers Excel. 
Deux options :

### Option A : Inclure les fichiers dans Git
```bash
git add salles/*.xlsx
git commit -m "Ajout des fichiers Excel"
git push
```

### Option B : Uploader sur Google Sheets (recommandé)
Migre les données des fichiers Excel vers des onglets dans ton Google Sheet existant.

## Étape 5 : Déployer !

Clique sur **"Create Web Service"**

Render va :
1. Cloner ton repo
2. Installer les dépendances
3. Déployer l'application
4. Te donner une URL fixe : `https://gestion-salles-xxx.onrender.com`

## Commandes utiles Render CLI (optionnel)

Si tu veux utiliser le CLI Render :

```bash
# Installer Render CLI
curl https://render.com/install.sh | bash

# Se connecter
render login

# Déployer
render deploy
```

## Troubleshooting

### "Connexion Google Sheets impossible"
→ Vérifie que `GOOGLE_CREDENTIALS_PRIVATE_KEY` est bien sur une ligne avec `\n`

### "Fichiers Excel non trouvés"
→ Vérifie que le dossier `salles/` est bien dans Git : `git add salles/ && git commit && git push`

### L'app démarre mais affiche "OCCUPÉ" partout
→ C'est normal si la connexion Google Sheets échoue (sécurité). Vérifie les variables d'environnement.

## URL Finale

Une fois déployée, ton application sera accessible à :
**`https://gestion-salles-XXX.onrender.com`** (URL fixe à vie !)

---

Tu veux que je te prépare la valeur de `GOOGLE_CREDENTIALS_PRIVATE_KEY` correctement formatée ?
