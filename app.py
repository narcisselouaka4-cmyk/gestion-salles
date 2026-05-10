#!/usr/bin/env python3
"""
Application Streamlit pour la vérification de disponibilité des salles.
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

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Salles",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Refonte Complète
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 20px;
        text-align: center;
        margin: -3rem -1rem 2rem -1rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .main-header h1 { font-size: 2.5rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
    .sub-header { color: rgba(255,255,255,0.9); font-size: 1rem; font-weight: 400; margin-top: 0.5rem; }

    /* Cards */
    .glass-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Résultats */
    .result-libre {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(16,185,129,0.3);
        text-align: center;
        animation: fadeIn 0.4s ease-out;
    }
    .result-libre h3 { font-size: 1.8rem; font-weight: 700; margin: 0 0 0.5rem 0; }

    .result-occupe {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
        color: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(244,63,94,0.3);
        text-align: center;
        animation: fadeIn 0.4s ease-out;
    }
    .result-occupe h3 { font-size: 1.8rem; font-weight: 700; margin: 0 0 0.5rem 0; }

    /* Carte Occupation */
    .occupation-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border-left: 4px solid #667eea;
        transition: all 0.2s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .occupation-card:hover {
        transform: translateX(4px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
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

    .occupant-name { font-size: 1.1rem; color: #1f2937; margin-top: 0.75rem; font-weight: 500; }
    .activity-name { font-size: 0.95rem; color: #6b7280; margin-top: 0.25rem; }

    /* Détails */
    .reservation-details {
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        background: #f8fafc;
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.6;
        color: #475569;
    }
    .reservation-details strong { color: #1e293b; font-weight: 600; }

    /* Formulaire d'édition */
    .edit-section {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .edit-section h4 {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e2e8f0;
    }

    /* Badge discret "non renseigné" */
    .badge-missing {
        display: inline-block;
        background: #f1f5f9;
        color: #64748b;
        font-size: 0.7rem;
        font-weight: 500;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        margin-left: 0.4rem;
        vertical-align: middle;
    }

    /* Boutons */
    .btn-actions {
        display: flex;
        gap: 0.75rem;
        margin-top: 1.5rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding: 1.5rem;
        border-top: 1px solid #e2e8f0;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Streamlit overrides pour inputs */
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        background: #ffffff !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }
    div[data-testid="stExpanderDetails"] {
        background: #ffffff !important;
    }
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* Mode sombre */
    @media (prefers-color-scheme: dark) {
        .glass-card { background: #1e293b; border-color: #334155; }
        .occupation-card { background: #1e293b; border-left-color: #818cf8; }
        .occupant-name { color: #f1f5f9; }
        .activity-name { color: #94a3b8; }
        .reservation-details { background: #0f172a; }
        .edit-section { background: #1e293b; border-color: #334155; }
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

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

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
                        st.warning(f"⚠️ Connexion Google Sheets impossible. Les réservations ponctuelles ne sont pas affichées.")
                        
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
                    <p style="font-size: 1.1rem; margin-top: 1rem;">
                        Le <strong>{format_date_fr(result_date)}</strong><br>
                        <span style="font-size: 0.95rem; opacity: 0.9;">Aucune occupation prévue</span>
                    </p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                if is_libre:
                    st.markdown(f'''
                    <div class="result-libre">
                        <h3>✅ La {salle.lower()} est libre</h3>
                        <p style="font-size: 1.1rem; margin-top: 1rem;">
                            Le <strong>{format_date_fr(result_date)}</strong> à <strong>{result_heure.strftime("%Hh%M")}</strong>
                        </p>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="result-occupe">
                        <h3>🔴 Occupation trouvée</h3>
                        <p style="font-size: 1.1rem; margin-top: 1rem;">
                            {len(occupations)} résultat(s) pour cette recherche
                        </p>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
                st.markdown("### 📋 Détails des occupations")

                # Afficher chaque occupation avec formulaire d'édition si c'est une réservation
                for idx, occ in enumerate(occupations):
                    horaire_display = occ.get("horaire", "Horaire non précisé")
                    occupant = occ.get("occupant", "Non précisé")
                    activite = occ.get("activite", "")
                    
                    # Préparer les infos financières pour affichage - uniquement si renseigné
                    details_items = []

                    accompte_display = occ.get('accompte', '')
                    if accompte_display:
                        details_items.append(f'💰 <strong>Accompte (€)</strong> {accompte_display}')

                    reste_display = occ.get('reste_a_payer', '')
                    if reste_display:
                        details_items.append(f'💳 <strong>Reste à payer (€)</strong> {reste_display}')

                    prix_display = occ.get('prix_location', '')
                    if prix_display:
                        details_items.append(f'💵 <strong>Prix location (€)</strong> {prix_display}')

                    caution_display = occ.get('caution_menage', '')
                    if caution_display:
                        details_items.append(f'🧹 <strong>Caution</strong> {caution_display}')

                    salle_display = occ.get('salle', '')
                    if salle_display:
                        details_items.append(f'🏠 <strong>Salle</strong> {salle_display}')

                    # Joindre les éléments avec <br> s'il y en a
                    details_html = '<br>'.join(details_items) if details_items else ''

                    with st.container():
                        # Afficher la carte en HTML compact (pas de sauts de ligne)
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
                        
                        # Formulaire d'édition dans un expander
                        if occ.get('source') == 'réservation':
                            with st.expander("✏️ Modifier les informations"):

                                # Petit résumé en haut du formulaire
                                st.markdown(f"""
                                <div style="margin-bottom:1rem;">
                                    <span style="font-size:0.875rem; color:#64748b;">Réservation</span>
                                    <strong style="color:#1e293b; margin-left:0.5rem;">{occupant}</strong>
                                    <span style="font-size:0.75rem; color:#94a3b8; margin-left:0.5rem;">{horaire_display}</span>
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

                                    # Actions : Sauvegarder principal + Effacer discret
                                    c1, c2, c3 = st.columns([3, 1, 1])
                                    with c1:
                                        submitted = st.form_submit_button("💾 Sauvegarder les modifications", type="primary", use_container_width=True)
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
                                                st.success("Modifications sauvegardées")
                                                st.session_state.occupations[idx].update(update_data)
                                                st.session_state.last_update = datetime.now()
                                                time_module.sleep(0.5)
                                                st.rerun()
                                            else:
                                                st.error(f"Erreur : {error}")

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
                                            st.success("Informations effacées")
                                            st.session_state.occupations[idx].update(update_data)
                                            st.session_state.last_update = datetime.now()
                                            time_module.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error(f"Erreur : {error}")

    # Auto-refresh toutes les 60 secondes si des résultats sont affichés
    if 'occupations' in st.session_state and st.session_state.occupations:
        # Afficher dernière mise à jour
        if 'last_update' in st.session_state:
            st.caption(f"🔄 Dernière mise à jour: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        # Bouton refresh manuel
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Rafraîchir", key="manual_refresh"):
                st.session_state.last_update = datetime.now()
                st.rerun()
        with col2:
            st.caption("Les données se rafraîchissent automatiquement toutes les 60 secondes")
        
        # Auto-refresh avec JavaScript
        st.markdown("""
        <script>
            setTimeout(function() {
                window.location.reload();
            }, 60000);
        </script>
        """, unsafe_allow_html=True)

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
