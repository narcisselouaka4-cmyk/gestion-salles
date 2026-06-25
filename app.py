#!/usr/bin/env python3
"""
Application Streamlit pour la vérification de disponibilité des salles
et l'édition du planning de réservation.
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
    pass

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

    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 8px 8px 0 0;
        gap: 4px;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
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


def render_occupation_card(occ):
    """Rendu HTML d'une carte d'occupation (lecture seule)."""
    horaire_display = occ.get("horaire", "Horaire non précisé")
    occupant = occ.get("occupant", "Non précisé")
    activite = occ.get("activite", "")

    details_items = []
    for key, label, icon in [
        ('accompte', 'Accompte (€)', '💰'),
        ('reste_a_payer', 'Reste à payer (€)', '💳'),
        ('prix_location', 'Prix location (€)', '💵'),
        ('caution_menage', 'Caution', '🧹'),
        ('salle', 'Salle', '🏠'),
    ]:
        val = occ.get(key, '')
        if val:
            details_items.append(f'{icon} <strong>{label}:</strong> {val}')

    details_html = '<br>'.join(details_items) if details_items else ''

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
    return ''.join(parts)


def init_checker():
    """Initialise le SalleChecker."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    salles_dir = os.path.join(script_dir, "salles")

    GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
    if not GOOGLE_SHEET_ID:
        try:
            GOOGLE_SHEET_ID = st.secrets.get("app_config", {}).get("google_sheet_id", "")
        except Exception:
            GOOGLE_SHEET_ID = ""

    if not os.path.exists(salles_dir):
        st.error("❌ Dossier 'salles/' introuvable. Vérifiez l'installation.")
        return None

    return SalleChecker(salles_dir, GOOGLE_SHEET_ID)


