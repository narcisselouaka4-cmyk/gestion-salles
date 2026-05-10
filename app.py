#!/usr/bin/env python3
"""
Application Streamlit pour la vérification de disponibilité des salles.
Version 2.0 - Design System modernisé
"""

import streamlit as st
from datetime import datetime, time
import os
import time as time_module

# Charger les variables d'environnement locales (optionnel)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv n'est pas installé, on continue sans

from checker import SalleChecker

# Configuration de la page - FORCER LE MODE CLAIR
st.set_page_config(
    page_title="Gestion des Salles",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# FORCER LE MODE CLAIR
st.markdown("""
    <script>
        // Forcer le mode clair
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    </script>
""", unsafe_allow_html=True)

# CSS Refonte Complète - Design System Pro
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    /* FORCER LE FOND CLAIR PARTOUT */
    .stApp {
        background-color: #f5f7fb !important;
    }
    
    body, [data-testid="stAppViewContainer"] {
        background-color: #f5f7fb !important;
    }

    /* Header avec gradient moderne */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 2.5rem 1.5rem;
        border-radius: 24px;
        text-align: center;
        margin: -3rem -1rem 2.5rem -1rem;
        box-shadow: 0 20px 40px -12px rgba(99, 102, 241, 0.35);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
    }
    
    .main-header h1 { 
        font-size: 2.75rem; 
        font-weight: 700; 
        margin: 0; 
        letter-spacing: -0.03em;
        position: relative;
    }
    
    .sub-header { 
        color: rgba(255,255,255,0.85); 
        font-size: 1rem; 
        font-weight: 400; 
        margin-top: 0.75rem;
        position: relative;
    }

    /* Cards modernes - Glassmorphism léger */
    .glass-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.02),
            0 2px 4px -1px rgba(0, 0, 0, 0.02),
            0 0 0 1px rgba(0, 0, 0, 0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        box-shadow: 
            0 20px 25px -5px rgba(0, 0, 0, 0.05),
            0 10px 10px -5px rgba(0, 0, 0, 0.02),
            0 0 0 1px rgba(0, 0, 0, 0.02);
        transform: translateY(-2px);
    }

    /* Résultats - Cards vibrantes */
    .result-libre {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 
            0 20px 40px -12px rgba(16, 185, 129, 0.35),
            inset 0 1px 0 rgba(255,255,255,0.2);
        text-align: center;
        animation: slideUpFade 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .result-libre::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    }
    
    .result-libre h3 { 
        font-size: 2rem; 
        font-weight: 700; 
        margin: 0 0 0.75rem 0;
        position: relative;
    }

    .result-occupe {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
        color: white;
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 
            0 20px 40px -12px rgba(244, 63, 94, 0.35),
            inset 0 1px 0 rgba(255,255,255,0.2);
        text-align: center;
        animation: slideUpFade 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .result-occupe::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    }
    
    .result-occupe h3 { 
        font-size: 2rem; 
        font-weight: 700; 
        margin: 0 0 0.75rem 0;
        position: relative;
    }

    /* Carte Occupation - Design épuré */
    .occupation-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 
            0 1px 3px rgba(0,0,0,0.02),
            0 0 0 1px rgba(0,0,0,0.02);
        border-left: 4px solid #6366f1;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .occupation-card:hover {
        transform: translateX(6px);
        box-shadow: 
            0 10px 15px -3px rgba(0,0,0,0.05),
            0 4px 6px -2px rgba(0,0,0,0.025),
            0 0 0 1px rgba(0,0,0,0.02);
    }

    .time-display {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 4px 12px -2px rgba(99, 102, 241, 0.3);
    }

    .occupant-name { 
        font-size: 1.2rem; 
        color: #1e293b; 
        margin-top: 1rem; 
        font-weight: 600;
    }
    
    .activity-name { 
        font-size: 1rem; 
        color: #64748b; 
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* Détails financiers - Section claire */
    .reservation-details {
        margin-top: 1.25rem;
        padding: 1rem 1.25rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        font-size: 0.95rem;
        line-height: 1.8;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    
    .reservation-details strong { 
        color: #1e293b; 
        font-weight: 600;
    }
    
    .reservation-details span {
        color: #6366f1;
        font-weight: 500;
    }

    /* Formulaire d'édition - Section épurée */
    .edit-section {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.75rem;
        margin-top: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    .edit-section h4 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 1.25rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* Footer moderne */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 4rem;
        padding: 2rem;
        border-top: 1px solid #e2e8f0;
    }

    /* Animations */
    @keyframes slideUpFade {
        from { 
            opacity: 0; 
            transform: translateY(20px) scale(0.98); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }
    
    @keyframes slideIn {
        from { 
            opacity: 0; 
            transform: translateX(-10px); 
        }
        to { 
            opacity: 1; 
            transform: translateX(0); 
        }
    }

    /* Streamlit overrides - Inputs modernisés */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="datepicker"] > div {
        background-color: #ffffff !important;
        border-color: #d1d5db !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="input"] > div:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }

    /* Checkbox moderne */
    [data-testid="stCheckbox"] > label {
        background: #f8fafc;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    /* Expander modernisé */
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        background: #ffffff !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
        overflow: hidden;
    }
    
    div[data-testid="stExpanderHeader"] {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        padding: 1rem 1.25rem !important;
        font-weight: 500 !important;
        color: #1e293b !important;
    }
    
    div[data-testid="stExpanderDetails"] {
        background: #ffffff !important;
        padding: 1.25rem !important;
    }

    /* Bouton primaire - Violet moderne */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 30px -5px rgba(99, 102, 241, 0.5) !important;
    }
    
    .stButton > button[kind="primary"]:active {
        transform: translateY(0) !important;
    }

    /* Bouton secondaire */
    .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        border-color: #d1d5db !important;
        transform: translateY(-1px);
    }

    /* Form submit buttons */
    button[type="submit"] {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
    }

    /* Section titre */
    h3 {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Labels des formulaires */
    label {
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }

    /* Messages d'erreur/succès modernisés */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
    }
    
    [data-testid="stAlert"] > div {
        padding: 1rem 1.25rem !important;
    }

    /* Séparateur invisible élégant */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(to right, transparent, #e2e8f0, transparent) !important;
        margin: 2rem 0 !important;
    }

    /* Spinner */
    [data-testid="stSpinner"] > div {
        color: #6366f1 !important;
    }

    /* Caption */
    .stCaption {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }

    /* Espacement amélioré */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
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

    # ID du Google Sheet
    GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
    if not GOOGLE_SHEET_ID:
        try:
            GOOGLE_SHEET_ID = st.secrets.get("app_config", {}).get("google_sheet_id", "")
        except Exception:
            GOOGLE_SHEET_ID = ""

    if not os.path.exists(salles_dir):
        st.error("❌ Dossier 'salles/' introuvable. Vérifiez l'installation.")
        return

    # Initialiser le checker
    checker = SalleChecker(salles_dir, GOOGLE_SHEET_ID)

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

    st.markdown("<hr>", unsafe_allow_html=True)

    # Zone de résultat
    if verify_clicked or 'occupations' in st.session_state:
        
        if verify_clicked:
            # Recharger les données
            with st.spinner("Analyse en cours..."):
                try:
                    if sans_heure:
                        result = checker.get_all_occupations(salle.lower(), date_input)
                    else:
                        result = checker.check_availability(salle.lower(), date_input, heure)
                    
                    st.session_state.occupations = result.get("occupations", [])
                    st.session_state.is_libre = result.get("libre", False)
                    st.session_state.result_date = result.get("date", date_input)
                    st.session_state.result_heure = result.get("heure", heure)
                    st.session_state.salle = salle
                    st.session_state.date_input = date_input
                    
                    if "error" in result:
                        st.warning("⚠️ Connexion Google Sheets impossible. Les réservations ponctuelles ne sont pas affichées.")
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors de la vérification : {str(e)}")
                    st.session_state.occupations = []
        
        # Afficher les résultats
        if 'occupations' in st.session_state:
            occupations = st.session_state.occupations
            is_libre = st.session_state.get("is_libre", False)
            result_date = st.session_state.get("result_date", date_input)
            result_heure = st.session_state.get("result_heure", heure)
            
            if not occupations:
                st.markdown(f'''
                <div class="result-libre">
                    <h3>✅ La {salle.lower()} est libre</h3>
                    <p style="font-size: 1.15rem; margin-top: 1.25rem; opacity: 0.95;">
                        Le <strong>{format_date_fr(result_date)}</strong><br>
                        <span style="font-size: 0.95rem; opacity: 0.85;">Aucune occupation prévue</span>
                    </p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                if is_libre:
                    st.markdown(f'''
                    <div class="result-libre">
                        <h3>✅ La {salle.lower()} est libre</h3>
                        <p style="font-size: 1.15rem; margin-top: 1.25rem; opacity: 0.95;">
                            Le <strong>{format_date_fr(result_date)}</strong> à <strong>{result_heure.strftime("%Hh%M")}</strong>
                        </p>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="result-occupe">
                        <h3>🔴 Occupation trouvée</h3>
                        <p style="font-size: 1.15rem; margin-top: 1.25rem; opacity: 0.95;">
                            {len(occupations)} résultat(s) pour cette recherche
                        </p>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown('<div style="margin-top: 2.5rem;"></div>', unsafe_allow_html=True)
                st.markdown("### 📋 Détails des occupations")

                # Afficher chaque occupation avec formulaire d'édition
                for idx, occ in enumerate(occupations):
                    horaire_display = occ.get("horaire", "Horaire non précisé")
                    occupant = occ.get("occupant", "Non précisé")
                    activite = occ.get("activite", "")
                    
                    # Préparer les infos financières
                    details_items = []

                    accompte_display = occ.get('accompte', '')
                    if accompte_display:
                        details_items.append(f'💰 <strong>Accompte :</strong> <span>{accompte_display}</span>')

                    reste_display = occ.get('reste_a_payer', '')
                    if reste_display:
                        details_items.append(f'💳 <strong>Reste à payer :</strong> <span>{reste_display}</span>')

                    prix_display = occ.get('prix_location', '')
                    if prix_display:
                        details_items.append(f'💵 <strong>Prix location :</strong> <span>{prix_display}</span>')

                    caution_display = occ.get('caution_menage', '')
                    if caution_display:
                        details_items.append(f'🧹 <strong>Caution :</strong> <span>{caution_display}</span>')

                    salle_display = occ.get('salle', '')
                    if salle_display:
                        details_items.append(f'🏠 <strong>Salle :</strong> <span>{salle_display}</span>')

                    details_html = '<br>'.join(details_items) if details_items else ''

                    with st.container():
                        parts = [
                            f'<div class="occupation-card">',
                            f'<div class="time-display">🕐 {horaire_display}</div>',
                            f'<div class="occupant-name">👤 Par : <strong>{occupant}</strong></div>',
                        ]
                        if activite:
                            parts.append(f'<div class="activity-name">📝 {activite}</div>')
                        if details_html:
                            parts.append(f'<div class="reservation-details">{details_html}</div>')
                        parts.append('</div>')
                        st.markdown(''.join(parts), unsafe_allow_html=True)
                        
                        # Formulaire d'édition
                        if occ.get('source') == 'réservation':
                            with st.expander("✏️ Modifier les informations"):
                                st.markdown(f"""
                                <div style="margin-bottom:1.25rem; padding: 0.75rem 1rem; background: #f8fafc; border-radius: 10px;">
                                    <span style="font-size:0.875rem; color:#64748b;">Réservation</span>
                                    <strong style="color:#1e293b; margin-left:0.5rem;">{occupant}</strong>
                                    <span style="font-size:0.8rem; color:#94a3b8; margin-left:0.5rem;">• {horaire_display}</span>
                                </div>
                                """, unsafe_allow_html=True)

                                with st.form(key=f"edit_form_{idx}", border=False):
                                    col1, col2 = st.columns(2)

                                    with col1:
                                        nom_val = occ.get('occupant', '')
                                        new_nom = st.text_input("👤 Nom", value=nom_val)

                                        accompte_val = occ.get('accompte', '')
                                        new_accompte = st.text_input("💰 Accompte (€)", value=accompte_val, placeholder="Ex: 100")

                                        reste_val = occ.get('reste_a_payer', '')
                                        new_reste = st.text_input("💳 Reste à payer (€)", value=reste_val, placeholder="Ex: 550")

                                    with col2:
                                        prix_val = occ.get('prix_location', '')
                                        new_prix = st.text_input("💵 Prix location (€)", value=prix_val, placeholder="Ex: 650")

                                        caution_val = occ.get('caution_menage', '')
                                        new_caution = st.text_input("🧹 Caution", value=caution_val, placeholder="Ex: Oui")

                                        salle_val = occ.get('salle', '')
                                        new_salle = st.text_input("🏠 Salle", value=salle_val, placeholder="Ex: Salle principale")

                                    # Actions
                                    c1, c2, c3 = st.columns([3, 1, 1])
                                    with c1:
                                        submitted = st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True)
                                    with c3:
                                        clear_submitted = st.form_submit_button("🗑️ Effacer", use_container_width=True)

                                    if submitted:
                                        update_data = {}
                                        if new_nom != occupant:
                                            update_data['occupant'] = new_nom if new_nom else "Non renseigné"

                                        update_data['accompte'] = f"{new_accompte}€" if new_accompte and '€' not in new_accompte else (new_accompte if new_accompte else "")
                                        update_data['reste_a_payer'] = f"{new_reste}€" if new_reste and '€' not in new_reste else (new_reste if new_reste else "")
                                        update_data['prix_location'] = f"{new_prix}€" if new_prix and '€' not in new_prix else (new_prix if new_prix else "")
                                        update_data['caution_menage'] = new_caution if new_caution else ""
                                        update_data['salle'] = new_salle if new_salle else ""

                                        if update_data:
                                            success, error = checker.update_reservation_google(
                                                st.session_state.salle.lower(),
                                                st.session_state.date_input,
                                                occupant.strip(),
                                                update_data
                                            )

                                            if success:
                                                st.success("✅ Modifications sauvegardées")
                                                st.session_state.occupations[idx].update(update_data)
                                                st.session_state.last_update = datetime.now()
                                                time_module.sleep(0.5)
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Erreur : {error}")

                                    if clear_submitted:
                                        update_data = {
                                            'accompte': "",
                                            'reste_a_payer': "",
                                            'prix_location': "",
                                            'caution_menage': "",
                                            'salle': ""
                                        }

                                        success, error = checker.update_reservation_google(
                                            st.session_state.salle.lower(),
                                            st.session_state.date_input,
                                            occupant.strip(),
                                            update_data
                                        )

                                        if success:
                                            st.success("✅ Informations effacées")
                                            st.session_state.occupations[idx].update(update_data)
                                            st.session_state.last_update = datetime.now()
                                            time_module.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Erreur : {error}")

    # Auto-refresh
    if 'occupations' in st.session_state and st.session_state.occupations:
        if 'last_update' in st.session_state:
            st.caption(f"🔄 Dernière mise à jour : {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Rafraîchir", key="manual_refresh"):
                st.session_state.last_update = datetime.now()
                st.rerun()
        with col2:
            st.caption("Les données se rafraîchissent automatiquement toutes les 60 secondes")
        
        st.markdown("""
        <script>
            setTimeout(function() {
                window.location.reload();
            }, 60000);
        </script>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div class="footer">'
        '<div style="font-size: 1.5rem; margin-bottom: 0.75rem;">🏢</div>'
        '<strong style="color: #475569;">CFPDC</strong> — Gestion des Salles<br>'
        '<span style="font-size: 0.8rem; opacity: 0.7;">© 2024 — Centre de Formation et de Prière</span>'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
