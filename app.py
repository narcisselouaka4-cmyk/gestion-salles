#!/usr/bin/env python3
"""
Application Streamlit — Gestion des Salles CFPDC
UI Professionnelle type Dashboard SaaS
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, time, date, timedelta
import os
import time as time_module

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from checker import SalleChecker

# ═══════════════════════════════════════════════════════════
# CONFIG PAGE
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CFPDC — Gestion des Salles",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# PWA MANIFEST (injection dans le <head>)
# ═══════════════════════════════════════════════════════════
components.html("""
<script>
    // Manifest PWA
    if (!document.querySelector('link[rel="manifest"]')) {
        const link = document.createElement('link');
        link.rel = 'manifest';
        link.href = 'https://gestion-salles-usjp.onrender.com/assets/manifest.json';
        document.head.appendChild(link);
    }
    // Theme color
    if (!document.querySelector('meta[name="theme-color"]')) {
        const meta = document.createElement('meta');
        meta.name = 'theme-color';
        meta.content = '#4f46e5';
        document.head.appendChild(meta);
    }
    // Apple touch icon
    if (!document.querySelector('link[rel="apple-touch-icon"]')) {
        const icon = document.createElement('link');
        icon.rel = 'apple-touch-icon';
        icon.href = 'https://gestion-salles-usjp.onrender.com/assets/qr-code.png';
        document.head.appendChild(icon);
    }
