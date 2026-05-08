#!/bin/bash
# Script d'installation automatique pour Gestion des Salles
# Usage: ./install.sh

set -e  # Stop en cas d'erreur

echo "=========================================="
echo "  Installation Gestion des Salles"
echo "=========================================="
echo ""

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git n'est pas installé${NC}"
    echo "Installation: sudo apt install git"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 n'est pas installé${NC}"
    echo "Installation: sudo apt install python3 python3-venv"
    exit 1
fi

echo -e "${GREEN}✅ Git et Python3 sont installés${NC}"

# Demander le token GitHub (optionnel mais recommandé)
echo ""
echo "📦 Configuration GitHub"
echo "Si vous avez un Personal Access Token, collez-le ci-dessous"
echo "(laissez vide si vous voulez utiliser HTTPS standard)"
read -p "GitHub Token (ou Entrée pour ignorer): " GITHUB_TOKEN

# Cloner le repo
REPO_URL="https://github.com/narcisselouaka4-cmyk/gestion-salles.git"
if [ -n "$GITHUB_TOKEN" ]; then
    REPO_URL="https://${GITHUB_TOKEN}@github.com/narcisselouaka4-cmyk/gestion-salles.git"
fi

if [ -d "gestion-salles" ]; then
    echo -e "${YELLOW}⚠️  Le dossier gestion-salles existe déjà${NC}"
    read -p "Voulez-vous le mettre à jour? (o/n): " UPDATE
    if [ "$UPDATE" = "o" ] || [ "$UPDATE" = "O" ]; then
        cd gestion-salles
        git pull
        cd ..
    fi
else
    echo ""
    echo "📥 Clonage du repository..."
    git clone "$REPO_URL"
fi

cd gestion-salles

# Créer l'environnement virtuel
echo ""
echo "🐍 Création de l'environnement virtuel..."
if [ -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel déjà existant${NC}"
else
    python3 -m venv .venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# Activer l'environnement
echo ""
echo "⚡ Activation de l'environnement..."
source .venv/bin/activate

# Installer les dépendances
echo ""
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dépendances installées${NC}"

# Configuration du fichier credentials.json
echo ""
echo "=========================================="
echo "  Configuration Google Sheets"
echo "=========================================="
echo ""
echo "Pour que l'application fonctionne, vous devez:"
echo "1. Télécharger le fichier credentials.json depuis Google Cloud Console"
echo "2. Le placer dans ce dossier (gestion-salles/)"
echo ""
echo "Le fichier doit contenir les clés d'accès au compte de service."
echo ""

if [ -f "credentials.json" ]; then
    echo -e "${GREEN}✅ credentials.json déjà présent${NC}"
else
    echo -e "${YELLOW}⚠️  credentials.json non trouvé${NC}"
    echo ""
    echo "Option 1: Copiez votre fichier credentials.json existant ici"
    echo "Option 2: Créez un nouveau fichier sur Google Cloud Console:"
    echo "  - https://console.cloud.google.com/iam-admin/serviceaccounts"
    echo "  - Sélectionnez 'gestion-salles-app' → Clés → Ajouter une clé → JSON"
    echo ""
    read -p "Appuyez sur Entrée quand vous avez placé le fichier credentials.json..."

    if [ -f "credentials.json" ]; then
        echo -e "${GREEN}✅ credentials.json trouvé !${NC}"
    else
        echo -e "${YELLOW}⚠️  credentials.json toujours absent. L'app fonctionnera en mode local uniquement.${NC}"
    fi
fi

# Créer .streamlit/secrets.toml si besoin
if [ ! -d ".streamlit" ]; then
    mkdir -p .streamlit
fi

if [ ! -f ".streamlit/secrets.toml" ] && [ -f "credentials.json" ]; then
    echo ""
    echo "🔧 Création du fichier secrets.toml..."

    # Extraire les valeurs de credentials.json
    CLIENT_EMAIL=$(python3 -c "import json; print(json.load(open('credentials.json'))['client_email'])" 2>/dev/null || echo "")
    PROJECT_ID=$(python3 -c "import json; print(json.load(open('credentials.json'))['project_id'])" 2>/dev/null || echo "gestion-salles-app")

    cat > .streamlit/secrets.toml << EOF
[app_config]
google_sheet_id = "1y6TKJvafvteEJlJEsU_yjKbORRoSePx1TiL6-Ser6k8"

# Note: Pour Streamlit Cloud, copiez le contenu complet de credentials.json
# dans la section Secrets du dashboard
EOF
    echo -e "${GREEN}✅ Fichier .streamlit/secrets.toml créé${NC}"
fi

# Instructions finales
echo ""
echo "=========================================="
echo -e "${GREEN}  ✅ Installation terminée !${NC}"
echo "=========================================="
echo ""
echo "Pour lancer l'application:"
echo "  cd gestion-salles"
echo "  source .venv/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "Pour un accès public avec ngrok:"
echo "  ./start_public.sh"
echo ""
echo "L'application en ligne:"
echo "  https://gestion-salles-a9xbacpwjqkkkwzdvs7hn3.streamlit.app/"
echo ""
echo "=========================================="
