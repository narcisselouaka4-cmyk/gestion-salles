#!/usr/bin/env python3
"""
Application Streamlit pour la vérification de disponibilité des salles.
Accessible depuis tous les appareils du réseau local.
"""

import streamlit as st
from datetime import datetime, time
import os

from checker import SalleChecker

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Salles",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS élégant pour un site chrétien professionnel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

    /* Variables de couleur */
    :root {
        --primary-gold: #C9A227;
        --deep-blue: #1e3a5f;
        --warm-cream: #fefcf8;
        --soft-gray: #6b7280;
        --success-green: #059669;
        --error-red: #dc2626;
    }

    /* Style global */
    .stApp {
        background: linear-gradient(135deg, #fefcf8 0%, #f5f1eb 100%);
        font-family: 'Lato', sans-serif;
    }

    /* Header élégant */
    .main-header {
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
    }

    .sub-header {
        text-align: center;
        font-family: 'Lato', sans-serif;
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2.5rem;
        font-weight: 300;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Séparateur décoratif */
    .divider {
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #C9A227, #d4af37);
        margin: 0 auto 2rem auto;
        border-radius: 2px;
    }

    /* Cards de résultat */
    .result-libre {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1px solid #6ee7b7;
        border-left: 4px solid #059669;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .result-libre:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .result-occupe {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1px solid #fca5a5;
        border-left: 4px solid #dc2626;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Carte d'occupation */
    .occupation-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }

    .occupation-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #C9A227;
    }

    /* Affichage horaire */
    .time-display {
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }

    /* Nom de l'occupant */
    .occupant-name {
        font-size: 1.05rem;
        color: #374151;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* Activité */
    .activity-name {
        font-size: 0.95rem;
        color: #6b7280;
        font-style: italic;
        margin-top: 0.25rem;
    }

    /* Footer élégant */
    .footer-text {
        text-align: center;
        color: #9ca3af;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
    }

    /* Sélecteurs stylisés */
    div[data-baseweb="select"] {
        border-radius: 8px !important;
    }

    /* Date picker stylisé */
    div[data-baseweb="datepicker"] {
        border-radius: 8px !important;
    }

    /* Bouton primaire personnalisé */
    .stButton>button {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 6px -1px rgba(30, 58, 95, 0.2) !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(30, 58, 95, 0.3) !important;
    }

    /* Checkbox stylisée */
    .stCheckbox label {
        font-size: 0.95rem;
        color: #4b5563;
    }

    /* Spinner personnalisé */
    .stSpinner > div {
        border-top-color: #C9A227 !important;
    }

    /* Alertes */
    .stAlert {
        border-radius: 10px !important;
    }

    /* Séparateur */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
        margin: 2rem 0;
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


def main():
    # En-tête élégant avec symbole chrétien
    st.markdown('<div class="main-header">✝️ Gestion des Salles</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Centre de Formation et de Perfectionnement des Dirigeants Chrétiens</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Déterminer le chemin vers les fichiers de salles
    # En priorité : dossier 'salles/' à côté du script, sinon le dossier courant
    script_dir = os.path.dirname(os.path.abspath(__file__))
    salles_dir = os.path.join(script_dir, "salles")

    # ID du Google Sheet pour les réservations
    # Essayer de lire depuis env vars (Render) puis Streamlit secrets (Streamlit Cloud)
    GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
    if not GOOGLE_SHEET_ID:
        try:
            GOOGLE_SHEET_ID = st.secrets.get("app_config", {}).get("google_sheet_id", "1y6TKJvafvteEJlJEsU_yjKbORRoSePx1TiL6-Ser6k8")
        except Exception:
            GOOGLE_SHEET_ID = "1y6TKJvafvteEJlJEsU_yjKbORRoSePx1TiL6-Ser6k8"

    if not os.path.exists(salles_dir):
        st.error(f"❌ Dossier 'salles/' introuvable. Vérifiez l'installation.")
        return

    # Formulaire
    col1, col2 = st.columns(2)

    with col1:
        salle = st.selectbox(
            "Salle",
            options=["Salle principale", "Salle du fond", "Salle du milieu"],
            index=0
        )

    with col2:
        date_input = st.date_input(
            "Date",
            value=datetime.now().date(),
            min_value=datetime(2020, 1, 1).date(),
            max_value=datetime(2030, 12, 31).date()
        )

    # Option sans heure précise
    sans_heure = st.checkbox("🕐 Sans heure précise (voir toutes les occupations du jour)", value=False)

    heure = None
    if not sans_heure:
        heure = st.time_input(
            "Heure",
            value=datetime.now().time().replace(minute=0, second=0, microsecond=0)
        )

    # Bouton de vérification (pleine largeur)
    st.markdown("<br>", unsafe_allow_html=True)
    verify_clicked = st.button("🔍 Vérifier la disponibilité", use_container_width=True, type="primary")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Zone de résultat
    if verify_clicked:
        with st.spinner("Analyse en cours..."):
            try:
                # Utiliser Google Sheets pour les réservations (temps réel)
                checker = SalleChecker(salles_dir, GOOGLE_SHEET_ID)

                if sans_heure:
                    # Mode : voir toutes les occupations du jour
                    result = checker.get_all_occupations(salle.lower(), date_input)
                    occupations = result["occupations"]

                    # Afficher un avertissement si Google Sheets est inaccessible
                    if "error" in result:
                        st.warning(f"⚠️ Connexion Google Sheets impossible : {result['error']}. Les réservations ponctuelles ne sont pas affichées.")

                    if not occupations:
                        st.markdown(f'''
                        <div class="result-libre">
                            <h3>✅ La {salle.lower()} est libre</h3>
                            <p style="font-size: 1.1rem; margin-top: 1rem;">
                                Le <strong>{format_date_fr(result["date"])}</strong><br>
                                <span style="font-size: 0.95rem; color: #155724;">Aucune occupation prévue ce jour</span>
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
                            <p style="color: #721c24;">{len(occupations)} occupation(s) ce jour</p>
                        </div>
                        ''', unsafe_allow_html=True)

                        # Afficher les occupations
                        st.markdown("### Créneaux occupés")

                        for occ in occupations:
                            # Affiche l'horaire tel quel depuis le fichier
                            horaire_display = occ["horaire"]

                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""

                            warning = ""
                            if "warning" in occ:
                                warning = f'<p style="color: #856404; font-size: 0.85rem;">⚠️ {occ["warning"]}</p>'

                            st.markdown(f'''
                            <div class="occupation-card">
                                <div class="time-display">🕐 {horaire_display}</div>
                                <div class="occupant-name">👤 <strong>{occupant}</strong></div>
                                {f'<div class="activity-name">📝 {activite}</div>' if activite else ''}
                                {warning}
                            </div>
                            ''', unsafe_allow_html=True)

                else:
                    # Mode : vérifier à une heure précise
                    result = checker.check_availability(salle.lower(), date_input, heure)

                    # Afficher un avertissement si Google Sheets est inaccessible
                    if "error" in result:
                        st.warning(f"⚠️ Connexion Google Sheets impossible : {result['error']}. Les réservations ponctuelles ne sont pas affichées.")

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
                        occupation_count = len(occupations)

                        st.markdown(f'''
                        <div class="result-occupe">
                            <h3>🔴 La {salle.lower()} est occupée</h3>
                            <p style="font-size: 1.1rem; margin-top: 1rem;">
                                Le <strong>{format_date_fr(result["date"])}</strong> à <strong>{result["heure"].strftime("%Hh%M")}</strong>
                            </p>
                            <p style="color: #721c24;">{occupation_count} occupation(s) trouvée(s)</p>
                        </div>
                        ''', unsafe_allow_html=True)

                        # Afficher les occupations
                        st.markdown("### Détails des occupations")

                        for occ in occupations:
                            # Affiche l'horaire tel quel depuis le fichier
                            horaire_display = occ["horaire"]

                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""

                            warning = ""
                            if "warning" in occ:
                                warning = f'<p style="color: #856404; font-size: 0.85rem;">⚠️ {occ["warning"]}</p>'

                            st.markdown(f'''
                            <div class="occupation-card">
                                <div class="time-display">{horaire_display}</div>
                                <div class="occupant-name">👤 Par : <strong>{occupant}</strong></div>
                                {f'<div class="activity-name">📝 {activite}</div>' if activite else ''}
                                {warning}
                            </div>
                            ''', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Erreur lors de la vérification : {str(e)}")
                st.info("Veuillez vérifier que les fichiers Excel sont présents dans le dossier 'salles/'")

    # Footer élégant
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div class="footer-text">'
        '🕊️ « Tout ce que vous faites, faites-le avec amour » — 1 Corinthiens 16:14<br>'
        'Application de gestion des salles • © CFPDC'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
