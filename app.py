#!/usr/bin/env python3
"""
Application Streamlit pour la vérification de disponibilité des salles.
"""

import streamlit as st
from datetime import datetime, time
import os

# Charger les variables d'environnement locales (optionnel)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv n'est pas installé, on continue sans

from checker import SalleChecker

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Salles",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Moderne & Professionnel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Moderne */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 20px;
        text-align: center;
        margin: -3rem -1rem 2rem -1rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    /* Cards Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    /* Résultats Modernes */
    .result-libre {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3);
        text-align: center;
        animation: fadeIn 0.4s ease-out;
    }
    
    .result-libre h3 {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .result-occupe {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
        color: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(244, 63, 94, 0.3);
        text-align: center;
        animation: fadeIn 0.4s ease-out;
    }
    
    .result-occupe h3 {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    /* Cartes d'occupation Modernes */
    .occupation-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
        transition: all 0.2s ease;
        animation: fadeIn 0.4s ease-out;
    }
    
    .occupation-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .time-display {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .occupant-name {
        font-size: 1.1rem;
        color: #1f2937;
        margin-top: 0.75rem;
        font-weight: 500;
    }
    
    .activity-name {
        font-size: 0.95rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Footer moderne */
    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding: 1.5rem;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Détails réservation */
    .reservation-details {
        margin-top: 1rem;
        padding: 0.75rem;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .detail-item {
        margin: 0.3rem 0;
    }
    
    .detail-missing {
        color: #d97706;
    }
</style>
""", unsafe_allow_html=True)


def format_date_fr(d):
    """Formate une date en français."""
    mois_fr = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "août",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }
    jours_fr = {
        "Monday": "lundi", "Tuesday": "mardi", "Wednesday": "mercredi",
        "Thursday": "jeudi", "Friday": "vendredi", "Saturday": "samedi", "Sunday": "dimanche"
    }
    jour = jours_fr.get(d.strftime("%A"), d.strftime("%A"))
    return f"{jour} {d.day} {mois_fr[d.month]}"


def format_reservation_details(occ):
    """Formate les détails d'une réservation avec les infos financières."""
    details = []
    
    # Accompte
    accompte = occ.get('accompte', 'Non renseigné')
    if accompte == 'Non renseigné':
        details.append('<div class="detail-item">💰 <strong>Accompte:</strong> <span style="color: #dc2626;">Non renseigné</span></div>')
    else:
        details.append(f'<div class="detail-item">💰 <strong>Accompte:</strong> {accompte}€</div>')
    
    # Reste à payer
    reste = occ.get('reste_a_payer', 'Non renseigné')
    if reste == 'Non renseigné':
        details.append('<div class="detail-item">💳 <strong>Reste à payer:</strong> <span style="color: #dc2626;">Non renseigné</span></div>')
    else:
        details.append(f'<div class="detail-item">💳 <strong>Reste à payer:</strong> {reste}€</div>')
    
    # Prix de location
    prix = occ.get('prix_location', 'Non renseigné')
    if prix == 'Non renseigné':
        details.append('<div class="detail-item">💵 <strong>Prix de location:</strong> <span style="color: #dc2626;">Non renseigné</span></div>')
    else:
        details.append(f'<div class="detail-item">💵 <strong>Prix de location:</strong> {prix}€</div>')
    
    # Caution ménage
    caution = occ.get('caution_menage', 'Non renseigné')
    if caution == 'Non renseigné':
        details.append('<div class="detail-item">🧹 <strong>Chèque caution ménage:</strong> <span style="color: #dc2626;">Non renseigné</span></div>')
    else:
        details.append(f'<div class="detail-item">🧹 <strong>Chèque caution ménage:</strong> {caution}</div>')
    
    # Salle d'occupation
    salle_occ = occ.get('salle_occupation', 'Non renseigné')
    if salle_occ == 'Non renseigné':
        details.append('<div class="detail-item">🏠 <strong>Salle d\'occupation:</strong> <span style="color: #dc2626;">Non renseignée</span></div>')
    else:
        details.append(f'<div class="detail-item">🏠 <strong>Salle d\'occupation:</strong> {salle_occ}</div>')
    
    return ''.join(details)


def main():
    # Header Moderne avec Gradient
    st.markdown('''
    <div class="main-header">
        <h1>🏢 Gestion des Salles</h1>
        <div class="sub-header">CFPDC — Centre de Formation Pédagogique des Disciples du Christ</div>
    </div>
    ''', unsafe_allow_html=True)

    # Déterminer le chemin vers les fichiers de salles
    script_dir = os.path.dirname(os.path.abspath(__file__))
    salles_dir = os.path.join(script_dir, "salles")

    # ID du Google Sheet - doit être configuré via variables d'environnement ou secrets
    GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
    if not GOOGLE_SHEET_ID:
        try:
            GOOGLE_SHEET_ID = st.secrets.get("app_config", {}).get("google_sheet_id", "")
        except Exception:
            GOOGLE_SHEET_ID = ""

    if not os.path.exists(salles_dir):
        st.error("❌ Dossier 'salles/' introuvable. Vérifiez l'installation.")
        return

    # Formulaire dans une card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        salle = st.selectbox(
            "🏠 **Salle**",
            options=["Salle principale", "Salle du fond", "Salle du milieu"],
            index=0
        )

    with col2:
        date_input = st.date_input(
            "📅 **Date**",
            value=datetime.now().date(),
            min_value=datetime(2020, 1, 1).date(),
            max_value=datetime(2030, 12, 31).date()
        )

    sans_heure = st.checkbox("🕐 Voir toutes les occupations du jour", value=False)

    heure = None
    if not sans_heure:
        heure = st.time_input(
            "⏰ **Heure**",
            value=datetime.now().time().replace(minute=0, second=0, microsecond=0)
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bouton stylé
    verify_clicked = st.button("🔍 Vérifier la disponibilité", use_container_width=True, type="primary")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Zone de résultat
    if verify_clicked:
        with st.spinner("Analyse en cours..."):
            try:
                checker = SalleChecker(salles_dir, GOOGLE_SHEET_ID)

                if sans_heure:
                    result = checker.get_all_occupations(salle.lower(), date_input)
                    occupations = result["occupations"]

                    if "error" in result:
                        st.warning(f"⚠️ Connexion Google Sheets impossible. Les réservations ponctuelles ne sont pas affichées.")

                    if not occupations:
                        st.markdown(f'''
                        <div class="result-libre">
                            <h3>✅ La {salle.lower()} est libre</h3>
                            <p style="font-size: 1.1rem; margin-top: 1rem;">
                                Le <strong>{format_date_fr(result["date"])}</strong><br>
                                <span style="font-size: 0.95rem; opacity: 0.9;">Aucune occupation prévue ce jour</span>
                            </p>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div class="result-occupe">
                            <h3>🔴 La {salle.lower()} a des occupations</h3>
                            <p style="font-size: 1.1rem; margin-top: 1rem;">
                                Le <strong>{format_date_fr(result["date"])}</strong>
                            </p>
                            <p style="font-size: 1.1rem; font-weight: bold;">{len(occupations)} occupation(s) ce jour</p>
                        </div>
                        ''', unsafe_allow_html=True)

                        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
                        st.markdown("### 📋 Créneaux occupés")

                        for occ in occupations:
                            horaire_display = occ["horaire"]
                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""
                            
                            # Récupérer les détails de réservation si disponibles
                            details_html = ""
                            if occ.get('source') == 'réservation':
                                details_html = f'<div class="reservation-details">{format_reservation_details(occ)}</div>'

                            warning = ""
                            if "warning" in occ:
                                warning = f'<div style="background: rgba(251, 191, 36, 0.2); border-left: 3px solid #f59e0b; padding: 0.5rem; margin-top: 0.75rem; border-radius: 4px; font-size: 0.85rem; color: #d97706;">⚠️ {occ["warning"]}</div>'

                            st.markdown(f'''
                            <div class="occupation-card">
                                <div class="time-display">🕐 {horaire_display}</div>
                                <div class="occupant-name">👤 <strong>{occupant}</strong></div>
                                {f'<div class="activity-name">📝 {activite}</div>' if activite else ''}
                                {details_html}
                                {warning}
                            </div>
                            ''', unsafe_allow_html=True)

                else:
                    result = checker.check_availability(salle.lower(), date_input, heure)

                    if "error" in result:
                        st.warning(f"⚠️ Connexion Google Sheets impossible. Les réservations ponctuelles ne sont pas affichées.")

                    if result["libre"]:
                        st.markdown(f'''
                        <div class="result-libre">
                            <h3>✅ La {salle.lower()} est libre</h3>
                            <p style="font-size: 1.1rem; margin-top: 1rem;">
                                Le <strong>{format_date_fr(result["date"])}</strong> à <strong>{result["heure"].strftime("%Hh%M")}</strong>
                            </p>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        occupations = result["occupations"]

                        st.markdown(f'''
                        <div class="result-occupe">
                            <h3>🔴 La {salle.lower()} est occupée</h3>
                            <p style="font-size: 1.1rem; margin-top: 1rem;">
                                Le <strong>{format_date_fr(result["date"])}</strong> à <strong>{result["heure"].strftime("%Hh%M")}</strong>
                            </p>
                            <p style="font-size: 1.1rem; font-weight: bold;">{len(occupations)} occupation(s) trouvée(s)</p>
                        </div>
                        ''', unsafe_allow_html=True)

                        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
                        st.markdown("### 📋 Détails des occupations")

                        for occ in occupations:
                            horaire_display = occ["horaire"]
                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""
                            
                            # Récupérer les détails de réservation si disponibles
                            details_html = ""
                            if occ.get('source') == 'réservation':
                                details_html = f'<div class="reservation-details">{format_reservation_details(occ)}</div>'

                            warning = ""
                            if "warning" in occ:
                                warning = f'<div style="background: rgba(251, 191, 36, 0.2); border-left: 3px solid #f59e0b; padding: 0.5rem; margin-top: 0.75rem; border-radius: 4px; font-size: 0.85rem; color: #d97706;">⚠️ {occ["warning"]}</div>'

                            st.markdown(f'''
                            <div class="occupation-card">
                                <div class="time-display">🕐 {horaire_display}</div>
                                <div class="occupant-name">👤 Par : <strong>{occupant}</strong></div>
                                {f'<div class="activity-name">📝 {activite}</div>' if activite else ''}
                                {details_html}
                                {warning}
                            </div>
                            ''', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Erreur lors de la vérification : {str(e)}")
                st.info("Vérifiez que les fichiers Excel sont présents dans le dossier 'salles/'")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="footer">'
        '<div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🏢</div>'
        '<strong>CFPDC</strong> — Gestion des Salles<br>'
        '<span style="font-size: 0.75rem; opacity: 0.7;">© 2024 — Centre de Formation et de Prière</span>'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
