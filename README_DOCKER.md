# Gestion des Salles - Docker

Application Streamlit de gestion de salles, packagée en Docker pour un déploiement facile.

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) installé
- [Docker Compose](https://docs.docker.com/compose/install/) (optionnel mais recommandé)

## Installation rapide

### Méthode 1 : Avec Docker Compose (recommandé)

1. Téléchargez les fichiers :
   - `docker-compose.yml`
   - `Dockerfile`
   - `app.py`
   - `checker.py`
   - `requirements.txt`
   - Dossier `salles/` (avec les fichiers Excel)

2. Lancez l'application :
   ```bash
   docker-compose up --build
   ```

3. Ouvrez votre navigateur à : http://localhost:8501

### Méthode 2 : Sans Docker Compose

1. Construisez l'image :
   ```bash
   docker build -t gestion-salles .
   ```

2. Lancez le conteneur :
   ```bash
   docker run -p 8501:8501 -v $(pwd)/salles:/app/salles gestion-salles
   ```

3. Ouvrez votre navigateur à : http://localhost:8501

## Fonctionnalités

- ✅ **Planning fixe** : Lecture des fichiers Excel locaux (toujours fonctionnel)
- ⚠️ **Google Sheets** : Nécessite la configuration des credentials (voir ci-dessous)

## Configuration Google Sheets (optionnel)

Pour activer les réservations ponctuelles depuis Google Sheets :

### Méthode A : Fichier credentials.json

1. Placez votre fichier `credentials.json` à la racine du projet
2. Lancez avec :
   ```bash
   docker-compose up
   ```

### Méthode B : Variables d'environnement

1. Créez un fichier `.env` :
   ```
   GOOGLE_SHEET_ID=1y6TKJvafvteEJlJEsU_yjKbORRoSePx1TiL6-Ser6k8
   GOOGLE_CREDENTIALS_TYPE=service_account
   GOOGLE_CREDENTIALS_PROJECT_ID=gestion-salles-app
   GOOGLE_CREDENTIALS_PRIVATE_KEY_ID=xxx
   GOOGLE_CREDENTIALS_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nxxx\n-----END PRIVATE KEY-----"
   GOOGLE_CREDENTIALS_CLIENT_EMAIL=cfpdc-nl@gestion-salles-app.iam.gserviceaccount.com
   GOOGLE_CREDENTIALS_CLIENT_ID=xxx
   ```

2. Modifiez le `docker-compose.yml` pour charger le fichier .env :
   ```yaml
   env_file:
     - .env
   ```

## Partager l'application

### Option 1 : Partager les fichiers sources

Envoyez par email/drive :
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
- Dossier `salles/` (les fichiers Excel)

L'autre personne fait juste `docker-compose up --build`.

### Option 2 : Exporter l'image Docker

1. Sauvegardez l'image :
   ```bash
   docker save gestion-salles:latest | gzip > gestion-salles.tar.gz
   ```

2. Envoyez le fichier `gestion-salles.tar.gz`

3. L'autre personne charge l'image :
   ```bash
   gunzip -c gestion-salles.tar.gz | docker load
   docker run -p 8501:8501 -v $(pwd)/salles:/app/salles gestion-salles
   ```

**Note** : Pour l'Option 2, il faut aussi partager le dossier `salles/` séparément.

## Arrêter l'application

```bash
docker-compose down
```

Ou si lancé sans Docker Compose :
```bash
docker stop $(docker ps -q --filter ancestor=gestion-salles)
```

## Dépannage

| Problème | Solution |
|----------|----------|
| "Port déjà utilisé" | Changez le port : `docker run -p 8502:8501 ...` |
| "Salles non trouvées" | Vérifiez que le dossier `salles/` est bien monté avec `-v` |
| Erreur Google Sheets | Normal si pas de credentials - les réservations fixes fonctionnent quand même |

## Support

Problèmes ? Vérifiez les logs :
```bash
docker-compose logs
```
