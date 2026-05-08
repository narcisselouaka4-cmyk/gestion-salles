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

# CSS minimal pour mobile-friendly
st.markdown("""
<style>
    .main-header {
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1f77b4;
    }
    .sub-header {
        text-align: center;
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-libre {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .result-occupe {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .occupation-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .time-display {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
    }
    .occupant-name {
        font-size: 1.1rem;
        color: #555;
        margin-top: 0.5rem;
    }
    .activity-name {
        font-size: 0.95rem;
        color: #777;
        font-style: italic;
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
    st.markdown('<div class="main-header">🏢 Vérification des Salles</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Consultez la disponibilité des salles en temps réel</div>', unsafe_allow_html=True)

    # Déterminer le chemin vers les fichiers de salles
    # En priorité : dossier 'salles/' à côté du script, sinon le dossier courant
    script_dir = os.path.dirname(os.path.abspath(__file__))
    salles_dir = os.path.join(script_dir, "salles")

    # ID du Google Sheet pour les réservations
    # Essayer de lire depuis Streamlit secrets, sinon utiliser la valeur par défaut
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

    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #999; font-size: 0.8rem;">'
        'Application accessible depuis tous les appareils du réseau local'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