</script>
""", height=0)

# ═══════════════════════════════════════════════════════════
# CSS MODERNE — Design System SaaS (Light & Dark compatible)
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Pas de fond forcé — on laisse Streamlit gérer le thème */
    .main .block-container {
        max-width: 1400px;
        padding: 2rem 3rem;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: none;
    }
    section[data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }

    /* ── Typography ── */
    h1 { font-weight: 800; letter-spacing: -0.03em; }
    h2 { font-weight: 700; letter-spacing: -0.02em; }
    h3 { font-weight: 600; }

    /* ── KPI Cards ── */
    .kpi-card {
        background: rgba(128,128,128,0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(128,128,128,0.12);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        border-radius: 20px 20px 0 0;
    }
    .kpi-card.success::before { background: linear-gradient(90deg, #10b981, #34d399); }
    .kpi-card.warning::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .kpi-card.danger::before { background: linear-gradient(90deg, #ef4444, #f87171); }

    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* ── Glass Cards ── */
    .glass-card {
        background: rgba(128,128,128,0.06);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }

    /* ── Timeline (Flexbox — pas de position absolute) ── */
    .timeline-bar {
        display: flex;
        width: 100%;
        height: 48px;
        background: rgba(128,128,128,0.1);
        border-radius: 12px;
        overflow: hidden;
        position: relative;
        margin-bottom: 0.5rem;
    }
    .timeline-slot {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: transform 0.2s ease, filter 0.2s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding: 0 6px;
        border-radius: 10px;
        margin: 4px 2px;
        min-width: 0;
    }
    .timeline-slot:hover {
        transform: scale(1.03);
        filter: brightness(1.15);
        z-index: 10;
    }
    .timeline-empty {
        flex: 1;
        min-width: 0;
    }
    .timeline-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        color: #94a3b8;
        font-weight: 500;
        padding: 0 4px;
    }

    /* ── Reservation Row ── */
    .res-row {
        display: flex;
        align-items: center;
        padding: 1rem 1.25rem;
        background: rgba(128,128,128,0.05);
        border-radius: 14px;
        margin-bottom: 0.6rem;
        border: 1px solid rgba(128,128,128,0.08);
        transition: all 0.2s ease;
        gap: 1rem;
    }
    .res-row:hover {
        background: rgba(128,128,128,0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        transform: translateX(4px);
    }
    .res-time {
        min-width: 100px;
        font-weight: 700;
        font-size: 0.85rem;
        color: #4f46e5;
        background: rgba(79,70,229,0.1);
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        text-align: center;
    }
    .res-name {
        flex: 1;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .res-meta {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .res-tag {
        font-size: 0.7rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        background: rgba(128,128,128,0.1);
        font-weight: 500;
    }

    /* ── Detail Card ── */
    .detail-card {
        background: rgba(128,128,128,0.06);
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 20px;
        padding: 1.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        position: relative;
        overflow: hidden;
    }
    .detail-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #6366f1, #8b5cf6);
        border-radius: 20px 0 0 20px;
    }
    .detail-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .detail-time {
        font-size: 1.1rem;
        font-weight: 800;
        color: #4f46e5;
    }
    .detail-name {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }
    .detail-activity {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }
    .detail-item {
        background: rgba(128,128,128,0.08);
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        font-size: 0.8rem;
    }
    .detail-item-label {
        font-size: 0.7rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.15rem;
    }
    .detail-item-value {
        font-weight: 600;
    }

    /* ── Form Section ── */
    .form-section {
        background: rgba(128,128,128,0.06);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    .form-section-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .form-section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(128,128,128,0.2), transparent);
        margin-left: 0.5rem;
    }

    /* ── Animations ── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .animate-in {
        animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }

    /* ── Streamlit overrides ── */
    div[data-testid="stTabs"] {
        background: transparent;
    }
    div[data-testid="stTabContent"] {
        padding-top: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(128,128,128,0.08);
        border-radius: 16px;
        padding: 6px;
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 12px;
        background: transparent;
        border: none;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        margin: 0 2px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: inherit;
        background: rgba(128,128,128,0.1);
    }
    .stTabs [aria-selected="true"] {
        background: rgba(128,128,128,0.15) !important;
        color: #4f46e5 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* Buttons override */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 12px;
        font-weight: 500;
    }

    /* Expander override */
    div[data-testid="stExpander"] {
        border: 1px solid rgba(128,128,128,0.12) !important;
        border-radius: 16px !important;
        background: rgba(128,128,128,0.04) !important;
        margin-bottom: 0.75rem !important;
    }
    div[data-testid="stExpanderDetails"] {
        background: transparent !important;
    }

    /* Select override */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stTimeInput"] label {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════
def format_date_fr(d):
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


def time_to_minutes(t):
    if t is None:
        return None
    return t.hour * 60 + t.minute


def parse_horaire_minutes(horaire_str):
    if not horaire_str:
        return None, None
    try:
        from checker import parse_horaire
        debut, fin = parse_horaire(horaire_str)
        return time_to_minutes(debut), time_to_minutes(fin)
    except Exception:
        return None, None


def render_timeline(occupations, start_hour=8, end_hour=23):
    """Timeline en flexbox — pas de position:absolute."""
    if not occupations:
        return '<div style="text-align:center; padding:2rem; color:#94a3b8;">Aucune occupation sur ce créneau</div>'

    total_min = (end_hour - start_hour) * 60
    colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#14b8a6']

    segments = []
    current_min = 0

    for i, occ in enumerate(occupations):
        debut_min, fin_min = parse_horaire_minutes(occ.get('horaire', ''))
        if debut_min is None:
            continue

        if fin_min is not None and fin_min < debut_min:
            fin_min += 24 * 60

        rel_start = max(0, debut_min - start_hour * 60)
        rel_end = min(total_min, (fin_min or (debut_min + 120)) - start_hour * 60)
        duration = rel_end - rel_start

        if duration <= 0:
            duration = 60

        # Empty space before
        empty_before = rel_start - current_min
        if empty_before > 0:
            empty_pct = (empty_before / total_min) * 100
            segments.append(f'<div class="timeline-empty" style="flex: 0 0 {empty_pct}%;"></div>')

        # Occupation slot
        slot_pct = (duration / total_min) * 100
        color = colors[i % len(colors)]
        name = occ.get('occupant', 'Inconnu')[:14]

        segments.append(
            f'<div class="timeline-slot" '
            f'style="flex: 0 0 {slot_pct}%; background: {color};" '
            f'title="{occ.get("occupant", "")} — {occ.get("horaire", "")}">'
            f'{name}</div>'
        )

        current_min = rel_end

    # Empty space after
    if current_min < total_min:
        empty_after = total_min - current_min
        empty_pct = (empty_after / total_min) * 100
        segments.append(f'<div class="timeline-empty" style="flex: 0 0 {empty_pct}%;"></div>')

    labels = []
    for h in range(start_hour, end_hour + 1, 2):
        labels.append(f'<span>{h}h</span>')

    return f"""
    <div class="animate-in">
        <div class="timeline-bar">
            {''.join(segments)}
        </div>
        <div class="timeline-labels">
            {''.join(labels)}
        </div>
    </div>
    """


def render_detail_card(occ):
    horaire = occ.get("horaire", "Horaire non précisé")
    occupant = occ.get("occupant", "Non précisé")
    activite = occ.get("activite", "")

    meta_items = []
    for key, label in [
        ('accompte', 'Accompte'),
        ('reste_a_payer', 'Reste'),
        ('prix_location', 'Prix loc.'),
        ('caution_menage', 'Caution'),
        ('salle', 'Salle'),
    ]:
        val = occ.get(key, '')
        if val:
            meta_items.append(f'<div class="detail-item"><div class="detail-item-label">{label}</div><div class="detail-item-value">{val}</div></div>')

    meta_grid = f'<div class="detail-grid">{ "".join(meta_items) }</div>' if meta_items else ''
    activite_html = f'<div class="detail-activity">{activite}</div>' if activite else ''

    return f"""
    <div class="detail-card animate-in">
        <div class="detail-header">
            <div>
                <div class="detail-time">{horaire}</div>
                <div class="detail-name">{occupant}</div>
                {activite_html}
            </div>
        </div>
        {meta_grid}
    </div>
    """


def render_reservation_row(occ, idx):
    horaire = occ.get("horaire", "—")
    occupant = occ.get("occupant", "Non précisé")
    salle = occ.get("salle", "")
    prix = occ.get("prix_location", "")
    reste = occ.get("reste_a_payer", "")

    tags = []
    if prix:
        tags.append(f'<span class="res-tag">{prix}</span>')
    if reste:
        tags.append(f'<span class="res-tag">Reste: {reste}</span>')
    if salle:
        tags.append(f'<span class="res-tag">{salle}</span>')

    return f"""
    <div class="res-row animate-in" style="animation-delay: {idx * 0.05}s;">
        <div class="res-time">{horaire}</div>
        <div class="res-name">{occupant}</div>
        <div class="res-meta">{''.join(tags)}</div>
    </div>
    """


# ═══════════════════════════════════════════════════════════
# INITIALISATION CHECKER
# ═══════════════════════════════════════════════════════════
@st.cache_resource
def init_checker():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    salles_dir = os.path.join(script_dir, "salles")

    GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
    if not GOOGLE_SHEET_ID:
        try:
            GOOGLE_SHEET_ID = st.secrets.get("app_config", {}).get("google_sheet_id", "")
        except Exception:
            GOOGLE_SHEET_ID = ""

    if not os.path.exists(salles_dir):
        return None

    return SalleChecker(salles_dir, GOOGLE_SHEET_ID)


# ═══════════════════════════════════════════════════════════
# SIDEBAR — Fonctionnelle
# ═══════════════════════════════════════════════════════════
def render_sidebar(checker):
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="padding: 1rem 0 2rem 0; text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏢</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em;">CFPDC</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">Gestion des Salles</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color: #334155; margin: 1rem 0;'>", unsafe_allow_html=True)

        # ── Paramètres rapides ──
        st.markdown("<div style='font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;'>Paramètres rapides</div>", unsafe_allow_html=True)

        st.caption("Ces valeurs sont préremplies dans les deux onglets")

        if "global_salle" not in st.session_state:
            st.session_state.global_salle = "Salle principale"
        if "global_date" not in st.session_state:
            st.session_state.global_date = datetime.now().date()

        salle_options = ["Salle principale", "Salle du fond", "Salle du milieu"]
        salle_idx = salle_options.index(st.session_state.global_salle) if st.session_state.global_salle in salle_options else 0

        sidebar_salle = st.selectbox(
            "Salle",
            options=salle_options,
            index=salle_idx,
            key="sidebar_salle",
            label_visibility="collapsed"
        )

        sidebar_date = st.date_input(
            "Date",
            value=st.session_state.global_date,
            min_value=date(2020, 1, 1),
            max_value=date(2030, 12, 31),
            key="sidebar_date",
            label_visibility="collapsed"
        )

        # Sync to global
        st.session_state.global_salle = sidebar_salle
        st.session_state.global_date = sidebar_date

        # Boutons rapides
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📅 Aujourd'hui", use_container_width=True):
                st.session_state.global_date = datetime.now().date()
                st.rerun()
        with c2:
            if st.button("📅 Demain", use_container_width=True):
                st.session_state.global_date = (datetime.now() + timedelta(days=1)).date()
                st.rerun()

        st.markdown("<hr style='border-color: #334155; margin: 1.5rem 0;'>", unsafe_allow_html=True)

        # ── Statut des salles — maintenant ──
        st.markdown("<div style='font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;'>Statut actuel</div>", unsafe_allow_html=True)

        now = datetime.now()
        now_time = now.time()

        for salle_name in salle_options:
            try:
                result = checker.check_availability(salle_name.lower(), now.date(), now_time)
                is_libre = result.get("libre", False)
                occs = result.get("occupations", [])

                if is_libre or not occs:
                    status_color = "#10b981"
                    status_text = "LIBRE"
                else:
                    status_color = "#ef4444"
                    status_text = "OCCUPÉE"

                next_info = ""
                if occs and not is_libre:
                    next_info = occs[0].get("horaire", "")
                elif occs:
                    next_info = f"{len(occs)} occupation(s)"

                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 0.85rem; color: #e2e8f0; font-weight: 500;">{salle_name}</div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: {status_color};">{status_text}</div>
                        <div style="font-size: 0.65rem; color: #64748b;">{next_info}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass

        st.markdown("<hr style='border-color: #334155; margin: 1.5rem 0;'>", unsafe_allow_html=True)

        # ── Raccourcis ──
        st.markdown("<div style='font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;'>Raccourcis</div>", unsafe_allow_html=True)

        GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
        if not GOOGLE_SHEET_ID:
            try:
                GOOGLE_SHEET_ID = st.secrets.get("app_config", {}).get("google_sheet_id", "")
            except Exception:
                GOOGLE_SHEET_ID = ""

        if GOOGLE_SHEET_ID:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit"
            st.markdown(f'''
            <a href="{sheet_url}" target="_blank" style="display: block; text-decoration: none; margin-bottom: 0.5rem;">
                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #94a3b8; font-weight: 500; transition: all 0.2s;">
                    📊 Ouvrir Google Sheet →
                </div>
            </a>
            ''', unsafe_allow_html=True)

        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #94a3b8; font-weight: 500;">
            📁 Gestion de Salle → Lecture seule, recherche par date/heure
        </div>
        <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #94a3b8; font-weight: 500; margin-top: 0.5rem;">
            ✏️ Planning → Ajouter, modifier, supprimer des réservations
        </div>
        """, unsafe_allow_html=True)

        # Footer
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; font-size: 0.7rem; color: #475569;">
            CFPDC © 2024<br>
            <span style="color: #334155;">v2.1 — Dashboard Pro</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# ONGLET 1 — DASHBOARD GESTION DE SALLE
