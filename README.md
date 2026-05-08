# Gestion des Salles

Application de gestion de réservation de salles pour le CFPDC (Centre de Formation et de Perfectionnement des Dirigeants Chrétiens).

## Fonctionnalités

- Consultation de la disponibilité des salles en temps réel
- Planning fixe depuis fichiers Excel locaux
- Réservations ponctuelles via Google Sheets (optionnel)
- Interface responsive (mobile et desktop)
- Support mode sombre/clair

## Prérequis

- Python 3.9+
- Docker (optionnel)
- Google Service Account (optionnel, pour Google Sheets)

## Installation

### Méthode 1 : Installation locale

```bash
# Cloner le repository
git clone https://github.com/narcisselouaka4-cmyk/gestion-salles.git
cd gestion-salles

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement (optionnel pour Google Sheets)
cp .env.example .env
# Éditez .env avec vos valeurs

# Lancer l'application
streamlit run app.py
```

L'application sera accessible sur http://localhost:8501

### Méthode 2 : Docker

```bash
# Construire et lancer
docker-compose up --build
```

L'application sera accessible sur http://localhost:8501

## Configuration Google Sheets (Optionnel)

Pour activer la synchronisation avec Google Sheets :

1. Créez un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activez l'API Google Sheets
3. Créez un compte de service et téléchargez le fichier `credentials.json`
4. Partagez votre Google Sheet avec l'email du compte de service
5. Configurez les variables d'environnement :
   - `GOOGLE_SHEET_ID` : L'ID de votre Google Sheet
   - Les variables `GOOGLE_CREDENTIALS_*` depuis le fichier credentials.json

## Déploiement

### Streamlit Cloud

1. Créez un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
2. Connectez votre repository GitHub
3. Configurez les secrets dans l'interface (Settings > Secrets) :
   ```toml
   [app_config]
   google_sheet_id = "votre_sheet_id"

   [google_credentials]
   type = "service_account"
   project_id = "votre_project_id"
   # ... autres champs du fichier credentials.json
   ```

### Render

1. Créez un compte sur [Render](https://render.com)
2. Déployez via le Blueprint (`render.yaml`)
3. Configurez les variables d'environnement dans le dashboard

## Structure du projet

```
gestion-salles/
├── app.py                 # Application Streamlit principale
├── checker.py            # Logique métier de vérification
├── requirements.txt      # Dépendances Python
├── salles/              # Fichiers Excel de planning
│   ├── SALLE_PRINCIPALE.xlsx
│   ├── SALLE_DU_FOND.xlsx
│   └── Salle_du_Milieu.xlsx
├── Dockerfile           # Configuration Docker
├── docker-compose.yml   # Configuration Docker Compose
├── render.yaml          # Configuration Render
└── .env.example         # Exemple de configuration
```

## Sécurité

⚠️ **Ne jamais committer de fichiers sensibles :**
- `credentials.json` (compte Google)
- `.streamlit/secrets.toml` (secrets Streamlit)
- `.env` (variables d'environnement)

Ces fichiers sont déjà dans `.gitignore` mais assurez-vous qu'ils ne sont pas dans l'historique Git.

## Contribution

Les contributions sont les bienvenues ! Assurez-vous de :
1. Ne pas inclure de données sensibles dans vos commits
2. Tester vos modifications avant de soumettre une PR

## Licence

Ce projet est privé. Tous droits réservés.
