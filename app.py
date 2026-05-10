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
        color: #374151;
    }
    
    .detail-item strong {
        color: #1f2937;
    }
    
    /* Mode sombre */
    @media (prefers-color-scheme: dark) {
        .glass-card {
            background: rgba(30, 41, 59, 0.8);
            border-color: rgba(255, 255, 255, 0.1);
        }
        
        .occupation-card {
            background: #1e293b;
            border-left-color: #818cf8;
        }
        
        .occupant-name {
            color: #f1f5f9;
        }
        
        .activity-name {
            color: #94a3b8;
        }
        
        .reservation-details {
            background: rgba(99, 102, 241, 0.2);
        }
        
        .detail-item {
            color: #e2e8f0;
        }
        
        .detail-item strong {
            color: #60a5fa;
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


def format_montant(valeur):
    """Formate un montant en ajoutant € si pas déjà présent."""
    if valeur == 'Non renseigné':
        return valeur
    valeur_str = str(valeur).strip()
    if '€' in valeur_str:
        return valeur_str
    return f"{valeur_str}€"


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

                        for idx, occ in enumerate(occupations):
                            horaire_display = occ["horaire"]
                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""
                            
                            # Créer un identifiant unique pour cette occupation
                            occ_id = f"{occupant}_{idx}".replace(" ", "_")
                            
                            # Afficher la carte
                            st.markdown(f'''
                            <div class="occupation-card">
                                <div class="time-display">🕐 {horaire_display}</div>
                                <div class="occupant-name">👤 <strong>{occupant}</strong></div>
                                {f'<div class="activity-name">📝 {activite}</div>' if activite else ''}
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Section édition pour les réservations
                            if occ.get('source') == 'réservation':
                                with st.expander("✏️ Modifier les informations"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Accompte
                                        accompte_val = occ.get('accompte', 'Non renseigné')
                                        if accompte_val == 'Non renseigné':
                                            st.markdown('💰 **Accompte:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_accompte = st.text_input("", placeholder="Ex: 100", key=f"accompte_{occ_id}")
                                        else:
                                            st.markdown(f'💰 **Accompte:** {format_montant(accompte_val)}', unsafe_allow_html=True)
                                            new_accompte = st.text_input("Modifier", value=str(accompte_val).replace('€', ''), key=f"accompte_{occ_id}")
                                        
                                        # Reste à payer
                                        reste_val = occ.get('reste_a_payer', 'Non renseigné')
                                        if reste_val == 'Non renseigné':
                                            st.markdown('💳 **Reste à payer:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_reste = st.text_input("", placeholder="Ex: 550", key=f"reste_{occ_id}")
                                        else:
                                            st.markdown(f'💳 **Reste à payer:** {format_montant(reste_val)}', unsafe_allow_html=True)
                                            new_reste = st.text_input("Modifier", value=str(reste_val).replace('€', ''), key=f"reste_{occ_id}")
                                        
                                        # Prix de location
                                        prix_val = occ.get('prix_location', 'Non renseigné')
                                        if prix_val == 'Non renseigné':
                                            st.markdown('💵 **Prix de location:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_prix = st.text_input("", placeholder="Ex: 650", key=f"prix_{occ_id}")
                                        else:
                                            st.markdown(f'💵 **Prix de location:** {format_montant(prix_val)}', unsafe_allow_html=True)
                                            new_prix = st.text_input("Modifier", value=str(prix_val).replace('€', ''), key=f"prix_{occ_id}")
                                    
                                    with col2:
                                        # Caution ménage
                                        caution_val = occ.get('caution_menage', 'Non renseigné')
                                        if caution_val == 'Non renseigné':
                                            st.markdown('🧹 **Chèque caution:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_caution = st.text_input("", placeholder="Ex: Oui / 100", key=f"caution_{occ_id}")
                                        else:
                                            st.markdown(f'🧹 **Chèque caution:** {caution_val}', unsafe_allow_html=True)
                                            new_caution = st.text_input("Modifier", value=str(caution_val), key=f"caution_{occ_id}")
                                        
                                        # Salle d'occupation
                                        salle_occ_val = occ.get('salle_occupation', 'Non renseigné')
                                        if salle_occ_val == 'Non renseigné':
                                            st.markdown('🏠 **Salle:** \u003cspan style="color: #dc2626;"\u003eNon renseignée\u003c/span\u003e', unsafe_allow_html=True)
                                            new_salle_occ = st.text_input("", placeholder="Ex: Salle principale", key=f"salleocc_{occ_id}")
                                        else:
                                            st.markdown(f'🏠 **Salle:** {salle_occ_val}', unsafe_allow_html=True)
                                            new_salle_occ = st.text_input("Modifier", value=str(salle_occ_val), key=f"salleocc_{occ_id}")
                                    
                                    # Bouton sauvegarder
                                    if st.button("💾 Sauvegarder", key=f"save_{occ_id}", type="primary"):
                                        # Préparer les données à mettre à jour
                                        update_data = {}
                                        if new_accompte:
                                            update_data['accompte'] = new_accompte if '€' in new_accompte else f"{new_accompte}€"
                                        if new_reste:
                                            update_data['reste_a_payer'] = new_reste if '€' in new_reste else f"{new_reste}€"
                                        if new_prix:
                                            update_data['prix_location'] = new_prix if '€' in new_prix else f"{new_prix}€"
                                        if new_caution:
                                            update_data['caution_menage'] = new_caution
                                        if new_salle_occ:
                                            update_data['salle_occupation'] = new_salle_occ
                                        
                                        if update_data:
                                            success, error = checker.update_reservation_google(
                                                salle.lower(),
                                                date_input,
                                                occ['occupant'],
                                                update_data
                                            )
                                            
                                            if success:
                                                st.success("✅ Modifications sauvegardées!")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Erreur: {error}")
                                        else:
                                            st.info("ℹ️ Aucune modification détectée")

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

                        for idx, occ in enumerate(occupations):
                            horaire_display = occ["horaire"]
                            occupant = occ["occupant"] if occ["occupant"] else "Non précisé"
                            activite = occ["activite"] if occ["activite"] and occ["activite"] != "Non précisée" else ""
                            
                            # Créer un identifiant unique pour cette occupation
                            occ_id = f"{occupant}_{idx}".replace(" ", "_")
                            
                            # Afficher la carte
                            st.markdown(f'''
                            <div class="occupation-card">
                                <div class="time-display">🕐 {horaire_display}</div>
                                <div class="occupant-name">👤 Par : <strong>{occupant}</strong></div>
                                {f'<div class="activity-name">📝 {activite}</div>' if activite else ''}
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Section édition pour les réservations
                            if occ.get('source') == 'réservation':
                                with st.expander("✏️ Modifier les informations"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Accompte
                                        accompte_val = occ.get('accompte', 'Non renseigné')
                                        if accompte_val == 'Non renseigné':
                                            st.markdown('💰 **Accompte:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_accompte = st.text_input("", placeholder="Ex: 100", key=f"accompte_{occ_id}")
                                        else:
                                            st.markdown(f'💰 **Accompte:** {format_montant(accompte_val)}', unsafe_allow_html=True)
                                            new_accompte = st.text_input("Modifier", value=str(accompte_val).replace('€', ''), key=f"accompte_{occ_id}")
                                        
                                        # Reste à payer
                                        reste_val = occ.get('reste_a_payer', 'Non renseigné')
                                        if reste_val == 'Non renseigné':
                                            st.markdown('💳 **Reste à payer:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_reste = st.text_input("", placeholder="Ex: 550", key=f"reste_{occ_id}")
                                        else:
                                            st.markdown(f'💳 **Reste à payer:** {format_montant(reste_val)}', unsafe_allow_html=True)
                                            new_reste = st.text_input("Modifier", value=str(reste_val).replace('€', ''), key=f"reste_{occ_id}")
                                        
                                        # Prix de location
                                        prix_val = occ.get('prix_location', 'Non renseigné')
                                        if prix_val == 'Non renseigné':
                                            st.markdown('💵 **Prix de location:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_prix = st.text_input("", placeholder="Ex: 650", key=f"prix_{occ_id}")
                                        else:
                                            st.markdown(f'💵 **Prix de location:** {format_montant(prix_val)}', unsafe_allow_html=True)
                                            new_prix = st.text_input("Modifier", value=str(prix_val).replace('€', ''), key=f"prix_{occ_id}")
                                    
                                    with col2:
                                        # Caution ménage
                                        caution_val = occ.get('caution_menage', 'Non renseigné')
                                        if caution_val == 'Non renseigné':
                                            st.markdown('🧹 **Chèque caution:** \u003cspan style="color: #dc2626;"\u003eNon renseigné\u003c/span\u003e', unsafe_allow_html=True)
                                            new_caution = st.text_input("", placeholder="Ex: Oui / 100", key=f"caution_{occ_id}")
                                        else:
                                            st.markdown(f'🧹 **Chèque caution:** {caution_val}', unsafe_allow_html=True)
                                            new_caution = st.text_input("Modifier", value=str(caution_val), key=f"caution_{occ_id}")
                                        
                                        # Salle d'occupation
                                        salle_occ_val = occ.get('salle_occupation', 'Non renseigné')
                                        if salle_occ_val == 'Non renseigné':
                                            st.markdown('🏠 **Salle:** \u003cspan style="color: #dc2626;"\u003eNon renseignée\u003c/span\u003e', unsafe_allow_html=True)
                                            new_salle_occ = st.text_input("", placeholder="Ex: Salle principale", key=f"salleocc_{occ_id}")
                                        else:
                                            st.markdown(f'🏠 **Salle:** {salle_occ_val}', unsafe_allow_html=True)
                                            new_salle_occ = st.text_input("Modifier", value=str(salle_occ_val), key=f"salleocc_{occ_id}")
                                    
                                    # Bouton sauvegarder
                                    if st.button("💾 Sauvegarder", key=f"save_{occ_id}", type="primary"):
                                        # Préparer les données à mettre à jour
                                        update_data = {}
                                        if new_accompte:
                                            update_data['accompte'] = new_accompte if '€' in new_accompte else f"{new_accompte}€"
                                        if new_reste:
                                            update_data['reste_a_payer'] = new_reste if '€' in new_reste else f"{new_reste}€"
                                        if new_prix:
                                            update_data['prix_location'] = new_prix if '€' in new_prix else f"{new_prix}€"
                                        if new_caution:
                                            update_data['caution_menage'] = new_caution
                                        if new_salle_occ:
                                            update_data['salle_occupation'] = new_salle_occ
                                        
                                        if update_data:
                                            success, error = checker.update_reservation_google(
                                                salle.lower(),
                                                date_input,
                                                occ['occupant'],
                                                update_data
                                            )
                                            
                                            if success:
                                                st.success("✅ Modifications sauvegardées!")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Erreur: {error}")
                                        else:
                                            st.info("ℹ️ Aucune modification détectée")

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