# ═══════════════════════════════════════════════════════════
def onglet_gestion_salle(checker):
    default_salle = st.session_state.get("global_salle", "Salle principale")
    default_date = st.session_state.get("global_date", datetime.now().date())

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        salle = st.selectbox(
            "SALLE",
            options=["Salle principale", "Salle du fond", "Salle du milieu"],
            index=["Salle principale", "Salle du fond", "Salle du milieu"].index(default_salle),
            key="gs_salle"
        )
    with col2:
        date_input = st.date_input(
            "DATE",
            value=default_date,
            min_value=date(2020, 1, 1),
            max_value=date(2030, 12, 31),
            key="gs_date"
        )
    with col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        sans_heure = st.toggle("Journée complète", value=True, key="gs_sans_heure")

    heure = None
    if not sans_heure:
        heure = st.time_input(
            "HEURE",
            value=datetime.now().time().replace(minute=0, second=0, microsecond=0),
            key="gs_heure"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    verify_clicked = st.button("Analyser la disponibilité", use_container_width=True, type="primary", key="gs_verify")

    if verify_clicked or 'gs_occupations' in st.session_state:
        if verify_clicked:
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
                        st.toast("Connexion Google Sheets impossible — réservations non affichées", icon="⚠️")
                except Exception as e:
                    st.error(f"Erreur lors de la vérification : {str(e)}")
                    st.session_state.gs_occupations = []

        if 'gs_occupations' in st.session_state:
            occupations = st.session_state.gs_occupations
            is_libre = st.session_state.get("gs_is_libre", False)
            result_date = st.session_state.get("gs_result_date", date_input)
            result_heure = st.session_state.get("gs_result_heure", heure)
            current_salle = st.session_state.get("gs_res_salle", salle)

            kpi1, kpi2, kpi3 = st.columns(3)

            with kpi1:
                if not occupations:
                    status_class = "success"
                    status_text = "LIBRE"
                    status_sub = "Aucune occupation"
                elif is_libre:
                    status_class = "success"
                    status_text = "LIBRE"
                    status_sub = f"{len(occupations)} occupation(s) hors créneau"
                else:
                    status_class = "danger"
                    status_text = "OCCUPÉE"
                    status_sub = f"{len(occupations)} conflit(s)"

                st.markdown(f"""
                <div class="kpi-card {status_class} animate-in">
                    <div class="kpi-label">Statut</div>
                    <div class="kpi-value">{status_text}</div>
                    <div class="kpi-sub">{status_sub}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi2:
                next_occ = "—"
                next_time = ""
                if occupations and not is_libre:
                    next_occ = occupations[0].get('occupant', 'Occupé')
                    next_time = occupations[0].get('horaire', '')
                elif occupations:
                    next_occ = f"{len(occupations)} résa."

                st.markdown(f"""
                <div class="kpi-card info animate-in">
                    <div class="kpi-label">Prochaine occupation</div>
                    <div class="kpi-value" style="font-size: 1.4rem;">{next_occ}</div>
                    <div class="kpi-sub">{next_time}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi3:
                total_revenus = 0
                for occ in occupations:
                    prix_str = str(occ.get('prix_location', '')).replace('€', '').replace(' ', '')
                    try:
                        if prix_str:
                            total_revenus += float(prix_str)
                    except ValueError:
                        pass

                revenus_text = f"{total_revenus:.0f} €" if total_revenus > 0 else "—"

                st.markdown(f"""
                <div class="kpi-card warning animate-in">
                    <div class="kpi-label">Revenus jour</div>
                    <div class="kpi-value">{revenus_text}</div>
                    <div class="kpi-sub">Prix location total</div>
                </div>
                """, unsafe_allow_html=True)

            # Timeline
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("### Timeline des occupations")
            st.markdown(render_timeline(occupations), unsafe_allow_html=True)

            # Détails
            if occupations:
                st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                st.markdown("### Détails des occupations")
                for occ in occupations:
                    st.markdown(render_detail_card(occ), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
                    <div style="font-size: 1.1rem; font-weight: 600;">La salle est entièrement libre</div>
                    <div style="font-size: 0.9rem; margin-top: 0.5rem; color: #94a3b8;">Aucune occupation prévue pour cette journée</div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# ONGLET 2 — PLANNING & RÉSERVATIONS
# ═══════════════════════════════════════════════════════════
def onglet_editer_planning(checker):
    default_salle = st.session_state.get("global_salle", "Salle principale")
    default_date = st.session_state.get("global_date", datetime.now().date())

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.4rem;">Planning de Réservation</h2>
        <p style="color: #94a3b8; margin-top: 0.25rem; font-size: 0.9rem;">Gérez les réservations ponctuelles du Google Sheet</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        ep_salle = st.selectbox(
            "SALLE",
            options=["Salle principale", "Salle du fond", "Salle du milieu"],
            index=["Salle principale", "Salle du fond", "Salle du milieu"].index(default_salle),
            key="ep_salle"
        )
    with c2:
        ep_date = st.date_input(
            "DATE",
            value=default_date,
            min_value=date(2020, 1, 1),
            max_value=date(2030, 12, 31),
            key="ep_date"
        )
    with c3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_clicked = st.button("Rechercher", use_container_width=True, type="primary", key="ep_search")

    st.markdown("</div>", unsafe_allow_html=True)

    needs_search = st.session_state.get("ep_needs_search", False)
    if search_clicked or 'ep_occupations' in st.session_state or needs_search:
        if search_clicked or needs_search:
            if needs_search:
                st.session_state.ep_needs_search = False
            with st.spinner("Recherche en cours..."):
                try:
                    result = checker.get_all_occupations(ep_salle.lower(), ep_date)
                    all_occ = result.get("occupations", [])
                    res_ponctuelles = [o for o in all_occ if o.get("source") == "réservation"]

                    st.session_state.ep_occupations = res_ponctuelles
                    st.session_state.ep_res_salle = ep_salle
                    st.session_state.ep_res_date = ep_date
                    st.session_state.ep_target_date = ep_date
                    st.session_state.ep_target_salle = ep_salle

                    if "error" in result:
                        st.toast("Connexion Google Sheets impossible", icon="⚠️")
                except Exception as e:
                    st.error(f"Erreur : {str(e)}")
                    st.session_state.ep_occupations = []

    if st.session_state.get("ep_edit_success"):
        st.success(st.session_state.ep_edit_success)
        st.session_state.ep_edit_success = None
        st.session_state.ep_edit_error = None
    if st.session_state.get("ep_edit_error"):
        st.error(f"Erreur : {st.session_state.ep_edit_error}")
        st.session_state.ep_edit_error = None
        st.session_state.ep_edit_success = None

    if 'ep_occupations' in st.session_state:
        occupations = st.session_state.ep_occupations
        current_salle = st.session_state.get("ep_res_salle", ep_salle)
        current_date = st.session_state.get("ep_res_date", ep_date)

        if not occupations:
            st.info(f"Aucune réservation ponctuelle pour **{current_salle}** le **{format_date_fr(current_date)}**.")
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">
                    {len(occupations)} réservation(s)
                </div>
            </div>
            """, unsafe_allow_html=True)

            for idx, occ in enumerate(occupations):
                st.markdown(render_reservation_row(occ, idx), unsafe_allow_html=True)

                with st.expander("Modifier"):
                    with st.form(key=f"ep_edit_form_{idx}", border=False):
                        ec1, ec2, ec3 = st.columns(3)
                        with ec1:
                            new_nom = st.text_input("Nom", value=occ.get('occupant', ''), key=f"ep_nom_{idx}")
                            new_horaire = st.text_input("Horaire", value=occ.get('horaire', ''), placeholder="15H30 - 18H00", key=f"ep_horaire_{idx}")
                            new_date_str = st.text_input("Date (JJ/MM/AA)", value=current_date.strftime("%d/%m/%y"), key=f"ep_date_str_{idx}")
                        with ec2:
                            new_accompte = st.text_input("Accompte (€)", value=occ.get('accompte', ''), key=f"ep_accompte_{idx}")
                            new_reste = st.text_input("Reste (€)", value=occ.get('reste_a_payer', ''), key=f"ep_reste_{idx}")
                            new_prix = st.text_input("Prix loc. (€)", value=occ.get('prix_location', ''), key=f"ep_prix_{idx}")
                        with ec3:
                            new_caution = st.text_input("Caution", value=occ.get('caution_menage', ''), key=f"ep_caution_{idx}")
                            new_salle_occ = st.text_input("Salle", value=occ.get('salle', ''), key=f"ep_salle_occ_{idx}")

                        btn1, btn2, btn3, btn4 = st.columns([2, 1, 1, 1])
                        with btn1:
                            submitted = st.form_submit_button("Sauvegarder", type="primary", use_container_width=True)
                        with btn2:
                            clear_submitted = st.form_submit_button("Effacer infos", use_container_width=True)
                        with btn4:
                            delete_submitted = st.form_submit_button("Supprimer", use_container_width=True)

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
                                current_salle.lower(), current_date, old_occupant.strip(), update_data
                            )
                            if success:
                                st.session_state.ep_edit_success = "Modifications sauvegardées"
                                st.session_state.ep_needs_search = True
                            else:
                                st.session_state.ep_edit_error = error
                            st.rerun()

                        if clear_submitted:
                            old_occupant = occ.get('occupant', '')
                            success, error = checker.update_reservation_google(
                                current_salle.lower(), current_date, old_occupant.strip(),
                                {'accompte': "", 'reste_a_payer': "", 'prix_location': "", 'caution_menage': "", 'salle_occupation': ""}
                            )
                            if success:
                                st.session_state.ep_edit_success = "Informations effacées"
                                st.session_state.ep_needs_search = True
                            else:
                                st.session_state.ep_edit_error = error
                            st.rerun()

                        if delete_submitted:
                            old_occupant = occ.get('occupant', '')
                            success, error = checker.delete_reservation_google(
                                current_salle.lower(), current_date, old_occupant.strip()
                            )
                            if success:
                                st.session_state.ep_edit_success = "Réservation supprimée"
                                st.session_state.ep_needs_search = True
                            else:
                                st.session_state.ep_edit_error = error
                            st.rerun()

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    add_success_msg = st.session_state.get("ep_add_success")
    if add_success_msg:
        st.success(add_success_msg)
        st.session_state.ep_add_success = False
        st.session_state.ep_add_error = None
    if st.session_state.get("ep_add_error"):
        st.error(f"Erreur : {st.session_state.ep_add_error}")
        st.session_state.ep_add_error = None
        st.session_state.ep_add_success = False

    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="margin: 0; font-size: 1.1rem;">Nouvelle réservation</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='form-section'>", unsafe_allow_html=True)

    with st.form(key="ep_add_form", border=False):
        a_col1, a_col2, a_col3 = st.columns(3)
        with a_col1:
            add_nom = st.text_input("Nom", placeholder="Nom du réservant", key="add_nom")
            add_horaire = st.text_input("Horaire", placeholder="15H30 - 18H00", key="add_horaire")
            add_date_str = st.text_input("Date (JJ/MM/AA)", value=ep_date.strftime("%d/%m/%y"), key="add_date")
        with a_col2:
            add_accompte = st.text_input("Accompte (€)", placeholder="100", key="add_accompte")
            add_reste = st.text_input("Reste (€)", placeholder="550", key="add_reste")
            add_prix = st.text_input("Prix loc. (€)", placeholder="650", key="add_prix")
        with a_col3:
            add_caution = st.text_input("Caution", placeholder="Oui", key="add_caution")
            add_salle_select = st.selectbox(
                "Salle",
                options=["Salle principale", "Salle du fond", "Salle du milieu"],
                key="add_salle_select"
            )

        add_submitted = st.form_submit_button("Ajouter la réservation", type="primary", use_container_width=True)

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
                    st.session_state.ep_add_success = f"Réservation ajoutée dans l'onglet '{info}'"
                    st.session_state.ep_add_error = None
                    st.session_state.ep_needs_search = True
                    try:
                        st.session_state.ep_target_date = datetime.strptime(add_date_str, "%d/%m/%y").date()
                    except ValueError:
                        st.session_state.ep_target_date = datetime.now().date()
                    st.session_state.ep_target_salle = add_salle_select
                else:
                    st.session_state.ep_add_error = info
                    st.session_state.ep_add_success = False
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    checker = init_checker()
    if checker is None:
        st.error("Dossier 'salles/' introuvable. Vérifiez l'installation.")
        st.stop()

    render_sidebar(checker)

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin: 0;">Tableau de bord</h1>
        <p style="color: #94a3b8; margin-top: 0.35rem; font-size: 0.95rem;">
            Gestion des salles et réservations — CFPDC
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Gestion de Salle", "Planning & Réservations"])

    with tab1:
        onglet_gestion_salle(checker)

    with tab2:
        onglet_editer_planning(checker)


if __name__ == "__main__":
    main()