def onglet_gestion_salle(checker):
    """Onglet 1 : Gestion de Salle (lecture seule, sans édition)."""
    # Formulaire dans une card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        salle = st.selectbox(
            "🏠 **Salle**",
            options=["Salle principale", "Salle du fond", "Salle du milieu"],
            index=0,
            key="gs_salle"
        )

    with col2:
        date_input = st.date_input(
            "📅 **Date**",
            value=datetime.now().date(),
            min_value=datetime(2020, 1, 1).date(),
            max_value=datetime(2030, 12, 31).date(),
            key="gs_date"
        )

    sans_heure = st.checkbox("🕐 Voir toutes les occupations du jour", value=False, key="gs_sans_heure")

    heure = None
    if not sans_heure:
        heure = st.time_input(
            "⏰ **Heure**",
            value=datetime.now().time().replace(minute=0, second=0, microsecond=0),
            key="gs_heure"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bouton stylé
    verify_clicked = st.button("🔍 Vérifier la disponibilité", use_container_width=True, type="primary", key="gs_verify")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Zone de résultat
    if verify_clicked or 'gs_occupations' in st.session_state:

        if verify_clicked:
            # Recharger les données
            with st.spinner("Analyse en cours..."):
                try:
                    if sans_heure:
                        result = checker.get_all_occupations(salle.lower(), date_input)
                    else:
                        result = checker.check_availability(salle.lower(), date_input, heure)

                    st.session_state.gs_occupations = result.get("occupations", [])
                    st.session_state.gs_is_libre = result.get("libre", False)
                    st.session_state.gs_result_date = result.get("date", date_input)
                    st.session_state.gs_result_heure = result.get("heure", heure)
                    st.session_state.gs_res_salle = salle
                    st.session_state.gs_res_date_input = date_input

                    if "error" in result:
                        st.warning(f"⚠️ Connexion Google Sheets impossible. Les réservations ponctuelles ne sont pas affichées.")

                except Exception as e:
                    st.error(f"❌ Erreur lors de la vérification : {str(e)}")
                    st.session_state.gs_occupations = []

        # Afficher les résultats
        if 'gs_occupations' in st.session_state:
            occupations = st.session_state.gs_occupations
            is_libre = st.session_state.get("gs_is_libre", False)
            result_date = st.session_state.get("gs_result_date", date_input)
            result_heure = st.session_state.get("gs_result_heure", heure)
            current_salle = st.session_state.get("gs_res_salle", salle)

            if not occupations:
                st.markdown(f'''
                <div class="result-libre">
                    <h3>✅ La {current_salle.lower()} est libre</h3>
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
                        <h3>✅ La {current_salle.lower()} est libre</h3>
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

                for occ in occupations:
                    st.markdown(render_occupation_card(occ), unsafe_allow_html=True)


def onglet_editer_planning(checker):
    """Onglet 2 : Éditer Planning de Réservation (CRUD réservations ponctuelles)."""
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.5rem; color: #1e293b;">✏️ Éditer Planning de Réservation</h2>
        <p style="color: #64748b; margin-top: 0.25rem;">Rechercher, modifier ou ajouter une réservation ponctuelle</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Recherche ──
    # Mettre à jour les clés de widget AVANT leur création pour refléter
    # la date/salle cible après un ajout/édition réussi
    if st.session_state.get("ep_needs_search"):
        target_salle = st.session_state.get("ep_target_salle", "Salle principale")
        target_date = st.session_state.get("ep_target_date", datetime.now().date())
        st.session_state.ep_salle = target_salle
        st.session_state.ep_date = target_date

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        ep_salle = st.selectbox(
            "🏠 **Salle**",
            options=["Salle principale", "Salle du fond", "Salle du milieu"],
            key="ep_salle"
        )
    with col2:
        ep_date = st.date_input(
            "📅 **Date**",
            min_value=datetime(2020, 1, 1).date(),
            max_value=datetime(2030, 12, 31).date(),
            key="ep_date"
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    search_clicked = st.button("🔍 Rechercher les réservations", use_container_width=True, type="primary", key="ep_search")

    # ── Résultats ──
    needs_search = st.session_state.get("ep_needs_search", False)
    if search_clicked or 'ep_occupations' in st.session_state or needs_search:
        if search_clicked or needs_search:
            if needs_search:
                st.session_state.ep_needs_search = False
            with st.spinner("Recherche en cours..."):
                try:
                    result = checker.get_all_occupations(ep_salle.lower(), ep_date)
                    # On ne garde QUE les réservations ponctuelles (source='réservation')
                    all_occ = result.get("occupations", [])
                    res_ponctuelles = [o for o in all_occ if o.get("source") == "réservation"]

                    st.session_state.ep_occupations = res_ponctuelles
                    st.session_state.ep_res_salle = ep_salle
                    st.session_state.ep_res_date = ep_date
                    st.session_state.ep_target_date = ep_date  # garde la date en mémoire
                    st.session_state.ep_target_salle = ep_salle  # garde la salle en mémoire

                    if "error" in result:
                        st.warning("⚠️ Connexion Google Sheets impossible.")
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
                    st.session_state.ep_occupations = []

    # Messages flash édition
    if st.session_state.get("ep_edit_success"):
        st.success(st.session_state.ep_edit_success)
        st.session_state.ep_edit_success = None
        st.session_state.ep_edit_error = None
    if st.session_state.get("ep_edit_error"):
        st.error(f"❌ Erreur : {st.session_state.ep_edit_error}")
        st.session_state.ep_edit_error = None
        st.session_state.ep_edit_success = None

    if 'ep_occupations' in st.session_state:
        occupations = st.session_state.ep_occupations
        current_salle = st.session_state.get("ep_res_salle", ep_salle)
        current_date = st.session_state.get("ep_res_date", ep_date)

        if not occupations:
            st.info(f"📭 Aucune réservation ponctuelle trouvée pour **{current_salle}** le **{format_date_fr(current_date)}**.")
        else:
            st.markdown(f"### 📋 {len(occupations)} réservation(s) trouvée(s)")

            for idx, occ in enumerate(occupations):
                horaire_display = occ.get("horaire", "Horaire non précisé")
                occupant = occ.get("occupant", "Non précisé")

                with st.expander(f"✏️ {occupant} — {horaire_display}"):
                    st.markdown(f"""
                    <div style="margin-bottom:1rem;">
                        <span style="font-size:0.875rem; color:#64748b;">Réservation ponctuelle</span>
                        <strong style="color:#1e293b; margin-left:0.5rem;">{occupant}</strong>
                        <span style="font-size:0.75rem; color:#94a3b8; margin-left:0.5rem;">{horaire_display}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.form(key=f"ep_edit_form_{idx}", border=False):
                        col1, col2 = st.columns(2)

                        with col1:
                            new_nom = st.text_input("👤 Nom", value=occ.get('occupant', ''), key=f"ep_nom_{idx}")
                            new_horaire = st.text_input("🕐 Horaire", value=occ.get('horaire', ''), placeholder="Ex: 15H30 - 18H00", key=f"ep_horaire_{idx}")
                            new_date_str = st.text_input("📅 Date (JJ/MM/AA)", value=current_date.strftime("%d/%m/%y"), key=f"ep_date_str_{idx}")

                            new_accompte = st.text_input("💰 Accompte (€)", value=occ.get('accompte', ''), placeholder="Ex: 100", key=f"ep_accompte_{idx}")
                            new_reste = st.text_input("💳 Reste à payer (€)", value=occ.get('reste_a_payer', ''), placeholder="Ex: 550", key=f"ep_reste_{idx}")

                        with col2:
                            new_prix = st.text_input("💵 Prix location (€)", value=occ.get('prix_location', ''), placeholder="Ex: 650", key=f"ep_prix_{idx}")
                            new_caution = st.text_input("🧹 Caution", value=occ.get('caution_menage', ''), placeholder="Ex: Oui", key=f"ep_caution_{idx}")
                            new_salle_occ = st.text_input("🏠 Salle", value=occ.get('salle', ''), placeholder="Ex: Salle principale", key=f"ep_salle_occ_{idx}")

                        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                        with c1:
                            submitted = st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True)
                        with c2:
                            clear_submitted = st.form_submit_button("💳 Effacer infos", use_container_width=True)
                        with c4:
                            delete_submitted = st.form_submit_button("🗑️ Supprimer", use_container_width=True)

                        if submitted:
                            old_occupant = occ.get('occupant', '')
                            update_data = {}

                            if new_nom != old_occupant:
                                update_data['occupant'] = new_nom if new_nom else "Non renseigné"
                            if new_horaire != occ.get('horaire', ''):
                                update_data['horaire'] = new_horaire
                            if new_date_str != current_date.strftime("%d/%m/%y"):
                                update_data['date'] = new_date_str
                            if new_salle_occ != occ.get('salle', ''):
                                update_data['salle'] = new_salle_occ

                            update_data['accompte'] = f"{new_accompte}€" if new_accompte and '€' not in new_accompte else (new_accompte if new_accompte else "")
                            update_data['reste_a_payer'] = f"{new_reste}€" if new_reste and '€' not in new_reste else (new_reste if new_reste else "")
                            update_data['prix_location'] = f"{new_prix}€" if new_prix and '€' not in new_prix else (new_prix if new_prix else "")
                            update_data['caution_menage'] = new_caution if new_caution else ""
                            update_data['salle_occupation'] = new_salle_occ if new_salle_occ else ""

                            success, error = checker.update_reservation_google(
                                current_salle.lower(),
                                current_date,
                                old_occupant.strip(),
                                update_data
                            )

                            if success:
                                st.session_state.ep_edit_success = "✅ Modifications sauvegardées"
                                st.session_state.ep_edit_error = None
                                st.session_state.ep_needs_search = True
                            else:
                                st.session_state.ep_edit_error = error
                                st.session_state.ep_edit_success = None
                            st.rerun()

                        if clear_submitted:
                            old_occupant = occ.get('occupant', '')
                            update_data = {
                                'accompte': "",
                                'reste_a_payer': "",
                                'prix_location': "",
                                'caution_menage': "",
                                'salle_occupation': ""
                            }

                            success, error = checker.update_reservation_google(
                                current_salle.lower(),
                                current_date,
                                old_occupant.strip(),
                                update_data
                            )

                            if success:
                                st.session_state.ep_edit_success = "💳 Informations effacées"
                                st.session_state.ep_edit_error = None
                                st.session_state.ep_needs_search = True
                            else:
                                st.session_state.ep_edit_error = error
                                st.session_state.ep_edit_success = None
                            st.rerun()

                        if delete_submitted:
                            old_occupant = occ.get('occupant', '')
                            success, error = checker.delete_reservation_google(
                                current_salle.lower(),
                                current_date,
                                old_occupant.strip()
                            )
                            if success:
                                st.session_state.ep_edit_success = "🗑️ Réservation supprimée"
                                st.session_state.ep_edit_error = None
                                st.session_state.ep_needs_search = True
                            else:
                                st.session_state.ep_edit_error = error
                                st.session_state.ep_edit_success = None
                            st.rerun()

    st.markdown("---")

    # ── Messages flash (succès/erreur) persistés après rerun ──
    add_success_msg = st.session_state.get("ep_add_success")
    if add_success_msg:
        st.success(add_success_msg)
        st.session_state.ep_add_success = False
        st.session_state.ep_add_error = None
    if st.session_state.get("ep_add_error"):
        st.error(f"❌ Erreur : {st.session_state.ep_add_error}")
        st.session_state.ep_add_error = None
        st.session_state.ep_add_success = False

    # ── Ajouter une nouvelle réservation ──
    st.markdown("### ➕ Ajouter une nouvelle réservation")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    with st.form(key="ep_add_form", border=False):
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            add_nom = st.text_input("👤 Nom", placeholder="Nom du réservant", key="add_nom")
            add_horaire = st.text_input("🕐 Horaire", placeholder="Ex: 15H30 - 18H00", key="add_horaire")
            add_date_str = st.text_input("📅 Date (JJ/MM/AA)", value=ep_date.strftime("%d/%m/%y"), key="add_date")
            add_accompte = st.text_input("💰 Accompte (€)", placeholder="Ex: 100", key="add_accompte")

        with a_col2:
            add_prix = st.text_input("💵 Prix location (€)", placeholder="Ex: 650", key="add_prix")
            add_reste = st.text_input("💳 Reste à payer (€)", placeholder="Ex: 550", key="add_reste")
            add_caution = st.text_input("🧹 Caution", placeholder="Ex: Oui", key="add_caution")

        add_salle_select = st.selectbox(
            "🏠 Salle concernée",
            options=["Salle principale", "Salle du fond", "Salle du milieu"],
            key="add_salle_select"
        )

        add_submitted = st.form_submit_button("➕ Ajouter la réservation", type="primary", use_container_width=True)

        if add_submitted:
            if not add_nom:
                st.session_state.ep_add_error = "Le nom est obligatoire."
                st.rerun()
            elif not add_horaire:
                st.session_state.ep_add_error = "L'horaire est obligatoire."
                st.rerun()
            elif not add_date_str:
                st.session_state.ep_add_error = "La date est obligatoire."
                st.rerun()
            else:
                new_data = {
                    'salle': add_salle_select,
                    'occupant': add_nom,
                    'horaire': add_horaire,
                    'date': add_date_str,
                    'accompte': f"{add_accompte}€" if add_accompte and '€' not in add_accompte else (add_accompte if add_accompte else ""),
                    'reste_a_payer': f"{add_reste}€" if add_reste and '€' not in add_reste else (add_reste if add_reste else ""),
                    'prix_location': f"{add_prix}€" if add_prix and '€' not in add_prix else (add_prix if add_prix else ""),
                    'caution_menage': add_caution if add_caution else "",
                    'salle_occupation': "",
                }

                success, info = checker.add_reservation_google(new_data)

                if success:
                    st.session_state.ep_add_success = f"✅ Réservation ajoutée dans l'onglet '{info}'"
                    st.session_state.ep_add_error = None
                    st.session_state.ep_needs_search = True
                    # Garder en mémoire la date et la salle de la réservation ajoutée
                    # pour que la recherche auto se fasse avec les bons critères
                    try:
                        st.session_state.ep_target_date = datetime.strptime(add_date_str, "%d/%m/%y").date()
                    except ValueError:
                        st.session_state.ep_target_date = datetime.now().date()
                    st.session_state.ep_target_salle = add_salle_select
                else:
                    st.session_state.ep_add_error = info
                    st.session_state.ep_add_success = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    # Header Moderne avec Gradient
    st.markdown('''
    <div class="main-header">
        <h1>🏢 Gestion des Salles</h1>
        <div class="sub-header">CFPDC — Centre de Formation Pédagogique des Disciples du Christ</div>
    </div>
    ''', unsafe_allow_html=True)

    # Initialiser le checker
    checker = init_checker()
    if checker is None:
        return

    # Onglets principaux
    tab1, tab2 = st.tabs(["🏢 Gestion de Salle", "✏️ Éditer Planning de Réservation"])

    with tab1:
        onglet_gestion_salle(checker)

    with tab2:
        onglet_editer_planning(checker)

    # Footer commun
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
