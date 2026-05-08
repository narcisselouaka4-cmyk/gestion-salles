#!/bin/bash
# Script pour lancer l'application avec accès public (ngrok)

cd "$(dirname "$0")"

# Active le venv
source ~/.venv/bin/activate

# Vérifie si Streamlit tourne déjà
if ! curl -s http://localhost:8501 > /dev/null; then
    echo "🚀 Lancement de Streamlit..."
    STREAMLIT_TELEMETRY_ENABLED=false STREAMLIT_SERVER_HEADLESS=true nohup streamlit run app.py --server.address=0.0.0.0 --server.port=8501 > streamlit.log 2>&1 &
    sleep 5
else
    echo "✅ Streamlit déjà en cours"
fi

# Lance ngrok en arrière-plan
echo "🌐 Lancement du tunnel ngrok..."
nohup ngrok http 8501 > ngrok.log 2>&1 &
sleep 3

# Récupère l'URL
URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print([t['public_url'] for t in data['tunnels']][0])" 2>/dev/null)

if [ -n "$URL" ]; then
    echo ""
    echo "✅ Application en ligne !"
    echo "🔗 URL publique : $URL"
    echo ""
    echo "📱 Partage cette URL avec qui tu veux"
    echo "⚠️  Cette URL changera au prochain redémarrage de ngrok"
else
    echo "❌ Erreur : impossible de récupérer l'URL ngrok"
    echo "Vérifie que ngrok est bien configuré avec : ngrok config check"
fi
