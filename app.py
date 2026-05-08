#!/usr/bin/env python3
"""
Application Streamlit pour la vérification de disponibilité des salles.
"""

import streamlit as st
from datetime import datetime, time
import os
from dotenv import load_dotenv

# Charger les variables d'environnement locales
load_dotenv()

from checker import SalleChecker

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Salles",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS simple et fonctionnel
st.markdown("""
<style>
    /* Style général */
    .main-header {
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0 0.5rem 0;
        color: #1e3a5f;
    }

    .sub-header {
        text-align: center;
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }

    /* Résultats */
    .result-libre {
        background-color: #dcfce7;
        border: 2px solid #22c55e;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .result-libre h3 {
        color: #15803d;
        margin: 0 0 0.5rem 0;
    }

    .result-occupe {
        background-color: #fee2e2;
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .result-occupe h3 {
        color: #b91c1c;
        margin: 0 0 0.5rem 0;
    }

    /* Cartes d'occupation */
    .occupation-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
    }

    .time-display {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }

    .occupant-name {
        font-size: 1rem;
        color: #374151;
        margin-top: 0.5rem;
    }

    .activity-name {
        font-size: 0.9rem;
        color: #6b7280;
        font-style: italic;
    }

    /* Mode sombre */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #60a5fa;
        }
        .sub-header {
            color: #94a3b8;
        }
        .result-libre {
            background-color: #064e3b;
            border-color: #22c55e;
        }
        .result-libre h3 {
            color: #4ade80;
        }
        .result-occupe {
            background-color: #7f1d1d;
            border-color: #f87171;
        }
        .result-occupe h3 {
            color: #fca5a5;
        }
        .occupation-card {
            background-color: #1e293b;
            border-color: #475569;
        }
        .time-display {
            color: #60a5fa;
        }
        .occupant-name {
            color: #e2e8f0;
        }
        .activity-name {
            color: #94a3b8;
        }
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
    # En-tête
    st.markdown('<div class="main-header">Gestion des Salles</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CFPDC — Système de réservation</div>', unsafe_allow_html=True)

    st.divider()

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

    sans_heure = st.checkbox("🕐 Sans heure précise (voir toutes les occupations du jour)", value=False)

    heure = None
    if not sans_heure:
        heure = st.time_input(
            "Heure",
            value=datetime.now().time().replace(minute=0, second=0, microsecond=0)
        )

    st.markdown("<br>", unsafe_allow_html=True)
    verify_clicked = st.button("🔍 Vérifier la disponibilité", use_container_width=True, type="primary")

    st.divider()

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
                                <span style="font-size: 0.95rem;">Aucune occupation prévue ce jour</span>
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

                        st.markdown("### Créneaux occupés")

                        for occ in occupations:
                            horaire_display = occ["horaire"]
                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""

                            warning = ""
                            if "warning" in occ:
                                warning = f'<p style="color: #ca8a04; font-size: 0.85rem;">⚠️ {occ["warning"]}</p>'

                            st.markdown(f'''
                            <div class="occupation-card">
                                <div class="time-display">🕐 {horaire_display}</div>
                                <div class="occupant-name">👤 <strong>{occupant}</strong></div>
                                {f'<div class="activity-name">📝 {activite}</div>' if activite else ''}
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

                        st.markdown("### Détails des occupations")

                        for occ in occupations:
                            horaire_display = occ["horaire"]
                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""

                            warning = ""
                            if "warning" in occ:
                                warning = f'<p style="color: #ca8a04; font-size: 0.85rem;">⚠️ {occ["warning"]}</p>'

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
                st.info("Vérifiez que les fichiers Excel sont présents dans le dossier 'salles/'")

    st.divider()
    st.markdown(
        '<p style="text-align: center; color: #9ca3af; font-size: 0.8rem;">'
        'CFPDC — Application de gestion des salles'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
