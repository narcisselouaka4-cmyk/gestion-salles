#!/usr/bin/env python3
"""
Application Streamlit — Gestion des Salles CFPDC
UI Professionnelle type Dashboard SaaS
"""

import streamlit as st
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
from datetime import datetime, time, date, timedelta
import os
import time as time_module
import secrets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from checker import SalleChecker
import notifications
import preferences
import keepalive

# ═══════════════════════════════════════════════════════════
# CONFIG PAGE
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CFPDC — Gestion des Salles",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════
# PWA MANIFEST (injection dans le <head>)
# ═══════════════════════════════════════════════════════════
st.markdown("""
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
        meta.content = '#2b5c9e';
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
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# CSS MODERNE — Design System SaaS (Light & Dark compatible)
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --accent: #2b5c9e;
        --accent-strong: #274b7f;
        --accent-soft: rgba(43, 92, 158, 0.10);
        --hairline: rgba(128, 128, 128, 0.16);
        --surface: rgba(128, 128, 128, 0.05);
        --surface-2: rgba(128, 128, 128, 0.08);
        --radius: 12px;
        --radius-sm: 8px;
        --shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    }

    /* Pas de fond forcé — on laisse Streamlit gérer le thème clair/sombre */
    .main .block-container {
        max-width: 1320px;
        padding: 2rem 2.5rem 4rem;
    }

    /* ── Sidebar (fond et couleurs pilotés par le thème via --sb-*) ── */
    section[data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }
    section[data-testid="stSidebar"] .css-1d391kg { background: transparent; }
    .sb-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--sb-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
    }

    /* ── Typographie ── */
    h1 { font-weight: 700; letter-spacing: -0.02em; }
    h2 { font-weight: 700; letter-spacing: -0.015em; }
    h3 { font-weight: 600; letter-spacing: -0.01em; }

    /* ── Responsive (mobile / tablette) ── */
    @media (max-width: 640px) {
        .main .block-container { padding: 1rem 1rem 3rem; }
        /* Sidebar en plein écran sur mobile UNIQUEMENT quand elle est dépliée.
           Repliée (aria-expanded="false"), on laisse Streamlit la masquer. */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 100vw !important;
            width: 100vw !important;
            max-width: 100vw !important;
        }
        section[data-testid="stSidebar"][aria-expanded="true"] > div { width: 100vw !important; }
        .kpi-value { font-size: 1.4rem !important; }
        .form-section, .glass-card, .detail-card { padding: 1.1rem !important; border-radius: 12px !important; }
        [data-testid="stTabs"] [role="tab"] { font-size: 0.8rem !important; padding: 0 0.6rem !important; }
        .res-row { flex-wrap: wrap; gap: 0.5rem !important; }
        .res-time { min-width: auto !important; }
    }

    /* ── KPI Cards ── */
    .kpi-card {
        background: var(--surface-2);
        border: 1px solid var(--hairline);
        border-radius: var(--radius);
        padding: 1.35rem 1.5rem;
        box-shadow: var(--shadow);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 3px;
        background: var(--accent);
    }
    .kpi-card.success::before { background: #10b981; }
    .kpi-card.warning::before { background: #d97706; }
    .kpi-card.danger::before { background: #dc2626; }

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
        background: var(--surface);
        border: 1px solid var(--hairline);
        border-radius: var(--radius);
        padding: 1.75rem;
        box-shadow: var(--shadow);
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
        color: #2b5c9e;
        background: rgba(43,92,158,0.1);
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
        background: var(--surface);
        border: 1px solid var(--hairline);
        border-radius: var(--radius);
        padding: 1.5rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    .detail-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--accent);
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
        color: #2b5c9e;
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
    /* .form-section : les <div> bruts ne peuvent pas envelopper des widgets
       Streamlit (le DOM se referme aussitôt). On neutralise donc la boîte
       fantôme — le contenu est groupé via st.container(border=True). */
    .form-section {
        display: block;
        margin: 0;
        padding: 0;
        border: none;
        background: none;
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
    div[data-testid="stTabContent"],
    div[data-testid="stTabPanel"] {
        padding-top: 1.25rem;
    }
    /* Onglets en « segmented control » : une piste arrondie, l'onglet actif est
       une carte qui flotte dessus (couleurs exactes : thème clair/sombre).
       Sélecteurs par rôle ARIA : valables pour les anciens onglets (baseweb) et
       les nouveaux (react-aria, Streamlit ≥ 1.5x), dont le HTML a changé. */
    [data-testid="stTabs"] [role="tablist"] {
        display: flex;
        width: fit-content;
        max-width: 100%;
        gap: 4px;
        padding: 4px;
        border-radius: 10px;
        background: var(--surface-2);
        flex-wrap: wrap;
    }
    [data-testid="stTabs"] [role="tablist"]::before,
    [data-testid="stTabs"] [role="tablist"]::after { display: none !important; }
    [data-testid="stTabs"] [role="tab"] {
        height: 36px;
        display: inline-flex;
        align-items: center;
        border-radius: 7px;
        background: transparent;
        border: none;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.92rem;
        padding: 0 1.1rem;
        white-space: nowrap;
        transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
        margin: 0;
        cursor: pointer;
    }
    [data-testid="stTabs"] [role="tab"] p {
        margin: 0; font-size: inherit; font-weight: inherit; color: inherit !important;
    }
    [data-testid="stTabs"] [role="tab"]:hover { color: var(--accent); }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--accent) !important;
        font-weight: 700 !important;
    }
    /* Soulignement natif de l'onglet actif : masqué (remplacé par la carte) */
    [data-testid="stTabs"] .react-aria-SelectionIndicator,
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

    /* Buttons override */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: var(--accent);
        border: 1px solid var(--accent);
        border-radius: var(--radius-sm);
        font-weight: 600;
        padding: 0.55rem 1.4rem;
        transition: background 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] > button[kind="primary"] p {
        color: #ffffff !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: var(--accent-strong);
        border-color: var(--accent-strong);
        box-shadow: 0 3px 10px rgba(43, 92, 158, 0.25);
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: var(--radius-sm);
        font-weight: 500;
    }

    /* Bouton-icône discret de bascule de thème */
    .st-key-theme_login button, .st-key-theme_sidebar button {
        min-height: 0 !important;
        width: 36px !important;
        height: 36px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        border: 1px solid var(--hairline) !important;
        background: transparent !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
    }
    .st-key-theme_login button:hover, .st-key-theme_sidebar button:hover {
        background: var(--surface-2) !important;
        border-color: var(--accent) !important;
    }
    .st-key-theme_login button [data-testid="stIconMaterial"] { font-size: 20px; }
    .st-key-theme_sidebar button {
        border-color: rgba(255,255,255,0.16) !important;
        color: #cbd5e1 !important;
    }
    .st-key-theme_sidebar button [data-testid="stIconMaterial"] { font-size: 20px; color: #cbd5e1 !important; }

    /* Form override — évite l'effet « carte dans la carte » (login) */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }

    /* Flou de l'arrière-plan quand une modale (dialog) est ouverte */
    [data-testid="stAppViewContainer"]:has([data-testid="stDialog"]) [data-testid="stMain"],
    [data-testid="stAppViewContainer"]:has([data-testid="stDialog"]) section[data-testid="stSidebar"] {
        filter: blur(3px);
        transition: filter 0.15s ease;
        pointer-events: none;
    }

    /* Expander override */
    div[data-testid="stExpander"] {
        border: 1px solid var(--hairline) !important;
        border-radius: var(--radius) !important;
        background: var(--surface) !important;
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

    /* ── Auth Card ── */
    .auth-card {
        background: var(--surface);
        border: 1px solid var(--hairline);
        border-radius: 16px;
        padding: 2rem 2.25rem;
        box-shadow: var(--shadow);
    }
    .auth-divider {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1.25rem 0;
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .auth-divider::before,
    .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(128,128,128,0.15);
    }

    /* Reduce padding inside auth card inputs */
    .auth-card div[data-testid="stTextInput"] input {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# THÈME CLAIR / SOMBRE (bascule manuelle, déterministe)
# ═══════════════════════════════════════════════════════════
# La portée du thème couvre la zone principale ET les modales (dialogs),
# mais jamais la sidebar (qui reste sombre).
_SC = ':is([data-testid="stMain"],[data-testid="stDialog"])'

_THEME_DARK = f"""
<style>
    [data-testid="stAppViewContainer"] {{ background-color: #0e1117 !important; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stDialog"] > div, [data-testid="stDialog"] [role="dialog"] {{
        background-color: #161b26 !important;
        max-height: 85vh !important;
        overflow-y: auto !important;
    }}
    {_SC} h1, {_SC} h2, {_SC} h3, {_SC} h4, {_SC} h5, {_SC} p,
    {_SC} span, {_SC} label, {_SC} li, {_SC} .stMarkdown {{ color: #e6e9ef; }}
    {_SC} [data-testid="stCaptionContainer"] * {{ color: #9aa4b2 !important; }}
    {_SC} input, {_SC} textarea,
    {_SC} [data-baseweb="input"], {_SC} [data-baseweb="base-input"],
    {_SC} [data-baseweb="select"] > div, {_SC} [data-baseweb="textarea"] {{
        background-color: #1b2130 !important;
        color: #e6e9ef !important;
        border-color: rgba(255,255,255,0.14) !important;
    }}
    {_SC} [data-testid="stVerticalBlockBorderWrapper"] {{ border-color: rgba(255,255,255,0.10) !important; }}
    /* Textes d'exemple (placeholders) : lisibles sur fond sombre */
    {_SC} input::placeholder, {_SC} textarea::placeholder {{
        color: #6b7689 !important; -webkit-text-fill-color: #6b7689 !important; opacity: 1;
    }}
    /* Onglets (sombre) : piste discrète, onglet actif = carte surélevée. */
    {_SC} [data-testid="stTabs"] [role="tablist"] {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.06);
    }}
    {_SC} [data-testid="stTabs"] [role="tab"]:hover {{ color: #e6e9ef; }}
    {_SC} [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background: #263049 !important;
        color: #ffffff !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.35), inset 0 0 0 1px rgba(255,255,255,0.06) !important;
    }}
    /* Champ date (Streamlit ≥ 1.5x) : fond sombre + chiffres clairs. Sans ça,
       le fond reste gris clair et les chiffres héritent du blanc → invisibles. */
    {_SC} [data-testid="stDateInputField"],
    section[data-testid="stSidebar"] [data-testid="stDateInputField"] {{
        background-color: #1b2130 !important;
        border-color: rgba(255,255,255,0.16) !important;
    }}
    {_SC} [data-testid="stDateInputField"] [data-type]:not([data-focused]),
    section[data-testid="stSidebar"] [data-testid="stDateInputField"] [data-type]:not([data-focused]) {{
        color: #e6e9ef !important;
        -webkit-text-fill-color: #e6e9ef !important;
    }}
    {_SC} [data-testid="stDateInputField"] [data-type="literal"],
    section[data-testid="stSidebar"] [data-testid="stDateInputField"] [data-type="literal"] {{
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
    }}
    /* Champs date (anciennes versions de Streamlit) : fond sombre + texte clair */
    {_SC} [data-testid="stDateInput"] div[data-baseweb="input"],
    {_SC} [data-testid="stDateInput"] input,
    section[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] [data-testid="stDateInput"] input {{
        background-color: #1b2130 !important;
        color: #e6e9ef !important;
        -webkit-text-fill-color: #e6e9ef !important;
        border-color: rgba(255,255,255,0.16) !important;
    }}
    {_SC} div[data-testid="stButton"] > button[kind="secondary"],
    {_SC} div[data-testid="stButton"] > button[kind="secondaryFormSubmit"],
    {_SC} button[kind="secondaryFormSubmit"] {{
        background-color: #1b2130 !important;
        color: #e6e9ef !important;
        border-color: rgba(255,255,255,0.16) !important;
    }}
    .kpi-card, .glass-card, .detail-card {{ background: rgba(255,255,255,0.04) !important; }}

    /* ── Sidebar (mode sombre) ── */
    :root {{
        --sb-bg: #0f172a; --sb-text: #f1f5f9; --sb-muted: #94a3b8;
        --sb-hairline: rgba(255,255,255,0.09); --sb-card: rgba(255,255,255,0.05);
    }}
    section[data-testid="stSidebar"] {{ background-color: var(--sb-bg) !important; border-right: 1px solid rgba(255,255,255,0.06); }}
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: #1b2130 !important; color: #e6e9ef !important; border-color: rgba(255,255,255,0.16) !important;
    }}
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] [data-baseweb="input"],
    section[data-testid="stSidebar"] [data-baseweb="base-input"] {{
        background-color: #1b2130 !important; color: #e6e9ef !important; border-color: rgba(255,255,255,0.16) !important;
    }}
    /* Bouton-icône de thème : toujours transparent et rond (prioritaire) */
    .st-key-theme_sidebar button, .st-key-theme_login button {{
        background: transparent !important; border: 1px solid var(--hairline) !important;
        width: 36px !important; height: 36px !important; border-radius: 50% !important; padding: 0 !important;
    }}
    .st-key-theme_sidebar button {{ border-color: rgba(255,255,255,0.16) !important; }}
    .st-key-theme_sidebar button [data-testid="stIconMaterial"],
    .st-key-theme_login button [data-testid="stIconMaterial"] {{ color: #e6e9ef !important; }}
</style>
"""

_THEME_LIGHT = f"""
<style>
    [data-testid="stAppViewContainer"] {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stDialog"] > div, [data-testid="stDialog"] [role="dialog"] {{
        background-color: #ffffff !important;
        max-height: 85vh !important;
        overflow-y: auto !important;
    }}
    {_SC} h1, {_SC} h2, {_SC} h3, {_SC} h4, {_SC} h5, {_SC} p,
    {_SC} span, {_SC} label, {_SC} li, {_SC} .stMarkdown {{ color: #1e293b; }}
    {_SC} [data-testid="stCaptionContainer"] * {{ color: #64748b !important; }}
    {_SC} input, {_SC} textarea,
    {_SC} [data-baseweb="input"], {_SC} [data-baseweb="base-input"],
    {_SC} [data-baseweb="select"] > div, {_SC} [data-baseweb="textarea"] {{
        background-color: #f8fafc !important;
        color: #1e293b !important;
        border-color: rgba(0,0,0,0.12) !important;
    }}
    {_SC} [data-testid="stVerticalBlockBorderWrapper"] {{ border-color: rgba(0,0,0,0.10) !important; }}
    /* Champ date (Streamlit ≥ 1.5x) : fond clair + chiffres sombres. */
    {_SC} [data-testid="stDateInputField"] {{
        background-color: #f8fafc !important;
        border-color: rgba(0,0,0,0.14) !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stDateInputField"] {{
        background-color: #ffffff !important;
        border-color: rgba(0,0,0,0.14) !important;
    }}
    {_SC} [data-testid="stDateInputField"] [data-type]:not([data-focused]),
    section[data-testid="stSidebar"] [data-testid="stDateInputField"] [data-type]:not([data-focused]) {{
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
    }}
    {_SC} [data-testid="stDateInputField"] [data-type="literal"],
    section[data-testid="stSidebar"] [data-testid="stDateInputField"] [data-type="literal"] {{
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }}
    /* Champs date (anciennes versions de Streamlit) : texte sombre forcé. */
    {_SC} [data-testid="stDateInput"] div[data-baseweb="input"],
    {_SC} [data-testid="stDateInput"] input,
    section[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] [data-testid="stDateInput"] input {{
        background-color: #f8fafc !important;
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
        border-color: rgba(0,0,0,0.14) !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] [data-testid="stDateInput"] input {{
        background-color: #ffffff !important;
    }}
    /* Onglets (clair) : piste gris bleuté, onglet actif = carte blanche. */
    {_SC} [data-testid="stTabs"] [role="tablist"] {{ background: #eef2f6 !important; }}
    {_SC} [data-testid="stTabs"] [role="tab"] {{ color: #64748b; }}
    {_SC} [data-testid="stTabs"] [role="tab"]:hover {{ color: #1e293b; }}
    {_SC} [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background: #ffffff !important;
        color: var(--accent) !important;
        box-shadow: 0 1px 2px rgba(15,23,42,0.06), 0 2px 6px rgba(15,23,42,0.09) !important;
    }}

    /* ── Sidebar (mode clair) ── */
    :root {{
        --sb-bg: #f1f5f9; --sb-text: #0f172a; --sb-muted: #64748b;
        --sb-hairline: rgba(0,0,0,0.08); --sb-card: rgba(0,0,0,0.04);
    }}
    section[data-testid="stSidebar"] {{ background-color: var(--sb-bg) !important; border-right: 1px solid rgba(0,0,0,0.08); }}
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: #ffffff !important; color: #1e293b !important; border-color: rgba(0,0,0,0.14) !important;
    }}
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] [data-baseweb="input"],
    section[data-testid="stSidebar"] [data-baseweb="base-input"] {{
        background-color: #ffffff !important; color: #1e293b !important; border-color: rgba(0,0,0,0.14) !important;
    }}
    .st-key-theme_sidebar button, .st-key-theme_login button {{
        background: transparent !important; border: 1px solid rgba(0,0,0,0.14) !important;
        width: 36px !important; height: 36px !important; border-radius: 50% !important; padding: 0 !important;
    }}
    .st-key-theme_sidebar button [data-testid="stIconMaterial"],
    .st-key-theme_login button [data-testid="stIconMaterial"] {{ color: #1e293b !important; }}
</style>
"""


def apply_theme():
    """Applique le thème choisi — appelé à chaque exécution.
    La préférence est mémorisée dans l'URL (?theme=) pour survivre au rafraîchissement."""
    if "ui_theme" not in st.session_state:
        qp = st.query_params.get("theme")
        st.session_state.ui_theme = qp if qp in ("light", "dark") else "light"
    css = _THEME_DARK if st.session_state.ui_theme == "dark" else _THEME_LIGHT
    st.markdown(css, unsafe_allow_html=True)


def theme_toggle(key, location=None):
    """Bascule clair/sombre — bouton icône discret (lune/soleil monochrome)."""
    loc = location or st
    cur = st.session_state.get("ui_theme", "light")
    icon = ":material/dark_mode:" if cur == "light" else ":material/light_mode:"
    tip = "Passer en mode sombre" if cur == "light" else "Passer en mode clair"
    if loc.button("", icon=icon, key=key, help=tip):
        st.session_state.ui_theme = "dark" if cur == "light" else "light"
        st.query_params["theme"] = st.session_state.ui_theme
        st.rerun()


apply_theme()


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
    colors = ['#2b5c9e', '#3f7cc0', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#14b8a6']

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
        ('telephone', 'Téléphone'),
        ('salle', 'Salle'),
        ('added_by', 'Ajouté par'),
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
    added_by = occ.get("added_by", "")

    tags = []
    if prix:
        tags.append(f'<span class="res-tag">{prix}</span>')
    if reste:
        tags.append(f'<span class="res-tag">Reste: {reste}</span>')
    if salle:
        tags.append(f'<span class="res-tag">{salle}</span>')
    if added_by:
        tags.append(f'<span class="res-tag" style="background: rgba(43,92,158,0.12); color: #2b5c9e;">👤 {added_by}</span>')

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
def render_sidebar(checker, authenticator):
    with st.sidebar:
        # Logo + bascule de thème (icône discrète à droite)
        lcol, tcol = st.columns([4, 1], vertical_alignment="center")
        with lcol:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.6rem; padding: 0.25rem 0;">
                <div style="font-size: 1.9rem; line-height: 1;">🕊️</div>
                <div style="line-height: 1.1;">
                    <div style="font-size: 1.15rem; font-weight: 800; color: var(--sb-text); letter-spacing: -0.02em;">CFPDC</div>
                    <div style="font-size: 0.72rem; color: var(--sb-muted); margin-top: 0.15rem;">Gestion des Salles</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with tcol:
            theme_toggle("theme_sidebar")
        st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

        # ── Utilisateur connecté ──
        if st.session_state.get("name"):
            st.markdown(f"""
            <div style="background: rgba(43,92,158,0.15); border-radius: 12px; padding: 0.75rem 1rem; margin-bottom: 1rem; border: 1px solid rgba(43,92,158,0.25);">
                <div style="font-size: 0.7rem; color: var(--sb-muted); text-transform: uppercase; letter-spacing: 0.05em;">Connecté</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: var(--sb-text); margin-top: 0.25rem;">👤 {st.session_state.get("name")}</div>
            </div>
            """, unsafe_allow_html=True)
            if authenticator:
                authenticator.logout(button_name='Déconnexion', location='sidebar')
            st.markdown("<hr style='border-color: var(--sb-hairline); margin: 1rem 0;'>", unsafe_allow_html=True)

        # ── Paramètres rapides (date uniquement) ──
        st.markdown("<div class='sb-label'>Paramètres rapides</div>", unsafe_allow_html=True)

        if "global_date" not in st.session_state:
            st.session_state.global_date = datetime.now().date()

        sidebar_date = st.date_input(
            "Date",
            value=st.session_state.global_date,
            min_value=date(2020, 1, 1),
            max_value=date(2030, 12, 31),
            key="sidebar_date",
            label_visibility="collapsed"
        )
        st.session_state.global_date = sidebar_date

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📅 Aujourd'hui", use_container_width=True):
                st.session_state.global_date = datetime.now().date()
                st.rerun()
        with c2:
            if st.button("📅 Demain", use_container_width=True):
                st.session_state.global_date = (datetime.now() + timedelta(days=1)).date()
                st.rerun()

        st.markdown("<hr style='border-color: var(--sb-hairline); margin: 1.5rem 0;'>", unsafe_allow_html=True)

        # ── Statut des salles — maintenant ──
        st.markdown("<div class='sb-label'>Statut actuel</div>", unsafe_allow_html=True)

        now = datetime.now()
        now_time = now.time()

        for salle_name in SALLES_ORDER_DISPLAY:
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
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid var(--sb-hairline);">
                    <div style="font-size: 0.85rem; color: var(--sb-text); font-weight: 500;">{salle_name}</div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: {status_color};">{status_text}</div>
                        <div style="font-size: 0.65rem; color: var(--sb-muted);">{next_info}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass

        # ── Raccourcis (Google Sheet uniquement) ──
        GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
        if not GOOGLE_SHEET_ID:
            try:
                GOOGLE_SHEET_ID = st.secrets.get("app_config", {}).get("google_sheet_id", "")
            except Exception:
                GOOGLE_SHEET_ID = ""

        if GOOGLE_SHEET_ID:
            st.markdown("<hr style='border-color: var(--sb-hairline); margin: 1.5rem 0;'>", unsafe_allow_html=True)
            st.markdown("<div class='sb-label'>Raccourcis</div>", unsafe_allow_html=True)
            sheet_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit"
            st.markdown(f'''
            <a href="{sheet_url}" target="_blank" style="display: block; text-decoration: none;">
                <div style="background: var(--sb-card); border: 1px solid var(--sb-hairline); border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.85rem; color: var(--sb-text); font-weight: 500;">
                    📊 Ouvrir Google Sheet →
                </div>
            </a>
            ''', unsafe_allow_html=True)

        # ── Réglages ──
        st.markdown("<hr style='border-color: var(--sb-hairline); margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='sb-label'>Réglages</div>", unsafe_allow_html=True)
        if st.button("⚙️ Réglages avancés", use_container_width=True, key="btn_settings"):
            open_settings_dialog(checker, authenticator)


# ═══════════════════════════════════════════════════════════
# ONGLET 1 — DASHBOARD GESTION DE SALLE
# ═══════════════════════════════════════════════════════════
SALLES_ORDER_DISPLAY = ["Salle principale", "Salle du fond", "Salle du milieu"]


def render_salle_section(checker, salle_name, d):
    """Affiche la section d'une salle : statut, timeline et détails des occupations."""
    try:
        result = checker.get_all_occupations(salle_name.lower(), d)
    except Exception as e:
        with st.container(border=True):
            st.markdown(f"**{salle_name}**")
            st.error(f"Erreur de chargement : {e}")
        return

    occupations = result.get("occupations", [])
    overlaps = result.get("overlaps", [])

    total_revenus = 0
    for occ in occupations:
        prix_str = str(occ.get("prix_location", "")).replace("€", "").replace(" ", "")
        try:
            if prix_str:
                total_revenus += float(prix_str)
        except ValueError:
            pass

    occupee = bool(occupations)
    pill_color = "#dc2626" if occupee else "#10b981"
    pill_bg = "rgba(220,38,38,0.12)" if occupee else "rgba(16,185,129,0.12)"
    pill_text = "OCCUPÉE" if occupee else "LIBRE"
    revenus_html = f" · {total_revenus:.0f} €" if total_revenus > 0 else ""

    # Sous-titre (nombre d'occupations) uniquement quand la salle est occupée :
    # quand elle est libre, on allège l'affichage (pas de « 0 occupation(s) »).
    if occupee:
        subtitle_html = (
            f'<div style="font-size:0.82rem;color:#94a3b8;margin:0.2rem 0 0.9rem;">'
            f'{len(occupations)} occupation(s){revenus_html}</div>'
        )
    else:
        subtitle_html = '<div style="margin-bottom:0.9rem;"></div>'

    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;gap:0.75rem;">
            <div style="font-size:1.15rem;font-weight:700;letter-spacing:-0.01em;">{salle_name}</div>
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.05em;color:{pill_color};
                        background:{pill_bg};padding:0.25rem 0.7rem;border-radius:999px;white-space:nowrap;">{pill_text}</div>
        </div>
        {subtitle_html}
        """, unsafe_allow_html=True)

        if overlaps:
            st.warning("⚠️ Conflits d'horaire détectés")
            for overlap in overlaps:
                first = overlap["first"]
                second = overlap["second"]
                st.markdown(
                    f"• **{first['occupant']}** ({first['horaire']}) chevauche "
                    f"**{second['occupant']}** ({second['horaire']})"
                )

        st.markdown(render_timeline(occupations), unsafe_allow_html=True)

        if occupations:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            for occ in occupations:
                st.markdown(render_detail_card(occ), unsafe_allow_html=True)
        # Quand la salle est libre, la timeline affiche déjà
        # « Aucune occupation sur ce créneau » : rien d'autre à ajouter.


def onglet_gestion_salle(checker):
    default_date = st.session_state.get("global_date", datetime.now().date())

    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            d = st.date_input(
                "DATE",
                value=default_date,
                min_value=date(2020, 1, 1),
                max_value=date(2030, 12, 31),
                key="gs_date",
            )
        with c2:
            st.markdown(
                "<div style='font-size:0.8rem;font-weight:600;text-transform:uppercase;"
                "letter-spacing:0.05em;margin-bottom:0.35rem;'>Salles à afficher</div>",
                unsafe_allow_html=True,
            )
            cols = st.columns(3)
            selected = []
            for i, s in enumerate(SALLES_ORDER_DISPLAY):
                with cols[i]:
                    if st.checkbox(s, value=True, key=f"gs_show_{i}"):
                        selected.append(s)

        gs_search_clicked = st.button(
            "🔍 Rechercher", type="primary", use_container_width=True, key="gs_search_btn"
        )

    st.session_state.global_date = d

    # La recherche n'est déclenchée qu'au clic (évite de tout recharger
    # à chaque changement de date ou de case).
    if gs_search_clicked:
        if not selected:
            st.session_state.pop("gs_search", None)
            st.warning("Sélectionnez au moins une salle à afficher.")
        else:
            st.session_state.gs_search = {"date": d, "salles": selected}

    search = st.session_state.get("gs_search")
    if not search:
        st.info("Choisissez une date et les salles à consulter, puis cliquez sur **Rechercher**.")
        return

    sd = search["date"]
    st.markdown(
        f"<div style='margin:0.5rem 0 1rem;color:#94a3b8;font-size:0.9rem;'>"
        f"Disponibilités du <strong>{format_date_fr(sd)}</strong></div>",
        unsafe_allow_html=True,
    )

    # Affichage dans l'ordre hiérarchique : principale → fond → milieu
    for s in SALLES_ORDER_DISPLAY:
        if s in search["salles"]:
            render_salle_section(checker, s, sd)


# ═══════════════════════════════════════════════════════════
# ONGLET 2 — PLANNING & RÉSERVATIONS
# ═══════════════════════════════════════════════════════════
def render_reservations_salle(checker, salle_name, d):
    """Liste et édition des réservations ponctuelles d'une salle pour une date."""
    skey = salle_name.lower().replace(" ", "_")
    try:
        result = checker.get_all_occupations(salle_name.lower(), d)
    except Exception as e:
        with st.container(border=True):
            st.markdown(f"**{salle_name}**")
            st.error(f"Erreur : {e}")
        return

    all_occ = result.get("occupations", [])
    reservations = [o for o in all_occ if o.get("source") == "réservation"]
    overlaps = result.get("overlaps", [])
    unprecise = result.get("unprecise", [])

    with st.container(border=True):
        st.markdown(
            f"<div style='font-size:1.1rem;font-weight:700;margin-bottom:0.5rem;'>{salle_name}</div>",
            unsafe_allow_html=True,
        )

        if overlaps:
            st.warning("⚠️ Conflits d'horaire détectés")
            for ov in overlaps:
                st.markdown(
                    f"• **{ov['first']['occupant']}** ({ov['first']['horaire']}) chevauche "
                    f"**{ov['second']['occupant']}** ({ov['second']['horaire']})"
                )
        if unprecise:
            st.warning("⚠️ Horaires non précisés — certains créneaux n'ont pas d'heure claire")
            for u in unprecise:
                st.markdown(f"• **{u['occupant']}** : {u['horaire']}")

        if not reservations:
            st.info(f"Aucune réservation ponctuelle le {format_date_fr(d)}.")
            return

        st.markdown(
            f"<div style='font-size:0.8rem;font-weight:600;color:#94a3b8;text-transform:uppercase;"
            f"letter-spacing:0.05em;margin-bottom:0.5rem;'>{len(reservations)} réservation(s)</div>",
            unsafe_allow_html=True,
        )

        for idx, occ in enumerate(reservations):
            st.markdown(render_reservation_row(occ, idx), unsafe_allow_html=True)
            with st.expander("Modifier"):
                with st.form(key=f"ep_edit_{skey}_{idx}", border=False):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        new_nom = st.text_input("Nom", value=occ.get('occupant', ''), key=f"ep_nom_{skey}_{idx}")
                        new_horaire = st.text_input("Horaire", value=occ.get('horaire', ''), placeholder="15H30 - 18H00", key=f"ep_horaire_{skey}_{idx}")
                        new_date_str = st.text_input("Date (JJ/MM/AA)", value=d.strftime("%d/%m/%y"), key=f"ep_datestr_{skey}_{idx}")
                    with ec2:
                        new_accompte = st.text_input("Accompte (€)", value=occ.get('accompte', ''), key=f"ep_acc_{skey}_{idx}")
                        new_reste = st.text_input("Reste (€)", value=occ.get('reste_a_payer', ''), key=f"ep_reste_{skey}_{idx}")
                        new_prix = st.text_input("Prix loc. (€)", value=occ.get('prix_location', ''), key=f"ep_prix_{skey}_{idx}")
                    with ec3:
                        new_caution = st.text_input("Caution", value=occ.get('caution_menage', ''), key=f"ep_cau_{skey}_{idx}")
                        new_telephone = st.text_input("Téléphone", value=occ.get('telephone', ''), key=f"ep_tel_{skey}_{idx}")
                        new_salle_occ = st.text_input("Salle", value=occ.get('salle', ''), key=f"ep_so_{skey}_{idx}")

                    b1, b2, b3, b4 = st.columns([2, 1, 1, 1])
                    with b1:
                        submitted = st.form_submit_button("Sauvegarder", type="primary", use_container_width=True)
                    with b2:
                        clear_submitted = st.form_submit_button("Effacer infos", use_container_width=True)
                    with b4:
                        delete_submitted = st.form_submit_button("Supprimer", use_container_width=True)

                    if submitted:
                        old_occupant = occ.get('occupant', '')
                        update_data = {}
                        if new_nom != old_occupant:
                            update_data['occupant'] = new_nom if new_nom else "Non renseigné"
                        if new_horaire != occ.get('horaire', ''):
                            update_data['horaire'] = new_horaire
                        if new_date_str != d.strftime("%d/%m/%y"):
                            update_data['date'] = new_date_str
                        if new_salle_occ != occ.get('salle', ''):
                            update_data['salle'] = new_salle_occ
                        update_data['accompte'] = f"{new_accompte}€" if new_accompte and '€' not in new_accompte else (new_accompte if new_accompte else "")
                        update_data['reste_a_payer'] = f"{new_reste}€" if new_reste and '€' not in new_reste else (new_reste if new_reste else "")
                        update_data['prix_location'] = f"{new_prix}€" if new_prix and '€' not in new_prix else (new_prix if new_prix else "")
                        update_data['caution_menage'] = new_caution if new_caution else ""
                        update_data['telephone'] = new_telephone if new_telephone else ""
                        update_data['salle_occupation'] = new_salle_occ if new_salle_occ else ""
                        success, error = checker.update_reservation_google(salle_name.lower(), d, old_occupant.strip(), update_data)
                        if success:
                            st.session_state.ep_edit_success = "Modifications sauvegardées"
                        else:
                            st.session_state.ep_edit_error = error
                        st.rerun()

                    if clear_submitted:
                        old_occupant = occ.get('occupant', '')
                        success, error = checker.update_reservation_google(
                            salle_name.lower(), d, old_occupant.strip(),
                            {'accompte': "", 'reste_a_payer': "", 'prix_location': "", 'caution_menage': "", 'telephone': "", 'salle_occupation': ""}
                        )
                        if success:
                            st.session_state.ep_edit_success = "Informations effacées"
                        else:
                            st.session_state.ep_edit_error = error
                        st.rerun()

                    if delete_submitted:
                        old_occupant = occ.get('occupant', '')
                        success, error = checker.delete_reservation_google(salle_name.lower(), d, old_occupant.strip())
                        if success:
                            st.session_state.ep_edit_success = "Réservation supprimée"
                        else:
                            st.session_state.ep_edit_error = error
                        st.rerun()


def onglet_editer_planning(checker):
    default_date = st.session_state.get("global_date", datetime.now().date())

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.4rem;">Planning de Réservation</h2>
        <p style="color: #94a3b8; margin-top: 0.25rem; font-size: 0.9rem;">Gérez les réservations ponctuelles du Google Sheet</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            ep_date = st.date_input(
                "DATE",
                value=default_date,
                min_value=date(2020, 1, 1),
                max_value=date(2030, 12, 31),
                key="ep_date"
            )
        with c2:
            st.markdown(
                "<div style='font-size:0.8rem;font-weight:600;text-transform:uppercase;"
                "letter-spacing:0.05em;margin-bottom:0.35rem;'>Salles à afficher</div>",
                unsafe_allow_html=True,
            )
            cols = st.columns(3)
            ep_selected = []
            for i, s in enumerate(SALLES_ORDER_DISPLAY):
                with cols[i]:
                    if st.checkbox(s, value=True, key=f"ep_show_{i}"):
                        ep_selected.append(s)

        ep_search_clicked = st.button(
            "🔍 Rechercher", type="primary", use_container_width=True, key="ep_search_btn"
        )

    st.session_state.global_date = ep_date

    if ep_search_clicked:
        if not ep_selected:
            st.session_state.pop("ep_search", None)
            st.warning("Sélectionnez au moins une salle à afficher.")
        else:
            st.session_state.ep_search = {"date": ep_date, "salles": ep_selected}

    if st.session_state.get("ep_edit_success"):
        st.success(st.session_state.ep_edit_success)
        st.session_state.ep_edit_success = None
        st.session_state.ep_edit_error = None
    if st.session_state.get("ep_edit_error"):
        st.error(f"Erreur : {st.session_state.ep_edit_error}")
        st.session_state.ep_edit_error = None
        st.session_state.ep_edit_success = None

    ep_search = st.session_state.get("ep_search")
    if ep_search:
        for s in SALLES_ORDER_DISPLAY:
            if s in ep_search["salles"]:
                render_reservations_salle(checker, s, ep_search["date"])
    else:
        st.info("Choisissez une date et les salles à gérer, puis cliquez sur **Rechercher**.")

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
    if st.session_state.get("ep_add_warning"):
        st.warning(st.session_state.ep_add_warning)
        st.session_state.ep_add_warning = None

    @st.dialog("Ajouter une nouvelle réservation", width="large")
    def _dialog_ajout_reservation():
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
                add_telephone = st.text_input("Téléphone", placeholder="06 12 34 56 78", key="add_telephone")
                add_salle_select = st.selectbox(
                    "Salle",
                    options=["Salle principale", "Salle du fond", "Salle du milieu"],
                    key="add_salle_select"
                )

            add_submitted = st.form_submit_button("Ajouter la réservation", type="primary", use_container_width=True)

        if add_submitted:
            if not add_nom:
                st.error("Le nom est obligatoire.")
            elif not add_horaire:
                st.error("L'horaire est obligatoire.")
            elif not add_date_str:
                st.error("La date est obligatoire.")
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
                    'telephone': add_telephone if add_telephone else "",
                    'salle_occupation': "",
                    'added_by': st.session_state.get("username", "Inconnu"),
                }

                try:
                    parsed_date = datetime.strptime(add_date_str, "%d/%m/%y").date()
                except ValueError:
                    try:
                        parsed_date = datetime.strptime(add_date_str, "%d/%m/%Y").date()
                    except ValueError:
                        parsed_date = datetime.now().date()

                # Détecter les conflits AVANT l'ajout (sinon la nouvelle
                # réservation se retrouverait comparée à elle-même).
                try:
                    conflits = checker.check_reservation_conflict(
                        add_salle_select.lower(), parsed_date, add_horaire
                    )
                except Exception as e:
                    print(f"[App] Erreur vérification conflit: {e}")
                    conflits = []

                success, info = checker.add_reservation_google(new_data)
                if success:
                    st.session_state.ep_add_success = f"Réservation ajoutée dans l'onglet '{info}'"
                    st.session_state.ep_add_error = None
                    # Recentrer l'affichage sur la date/salle de l'ajout
                    prev = st.session_state.get("ep_search") or {}
                    salles = list(prev.get("salles") or SALLES_ORDER_DISPLAY)
                    if add_salle_select not in salles:
                        salles.append(add_salle_select)
                    st.session_state.ep_search = {"date": parsed_date, "salles": salles}

                    # ── Notifications ──
                    # (b) Alerte doublon / chevauchement (créneaux précis OU imprécis)
                    if conflits:
                        for c in conflits:
                            try:
                                notifications.envoyer_alerte_doublon(checker, new_data, c)
                            except Exception as e:
                                print(f"[App] Erreur alerte doublon: {e}")
                        st.session_state.ep_add_warning = (
                            f"⚠️ Conflit détecté avec {len(conflits)} occupation(s) existante(s) "
                            f"sur ce créneau — une alerte a été envoyée par email."
                        )

                    # (c) Notification nouvel ajout
                    try:
                        notifications.envoyer_nouvel_ajout(checker, new_data)
                    except Exception as e:
                        print(f"[App] Erreur notification nouvel ajout: {e}")

                    st.rerun()  # ferme la modale et affiche le message de succès
                else:
                    st.error(f"Erreur : {info}")

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("➕ Ajouter une nouvelle réservation", type="primary", use_container_width=True, key="ep_open_add"):
        _dialog_ajout_reservation()


def onglet_notifications(checker):
    """Onglet pour configurer les notifications par email."""
    import notifications

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.4rem;">Notifications</h2>
        <p style="color: #94a3b8; margin-top: 0.25rem; font-size: 0.9rem;">Recevez les alertes et récapitulatifs par email</p>
    </div>
    """, unsafe_allow_html=True)

    # Statut des notifications
    active = notifications.notifications_active()
    if active:
        st.success("✅ Les notifications email sont activées.")
    else:
        st.warning("⚠️ Les notifications email sont désactivées (SMTP non configuré). Contactez l'administrateur.")

    # ── Mon email ──
    st.markdown("### 📧 Mon email de notification")
    st.markdown("<div class='form-section'>", unsafe_allow_html=True)
    current_user = st.session_state.get("username", "")
    current_email = checker.get_user_email(current_user)
    st.markdown(f"**Compte :** {current_user}")

    with st.form(key="notif_email_form", border=False):
        new_email = st.text_input("Votre email", value=current_email, placeholder="ex: jean.dupont@gmail.com")
        email_submitted = st.form_submit_button("Enregistrer mon email", type="primary", use_container_width=True)

        if email_submitted:
            if new_email and "@" not in new_email:
                st.error("❌ Email invalide.")
            else:
                success, info = checker.update_user_email_google(current_user, new_email.strip())
                if success:
                    st.success(f"✅ {info}")
                else:
                    st.error(f"❌ {info}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Test d'envoi ──
    st.markdown("### 🧪 Tester l'envoi")
    st.markdown("<div class='form-section'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📨 Envoyer le récap de demain", use_container_width=True):
            if not active:
                st.error("Notifications désactivées.")
            else:
                with st.spinner("Envoi en cours..."):
                    success, info = notifications.envoyer_recap_quotidien(checker)
                    if success:
                        st.success(f"✅ {info}")
                    else:
                        st.error(f"❌ {info}")
    with col2:
        if st.button("🔔 Envoyer un email de test", use_container_width=True):
            if not active:
                st.error("Notifications désactivées.")
            else:
                emails = preferences.get_subscribed_emails(checker)
                if not emails:
                    st.warning("Aucun email abonné. Renseignez votre email dans les Réglages (⚙️) et abonnez-vous.")
                else:
                    from datetime import date as _date
                    resa_test = {
                        "salle": "Salle de test",
                        "occupant": "Test",
                        "date": _date.today().strftime("%d/%m/%Y"),
                        "horaire": "14H00 - 16H00",
                        "telephone": "",
                        "accompte": "",
                        "added_by": current_user,
                    }
                    with st.spinner("Envoi..."):
                        success, error = notifications.envoyer_nouvel_ajout(checker, resa_test)
                        if success:
                            st.success(f"✅ Email de test envoyé à : {', '.join(emails)}")
                        else:
                            st.error(f"❌ {error}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Infos sur les destinataires (admin) ──
    admin_user = os.environ.get("AUTH_USER", "")
    if current_user == admin_user:
        st.markdown("### 👥 Destinataires enregistrés")
        users = checker.get_users_google()
        emails_list = [(u, (d.get("email") or "").strip()) for u, d in users.items()]
        if emails_list:
            for u, em in emails_list:
                badge = "✅" if em and "@" in em else "❌"
                label = em if em else "*(pas d'email)*"
                st.markdown(f"{badge} **{u}** — {label}")
        else:
            st.info("Aucun utilisateur enregistré.")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 — GESTION DES UTILISATEURS
# ═══════════════════════════════════════════════════════════
def onglet_utilisateurs(checker, authenticator):
    """Onglet pour créer des comptes, modifier les mots de passe, et supprimer (admin)."""

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.4rem;">Gestion des Utilisateurs</h2>
        <p style="color: #94a3b8; margin-top: 0.25rem; font-size: 0.9rem;">Modifier votre mot de passe ou gérer les comptes (admin)</p>
    </div>
    """, unsafe_allow_html=True)

    current_user = st.session_state.get("username", "")
    admin_user = os.environ.get("AUTH_USER", "")
    is_admin = current_user == admin_user

    # ── Modifier un mot de passe ──
    st.markdown("### 🔑 Modifier un mot de passe")
    st.markdown("<div class='form-section'>", unsafe_allow_html=True)

    if is_admin:
        # Admin : peut modifier n'importe quel compte sans vérifier l'ancien
        with st.form(key="user_pwd_form", border=False):
            c1, c2 = st.columns(2)
            with c1:
                target_user = st.text_input("Username à modifier", placeholder="ex: narcisse")
            with c2:
                new_pwd = st.text_input("Nouveau mot de passe", type="password")
                new_pwd_confirm = st.text_input("Confirmer nouveau mot de passe", type="password")

            pwd_submitted = st.form_submit_button("Mettre à jour", type="primary", use_container_width=True)

            if pwd_submitted:
                if not target_user or not new_pwd:
                    st.error("Le username et le nouveau mot de passe sont obligatoires.")
                elif new_pwd != new_pwd_confirm:
                    st.error("Les mots de passe ne correspondent pas.")
                elif len(new_pwd) < 4:
                    st.error("Le mot de passe doit faire au moins 4 caractères.")
                else:
                    all_users = checker.get_users_google()
                    env_user = os.environ.get("AUTH_USER", "")

                    if target_user.strip() == env_user:
                        st.error("❌ Impossible de modifier le compte administrateur ici. Contactez l'administrateur.")
                    elif target_user.strip() not in all_users:
                        st.error(f"❌ Utilisateur '{target_user}' non trouvé.")
                    else:
                        h = stauth.Hasher()
                        new_hash = h.hash(new_pwd)
                        success, info = checker.update_user_password_google(target_user.strip(), new_hash)
                        if success:
                            st.success(f"✅ {info}")
                            st.rerun()
                        else:
                            st.error(f"❌ {info}")
    else:
        # Utilisateur normal : modifier SON propre mot de passe (avec vérification ancien)
        with st.form(key="user_pwd_form", border=False):
            st.markdown(f"**Username :** {current_user}")
            c1, c2 = st.columns(2)
            with c1:
                old_pwd = st.text_input("Ancien mot de passe", type="password")
                new_pwd = st.text_input("Nouveau mot de passe", type="password")
            with c2:
                new_pwd_confirm = st.text_input("Confirmer nouveau mot de passe", type="password")

            pwd_submitted = st.form_submit_button("Mettre à jour", type="primary", use_container_width=True)

            if pwd_submitted:
                if not old_pwd or not new_pwd:
                    st.error("L'ancien et le nouveau mot de passe sont obligatoires.")
                elif new_pwd != new_pwd_confirm:
                    st.error("Les mots de passe ne correspondent pas.")
                elif len(new_pwd) < 4:
                    st.error("Le mot de passe doit faire au moins 4 caractères.")
                else:
                    all_users = checker.get_users_google()
                    if current_user not in all_users:
                        st.error("❌ Votre compte n'a pas été trouvé.")
                    else:
                        h = stauth.Hasher()
                        if not h.check_pw(old_pwd, all_users[current_user]["password"]):
                            st.error("❌ Ancien mot de passe incorrect.")
                        else:
                            new_hash = h.hash(new_pwd)
                            success, info = checker.update_user_password_google(current_user, new_hash)
                            if success:
                                st.success(f"✅ {info}")
                                st.rerun()
                            else:
                                st.error(f"❌ {info}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Admin : Supprimer un compte ──
    if is_admin:
        st.markdown("### 🗑️ Supprimer un compte")
        st.markdown("<div class='form-section'>", unsafe_allow_html=True)

        with st.form(key="user_delete_form", border=False):
            delete_user = st.text_input("Username à supprimer", placeholder="ex: ancien_compte")
            confirm = st.checkbox("Je confirme la suppression définitive")

            delete_submitted = st.form_submit_button("Supprimer le compte", type="primary", use_container_width=True)

            if delete_submitted:
                if not delete_user:
                    st.error("Le username est obligatoire.")
                elif not confirm:
                    st.error("Veuillez cocher la case de confirmation.")
                else:
                    env_user = os.environ.get("AUTH_USER", "")
                    if delete_user.strip() == env_user:
                        st.error("❌ Impossible de supprimer le compte administrateur.")
                    else:
                        success, info = checker.delete_user_google(delete_user.strip())
                        if success:
                            st.success(f"✅ {info}")
                            st.rerun()
                        else:
                            st.error(f"❌ {info}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Liste des utilisateurs ──
    st.markdown("### 👥 Utilisateurs enregistrés")
    users = checker.get_users_google()
    if users:
        for u, data in users.items():
            st.markdown(f"""
            <div class="res-row" style="padding: 0.75rem 1.25rem;">
                <div class="res-name" style="font-weight: 700;">{u}</div>
                <div class="res-tag">{data.get('name', u)}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucun utilisateur trouvé dans le Google Sheet (onglet 'Utilisateurs').")


# ═══════════════════════════════════════════════════════════
# DIALOG DES RÉGLAGES (rouage ⚙️)
# ═══════════════════════════════════════════════════════════
def save_user_email(checker, username, email):
    """
    Enregistre l'email de l'utilisateur de façon PERSISTANTE (Google Sheet) et
    en cache local. Un seul email pour tout : notifications ET vérification.
    Retourne (ok, message).
    """
    email = (email or "").strip()
    preferences.set_user_email(username, email)  # cache local
    try:
        ok, info = checker.update_user_email_google(username, email)
    except Exception as e:
        ok, info = False, str(e)
    if ok:
        return True, "Email enregistré."
    return False, f"Email gardé pour cette session, mais non enregistré durablement ({info})."


def collapse_sidebar_on_mobile():
    """
    Sur mobile, Streamlit ouvre la barre latérale au chargement malgré
    `initial_sidebar_state='collapsed'`. On la replie une seule fois par visite,
    uniquement sur petit écran (desktop non affecté).
    """
    components.html(
        """
        <script>
        (function(){
          try {
            var win = window.parent, doc = win.document;
            if (win.__cfpdcSidebarInit) return;
            if (win.innerWidth > 640) return;
            win.__cfpdcSidebarInit = true;
            function tryCollapse(n){
              var sb = doc.querySelector('section[data-testid="stSidebar"]');
              if (!sb){ if(n<25) setTimeout(function(){tryCollapse(n+1)},150); return; }
              if (sb.getAttribute('aria-expanded') !== 'true') return;
              var btn = doc.querySelector('[data-testid="stSidebarCollapseButton"] button')
                     || doc.querySelector('[data-testid="stSidebarCollapseButton"]')
                     || doc.querySelector('button[aria-label="Close sidebar"]');
              if (btn){ btn.click(); return; }
              if (n<25) setTimeout(function(){tryCollapse(n+1)},150);
            }
            setTimeout(function(){ tryCollapse(0); }, 250);
          } catch(e){}
        })();
        </script>
        """,
        height=0,
    )


def render_email_prompt(checker):
    """
    Invite (via une modale) les utilisateurs sans email à en renseigner un,
    pour pouvoir récupérer leur mot de passe par code de vérification.

    Affichée UNE SEULE FOIS par utilisateur : dès qu'elle apparaît, on mémorise
    (en session, en préférence locale ET dans le Google Sheet, colonne
    'email_prompt_vu') qu'elle a été présentée. Elle ne réapparaît donc plus —
    que l'utilisateur la referme avec la croix, recharge l'appli, se reconnecte,
    lance une recherche, change de thème ou que l'appli soit redéployée.
    """
    if st.session_state.get("email_prompt_done"):
        return False
    current_user = st.session_state.get("username", "")
    if not current_user:
        return False
    try:
        email = preferences.get_user_email(current_user, checker)
    except Exception:
        email = ""
    # A un email OU a déjà été invité → ne plus demander. Le « déjà vu » est lu
    # en local puis dans le Google Sheet : le fichier local est effacé à chaque
    # redéploiement Render, le Sheet non.
    dismissed = bool(preferences.get_pref(current_user, "email_prompt_dismissed", False))
    if not email and not dismissed:
        try:
            dismissed = checker.get_email_prompt_vu(current_user)
        except Exception:
            dismissed = False
    if email or dismissed:
        st.session_state.email_prompt_done = True
        return False

    # On marque TOUT DE SUITE l'invite comme présentée (session, local, Sheet),
    # avant même d'ouvrir la modale. Ainsi, quelle que soit la façon dont
    # l'utilisateur la referme (croix, Échap, clic en dehors, bouton), elle ne
    # se rouvrira jamais — même après un redéploiement.
    st.session_state.email_prompt_done = True
    try:
        preferences.set_pref(current_user, "email_prompt_dismissed", True)
    except Exception:
        pass
    try:
        checker.set_email_prompt_vu(current_user)
    except Exception:
        pass

    @st.dialog("📧 Ajoutez votre adresse email")
    def _d():
        st.markdown(
            "Aucune adresse email n'est associée à votre compte.\n\n"
            "Elle est **nécessaire** pour réinitialiser votre mot de passe en cas d'oubli "
            "(vous recevrez un **code de vérification** par email)."
        )
        new_email = st.text_input("Votre email", placeholder="ex: jean.dupont@gmail.com", key="prompt_email_input")
        c1, c2 = st.columns([2, 1])
        with c1:
            if st.button("💾 Enregistrer mon email", type="primary", use_container_width=True):
                if not new_email or "@" not in new_email:
                    st.error("Veuillez saisir une adresse email valide.")
                else:
                    ok, msg = save_user_email(checker, current_user, new_email.strip())
                    st.session_state.email_prompt_done = True
                    (st.success if ok else st.warning)(msg)
                    st.rerun()
        with c2:
            if st.button("Annuler", use_container_width=True):
                preferences.set_pref(current_user, "email_prompt_dismissed", True)
                st.session_state.email_prompt_done = True
                st.rerun()
        st.caption("Vous pourrez l'ajouter plus tard dans ⚙️ Réglages.")

    _d()
    return True


def open_settings_dialog(checker, authenticator):
    """Ouvre le dialog des réglages avancés (appelé au clic sur le bouton rouage).
    Appel direct (pas de flag persistant) : la croix ferme réellement le dialog."""
    current_user = st.session_state.get("username", "")
    admin_user = os.environ.get("AUTH_USER", "")
    is_admin = current_user == admin_user

    @st.dialog("⚙️ Réglages avancés", width="large")
    def _dialog():
        st.markdown(f"**Compte connecté :** {current_user}")
        st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)

        # ── Section Notifications (repliable) ──
        with st.expander("📧 Notifications par email", expanded=False):
            current_email = preferences.get_user_email(current_user, checker)
            subscribed = preferences.is_subscribed(current_user)

            new_email = st.text_input("Votre email", value=current_email, placeholder="ex: jean.dupont@gmail.com", key="settings_email")
            st.caption("Un seul email pour tout : notifications **et** récupération du mot de passe.")

            if st.button("💾 Enregistrer mon email", use_container_width=True):
                if new_email and "@" not in new_email:
                    st.error("❌ Email invalide.")
                else:
                    ok, msg = save_user_email(checker, current_user, new_email.strip())
                    (st.success if ok else st.warning)(msg)
                    st.rerun()

            # ── Option avancée : email de vérification distinct ──
            cur_verif_raw = (preferences.get_pref(current_user, "verif_email", "") or "").strip()
            with st.expander("Options avancées — email de récupération distinct", expanded=bool(cur_verif_raw)):
                st.caption("Par défaut, la récupération du mot de passe utilise votre email ci-dessus. "
                           "Vous pouvez ici définir un email différent, réservé à la récupération.")
                verif_email = st.text_input(
                    "Email de récupération (facultatif)",
                    value=cur_verif_raw,
                    placeholder="Laisser vide pour utiliser l'email principal",
                    key="settings_verif_email",
                )
                if st.button("💾 Enregistrer l'email de récupération", use_container_width=True, key="settings_save_verif"):
                    if verif_email and "@" not in verif_email:
                        st.error("❌ Email invalide.")
                    else:
                        preferences.set_verif_email(current_user, verif_email.strip())
                        if verif_email.strip():
                            st.success("✅ Email de récupération distinct enregistré.")
                        else:
                            st.success("✅ Récupération remise sur l'email principal.")
                        st.rerun()

            st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)

            # Sans email → forcément désabonné (impossible de recevoir).
            has_email = bool((current_email or "").strip())
            subscribed = has_email and subscribed

            if not has_email:
                st.markdown("**Statut :** ❌ Désabonné")
                st.caption("Renseignez votre email ci-dessus pour recevoir les notifications.")
            elif subscribed:
                st.markdown("**Statut :** ✅ Abonné")
                if st.button("🔕 Me désabonner des notifications", use_container_width=True):
                    preferences.set_subscribed(current_user, False)
                    st.success("Vous êtes maintenant désabonné des notifications.")
                    st.rerun()
            else:
                st.markdown("**Statut :** ❌ Désabonné")
                if st.button("🔔 Me réabonner aux notifications", type="primary", use_container_width=True):
                    preferences.set_subscribed(current_user, True)
                    st.success("✅ Vous êtes maintenant abonné aux notifications.")
                    st.rerun()

            # ── Préférences (heure + jours + salles) ──
            if subscribed:
                st.markdown("<div style='margin: 1rem 0 0.5rem;'></div>", unsafe_allow_html=True)
                st.markdown("**Mes préférences de notification**")
                st.caption("La veille au soir, vous recevez la liste des salles occupées le lendemain. Rien n'est envoyé si tout est libre.")

                jours_labels = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
                salles_labels = {
                    "salle principale": "Salle principale",
                    "salle du fond": "Salle du fond",
                    "salle du milieu": "Salle du milieu",
                }

                cur_jours = preferences.get_notif_jours(current_user)
                cur_salles = preferences.get_notif_salles(current_user)
                cur_heure = preferences.get_notif_heure(current_user)

                with st.form(key="settings_notif_prefs_form", border=False):
                    hcol, _ = st.columns([1, 1])
                    with hcol:
                        sel_heure = st.selectbox(
                            "Heure de réception",
                            options=list(range(24)),
                            index=cur_heure,
                            format_func=lambda h: f"{h:02d}h00",
                            help="Heure à laquelle vous recevez le récap, la veille.",
                        )
                    sel_jours_labels = st.multiselect(
                        "Jours de réception",
                        options=jours_labels,
                        default=[jours_labels[j] for j in cur_jours],
                        help="Décochez un jour pour ne pas recevoir le récap ce jour-là.",
                    )
                    st.markdown("<div style='font-size:0.8rem;font-weight:600;margin:0.4rem 0 0.2rem;'>Salles suivies</div>", unsafe_allow_html=True)
                    sel_salles = []
                    cols = st.columns(3)
                    for i, (skey, slabel) in enumerate(salles_labels.items()):
                        with cols[i]:
                            if st.checkbox(slabel, value=(skey in cur_salles), key=f"notif_salle_{skey}"):
                                sel_salles.append(skey)

                    prefs_submitted = st.form_submit_button("💾 Enregistrer mes préférences", use_container_width=True)
                    if prefs_submitted:
                        sel_jours = [jours_labels.index(l) for l in sel_jours_labels]
                        preferences.set_notif_heure(current_user, sel_heure)
                        preferences.set_notif_jours(current_user, sel_jours)
                        preferences.set_notif_salles(current_user, sel_salles)
                        if not sel_jours or not sel_salles:
                            st.warning("⚠️ Préférences enregistrées, mais aucun récap ne sera envoyé (aucun jour ou aucune salle sélectionné).")
                        else:
                            st.success("✅ Préférences enregistrées.")

            # Test d'envoi (admin seulement)
            if is_admin:
                st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)
                st.markdown("#### 🧪 Test d'envoi")
                import notifications as notif_mod
                if st.button("📨 Envoyer le récap de demain"):
                    if not notif_mod.notifications_active():
                        st.error("Notifications désactivées (SMTP non configuré).")
                    else:
                        with st.spinner("Envoi..."):
                            success, info = notif_mod.envoyer_recap_quotidien(checker)
                            if success:
                                st.success(f"✅ {info}")
                            else:
                                st.error(f"❌ {info}")

        # ── Section Mot de passe (repliable, sans ancien mot de passe) ──
        with st.expander("🔑 Modifier mon mot de passe", expanded=False):
            with st.form(key="settings_pwd_form", border=False):
                new_pwd = st.text_input("Nouveau mot de passe", type="password", key="settings_new_pwd")
                new_pwd_confirm = st.text_input("Confirmer le mot de passe", type="password", key="settings_new_pwd_confirm")

                pwd_submitted = st.form_submit_button("Mettre à jour", type="primary", use_container_width=True)

                if pwd_submitted:
                    if not new_pwd:
                        st.error("Veuillez saisir un nouveau mot de passe.")
                    elif new_pwd != new_pwd_confirm:
                        st.error("Les mots de passe ne correspondent pas.")
                    elif len(new_pwd) < 4:
                        st.error("Le mot de passe doit faire au moins 4 caractères.")
                    else:
                        h = stauth.Hasher()
                        new_hash = h.hash(new_pwd)
                        success, info = checker.update_user_password_google(current_user, new_hash)
                        if success:
                            st.success(f"✅ {info}")
                        else:
                            st.error(f"❌ {info}")

        # ── Section Admin : gestion des comptes ──
        if is_admin:
            st.markdown("### 👥 Gestion des comptes (admin)")
            st.markdown("<div class='form-section'>", unsafe_allow_html=True)

            with st.form(key="settings_admin_pwd_form", border=False):
                target_user = st.text_input("Username à modifier", placeholder="ex: narcisse", key="settings_target_user")
                admin_new_pwd = st.text_input("Nouveau mot de passe", type="password", key="settings_admin_new_pwd")

                admin_pwd_submitted = st.form_submit_button("Mettre à jour le mot de passe", type="primary", use_container_width=True)

                if admin_pwd_submitted:
                    if not target_user or not admin_new_pwd:
                        st.error("Le username et le nouveau mot de passe sont obligatoires.")
                    elif len(admin_new_pwd) < 4:
                        st.error("Le mot de passe doit faire au moins 4 caractères.")
                    elif target_user.strip() == admin_user:
                        st.error("❌ Impossible de modifier le compte administrateur ici.")
                    else:
                        all_users = checker.get_users_google()
                        if target_user.strip() not in all_users:
                            st.error(f"❌ Utilisateur '{target_user}' non trouvé.")
                        else:
                            h = stauth.Hasher()
                            new_hash = h.hash(admin_new_pwd)
                            success, info = checker.update_user_password_google(target_user.strip(), new_hash)
                            if success:
                                st.success(f"✅ {info}")
                            else:
                                st.error(f"❌ {info}")

            st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)

            with st.form(key="settings_delete_form", border=False):
                delete_user = st.text_input("Username à supprimer", placeholder="ex: ancien_compte", key="settings_delete_user")
                confirm = st.checkbox("Je confirme la suppression définitive")

                delete_submitted = st.form_submit_button("Supprimer le compte", use_container_width=True)

                if delete_submitted:
                    if not delete_user:
                        st.error("Le username est obligatoire.")
                    elif not confirm:
                        st.error("Veuillez cocher la case de confirmation.")
                    elif delete_user.strip() == admin_user:
                        st.error("❌ Impossible de supprimer le compte administrateur.")
                    else:
                        success, info = checker.delete_user_google(delete_user.strip())
                        if success:
                            st.success(f"✅ {info}")
                        else:
                            st.error(f"❌ {info}")

            st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)
            st.markdown("#### Utilisateurs enregistrés")
            users = checker.get_users_google()
            if users:
                for u, data in users.items():
                    st.markdown(f"""
                    <div class="res-row" style="padding: 0.5rem 1rem;">
                        <div class="res-name" style="font-weight: 700;">{u}</div>
                        <div class="res-tag">{data.get('name', u)}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun utilisateur trouvé.")

            st.markdown("</div>", unsafe_allow_html=True)

        # Bouton fermer
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        if st.button("Fermer", use_container_width=True):
            st.rerun()

    _dialog()


# ═══════════════════════════════════════════════════════════
# FLUX MOT DE PASSE OUBLIÉ (code de vérification par email)
# ═══════════════════════════════════════════════════════════
RESET_CODE_TTL = 600  # secondes (10 minutes)


def _clear_reset_state():
    """Nettoie l'état du flux de réinitialisation."""
    for k in ("reset_step", "reset_code", "reset_code_exp",
              "reset_target_user", "reset_target_email", "reset_target_name"):
        st.session_state.pop(k, None)


def _finaliser_connexion(authenticator, username, name):
    """Connecte directement l'utilisateur après réinitialisation du mot de passe."""
    st.session_state["authentication_status"] = True
    st.session_state["username"] = username
    st.session_state["name"] = name
    # Poser le cookie de re-authentification si possible (persistance)
    try:
        authenticator.cookie_controller.set_cookie()
    except Exception:
        pass


def render_password_reset_flow(checker, authenticator):
    """
    Réinitialisation « à la Google » :
      1. l'utilisateur saisit son email ;
      2. il reçoit un code de vérification ;
      3. il saisit le code + un nouveau mot de passe ;
      4. il est connecté directement à l'application.
    """
    import notifications

    st.markdown("<h4 style='margin: 0 0 1rem; font-size: 1.1rem;'>Mot de passe oublié</h4>", unsafe_allow_html=True)

    if not notifications.notifications_active():
        st.warning("⚠️ Le service d'email n'est pas configuré. Impossible d'envoyer un code de vérification pour le moment — contactez l'administrateur.")
        return

    step = st.session_state.get("reset_step", "request")

    # ── Étape 1 : demande du code ──
    if step == "request":
        st.caption("Saisissez l'email associé à votre compte. Vous recevrez un code de vérification.")
        with st.form(key="reset_request_form", border=False):
            email = st.text_input("Email du compte", placeholder="ex: jean.dupont@gmail.com", key="reset_email_input")
            submitted = st.form_submit_button("Envoyer le code", type="primary", use_container_width=True)

            if submitted:
                email = (email or "").strip()
                if not email or "@" not in email:
                    st.error("Veuillez saisir une adresse email valide.")
                else:
                    username, data = preferences.find_username_by_email(checker, email)
                    if not data:
                        data = {}
                    env_user = os.environ.get("AUTH_USER", "")
                    if username and username == env_user:
                        st.error("❌ Ce compte doit être réinitialisé par l'administrateur.")
                    elif not username:
                        st.error("❌ Aucun compte n'est associé à cet email.")
                    else:
                        code = f"{secrets.randbelow(1000000):06d}"
                        ok, err = notifications.envoyer_code_verification(
                            email, code, data.get("name", username)
                        )
                        if ok:
                            st.session_state.reset_step = "verify"
                            st.session_state.reset_code = code
                            st.session_state.reset_code_exp = time_module.time() + RESET_CODE_TTL
                            st.session_state.reset_target_user = username
                            st.session_state.reset_target_email = email
                            st.session_state.reset_target_name = data.get("name", username)
                            st.rerun()
                        else:
                            st.error(f"❌ Envoi impossible : {err}")

    # ── Étape 2 : vérification du code + nouveau mot de passe ──
    else:
        email = st.session_state.get("reset_target_email", "")
        st.caption(f"Un code à 6 chiffres a été envoyé à **{email}**. Il est valable 10 minutes.")

        with st.form(key="reset_verify_form", border=False):
            code_input = st.text_input("Code de vérification", placeholder="6 chiffres", max_chars=6, key="reset_code_input")
            c1, c2 = st.columns(2)
            with c1:
                new_pwd = st.text_input("Nouveau mot de passe", type="password", key="reset_new_pwd")
            with c2:
                new_pwd_confirm = st.text_input("Confirmer", type="password", key="reset_new_pwd_confirm")

            submitted = st.form_submit_button("Réinitialiser et se connecter", type="primary", use_container_width=True)

            if submitted:
                expected = st.session_state.get("reset_code")
                exp = st.session_state.get("reset_code_exp", 0)
                username = st.session_state.get("reset_target_user")
                name = st.session_state.get("reset_target_name", username)

                if not expected or time_module.time() > exp:
                    st.error("⏱️ Le code a expiré. Recommencez la procédure.")
                elif (code_input or "").strip() != expected:
                    st.error("❌ Code incorrect.")
                elif not new_pwd:
                    st.error("Veuillez saisir un nouveau mot de passe.")
                elif new_pwd != new_pwd_confirm:
                    st.error("Les mots de passe ne correspondent pas.")
                elif len(new_pwd) < 4:
                    st.error("Le mot de passe doit faire au moins 4 caractères.")
                else:
                    h = stauth.Hasher()
                    new_hash = h.hash(new_pwd)
                    success, info = checker.update_user_password_google(username, new_hash)
                    if success:
                        _clear_reset_state()
                        st.session_state.login_mode = "login"
                        _finaliser_connexion(authenticator, username, name)
                        st.success("✅ Mot de passe modifié. Connexion en cours…")
                        st.rerun()
                    else:
                        st.error(f"❌ {info}")

        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("↻ Renvoyer un code", key="reset_resend", use_container_width=True):
                code = f"{secrets.randbelow(1000000):06d}"
                ok, err = notifications.envoyer_code_verification(
                    email, code, st.session_state.get("reset_target_name", "")
                )
                if ok:
                    st.session_state.reset_code = code
                    st.session_state.reset_code_exp = time_module.time() + RESET_CODE_TTL
                    st.success("Nouveau code envoyé.")
                else:
                    st.error(f"❌ {err}")
        with cc2:
            if st.button("Changer d'email", key="reset_change_email", use_container_width=True):
                _clear_reset_state()
                st.rerun()


# ═══════════════════════════════════════════════════════════
# ÉCRAN DE LOGIN (non authentifié)
# ═══════════════════════════════════════════════════════════
def render_login_screen(checker, authenticator):
    """Affiche l'écran de login centré et épuré."""

    # Aucune barre latérale sur l'écran de connexion
    st.markdown("""
    <style>
        section[data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    if "login_mode" not in st.session_state:
        st.session_state.login_mode = "login"
    mode = st.session_state.login_mode

    # Centrer tout
    _, center, _ = st.columns([1, 2, 1])

    with center:
        # Bascule de thème (icône discrète en haut à droite)
        _, tcol = st.columns([6, 1])
        with tcol:
            theme_toggle("theme_login")

        # Header
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0 1.5rem;">
            <div style="font-size: 3rem; line-height: 1; margin-bottom: 0.5rem;">🕊️</div>
            <h2 style="font-size: 1.6rem; margin: 0; font-weight: 800; letter-spacing: -0.02em;">CFPDC</h2>
            <p style="color: #94a3b8; margin-top: 0.35rem; font-size: 0.9rem;">Gestion des Salles</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            if mode == "login":
                try:
                    authenticator.login(location='main', fields={
                        'Form name': 'Se connecter',
                        'Username': "Nom d'utilisateur ou pseudo",
                        'Password': 'Mot de passe',
                        'Login': 'Se connecter',
                    })
                except Exception:
                    # Cookie invalide (session expirée / compte supprimé) : on nettoie
                    try:
                        authenticator.cookie_controller.delete_cookie()
                    except Exception:
                        pass
                    st.warning("Votre session a expiré. Actualisez la page (F5) puis reconnectez-vous.")

                st.markdown("<div class='auth-divider'>ou</div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Créer un compte", use_container_width=True, key="btn_to_register"):
                        st.session_state.login_mode = "register"
                        st.rerun()
                with c2:
                    if st.button("Mot de passe oublié", use_container_width=True, key="btn_to_reset"):
                        st.session_state.login_mode = "reset"
                        st.rerun()

            elif mode == "register":
                st.markdown("<h4 style='margin: 0 0 1rem; font-size: 1.1rem;'>Créer un compte</h4>", unsafe_allow_html=True)

                with st.form(key="login_register_form", border=False):
                    reg_username = st.text_input("Nom d'utilisateur", placeholder="ex: pastor", key="reg_username")
                    reg_pwd = st.text_input("Mot de passe", type="password", placeholder="Min. 4 caractères", key="reg_pwd")
                    reg_pwd_confirm = st.text_input("Confirmer le mot de passe", type="password", placeholder="Retapez le mot de passe", key="reg_pwd_confirm")
                    reg_name = st.text_input("Pseudo", placeholder="ex: Pastor Jean", key="reg_name")

                    reg_submitted = st.form_submit_button("Créer le compte", type="primary", use_container_width=True)

                    if reg_submitted:
                        if not reg_username or not reg_pwd:
                            st.error("Le nom d'utilisateur et le mot de passe sont obligatoires.")
                        elif reg_pwd != reg_pwd_confirm:
                            st.error("Les mots de passe ne correspondent pas.")
                        elif len(reg_pwd) < 4:
                            st.error("Le mot de passe doit faire au moins 4 caractères.")
                        else:
                            h = stauth.Hasher()
                            pwd_hash = h.hash(reg_pwd)
                            success, info = checker.add_user_google(
                                reg_username.strip(),
                                reg_name.strip() or reg_username.strip(),
                                pwd_hash,
                                created_by="inscription"
                            )
                            if success:
                                st.success(f"✅ {info}. Vous pouvez maintenant vous connecter.")
                            else:
                                st.error(f"❌ {info}")

                if st.button("← Retour à la connexion", key="btn_back_login_from_reg", use_container_width=True):
                    st.session_state.login_mode = "login"
                    st.rerun()

            elif mode == "reset":
                render_password_reset_flow(checker, authenticator)

                if st.button("← Retour à la connexion", key="btn_back_login_from_rst", use_container_width=True):
                    _clear_reset_state()
                    st.session_state.login_mode = "login"
                    st.rerun()


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    # ── App principale (checker initialisé avant auth pour lire les users) ──
    checker = init_checker()

    # Keep-alive : évite la mise en veille sur Render (démarre dès le 1er chargement,
    # même sur l'écran de connexion). Ne fait rien en local (pas d'URL publique).
    try:
        keepalive.KeepAlive.demarrer()
    except Exception as e:
        print(f"[App] Impossible de démarrer le keep-alive: {e}")

    # ═══════════════════════════════════════════════════════════
    # AUTHENTIFICATION — env vars / secrets + Google Sheets users
    # ═══════════════════════════════════════════════════════════
    cookie_name = os.environ.get("AUTH_COOKIE_NAME", "cfpdc_auth_cookie")
    cookie_key = os.environ.get("AUTH_COOKIE_KEY", "cfpdc_secret_key_2024")
    cookie_expiry = int(os.environ.get("AUTH_COOKIE_EXPIRY", "30"))

    # 1. Essayer les variables d'environnement
    auth_user = os.environ.get("AUTH_USER", "")
    auth_name = os.environ.get("AUTH_NAME", "")
    auth_hash = os.environ.get("AUTH_HASH", "")

    # 2. Fallback sur Streamlit secrets (local / Streamlit Cloud)
    if (not auth_user or not auth_hash):
        try:
            secret_creds = st.secrets.get("auth_credentials", {})
            if secret_creds and "usernames" in secret_creds:
                credentials = {"usernames": dict(secret_creds["usernames"])}
            else:
                credentials = None
        except Exception:
            credentials = None
    else:
        credentials = {
            "usernames": {
                auth_user: {
                    "name": auth_name or auth_user,
                    "password": auth_hash,
                }
            }
        }

    if not credentials or not credentials.get("usernames"):
        st.error("Configuration d'authentification manquante. Contactez l'administrateur.")
        st.stop()

    # Charger les utilisateurs depuis Google Sheets si dispo
    if checker is not None:
        try:
            sheet_users = checker.get_users_google()
            if sheet_users:
                credentials["usernames"].update(sheet_users)
        except Exception:
            pass

    # Alias pseudo → nom d'utilisateur : permet de se connecter avec le pseudo.
    # streamlit-authenticator met l'identifiant saisi en minuscules ; on ajoute
    # donc des entrées en minuscules pointant vers le même compte.
    pseudo_alias = {}
    try:
        base_users = dict(credentials["usernames"])
        existing = {u.lower() for u in base_users}
        for uname, udata in base_users.items():
            pseudo = (udata.get("name") or "").strip().lower()
            if not pseudo or pseudo in existing:
                continue
            if pseudo in pseudo_alias:
                pseudo_alias[pseudo] = None  # pseudo ambigu → désactivé
                continue
            pseudo_alias[pseudo] = uname
        for pkey, real in list(pseudo_alias.items()):
            if real:
                credentials["usernames"][pkey] = dict(credentials["usernames"][real])
        st.session_state["_pseudo_alias"] = {k: v for k, v in pseudo_alias.items() if v}
    except Exception:
        st.session_state["_pseudo_alias"] = {}

    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        cookie_expiry_days=cookie_expiry
    )

    # Vérifier l'état d'authentification (cookie)
    # Un cookie périmé ou pointant vers un compte inexistant/supprimé fait lever
    # LoginError par streamlit-authenticator : on l'intercepte pour ne pas planter
    # l'app, on repart en "non connecté" et on nettoie le cookie invalide.
    try:
        authenticator.login(location='unrendered')
    except Exception:
        st.session_state['authentication_status'] = None
        try:
            authenticator.cookie_controller.delete_cookie()
        except Exception:
            pass
        # Relancer une fois pour repartir d'un état propre (cookie supprimé)
        if not st.session_state.get('_auth_cookie_reset'):
            st.session_state['_auth_cookie_reset'] = True
            st.rerun()
    authentication_status = st.session_state.get('authentication_status')

    if authentication_status is True:
        username = st.session_state.get('username')
        # Si connexion via un pseudo, revenir au vrai nom d'utilisateur
        alias_map = st.session_state.get("_pseudo_alias", {})
        if username in alias_map:
            username = alias_map[username]
        name = st.session_state.get('name')
        st.session_state["username"] = username
        st.session_state["name"] = name

        if checker is None:
            st.error("Dossier 'salles/' introuvable. Vérifiez l'installation.")
            st.stop()

        render_sidebar(checker, authenticator)

        # Replier la barre latérale au 1er chargement sur mobile
        collapse_sidebar_on_mobile()

        # Démarrer le scheduler de notifications quotidiennes (thread daemon)
        try:
            notifications.NotifScheduler.demarrer(checker)
        except Exception as e:
            print(f"[App] Impossible de démarrer le scheduler de notifications: {e}")

        st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h1 style="font-size: 1.8rem; margin: 0;">Tableau de bord</h1>
            <p style="color: #94a3b8; margin-top: 0.35rem; font-size: 0.95rem;">
                Gestion des salles et réservations — CFPDC
            </p>
        </div>
        """, unsafe_allow_html=True)

        is_admin = st.session_state.get("username", "") == os.environ.get("AUTH_USER", "")

        # Invitation à renseigner l'email (récupération de mot de passe).
        # Prioritaire : si elle s'affiche, on n'ouvre pas d'autre modale.
        render_email_prompt(checker)

        # Onglets principaux (Utilisateurs et Notifications sont dans le rouage ⚙️)
        if is_admin:
            tab1, tab2, tab3 = st.tabs(["Disponibilités", "Réservations", "Notifications"])
        else:
            tab1, tab2 = st.tabs(["Disponibilités", "Réservations"])

        with tab1:
            onglet_gestion_salle(checker)

        with tab2:
            onglet_editer_planning(checker)

        if is_admin:
            with tab3:
                onglet_notifications(checker)

    elif authentication_status == False:
        st.error("❌ Mot de passe incorrect")
        render_login_screen(checker, authenticator)
    else:
        # Pas encore authentifié
        render_login_screen(checker, authenticator)


if __name__ == "__main__":
    main()
