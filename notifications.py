"""
Module de notifications par email (SMTP) pour la gestion des salles CFPDC.

Trois types de notifications:
  (a) Quotidienne — récapitulatif des occupations du lendemain (toutes salles)
  (b) Alerte doublon — créneau en conflit détecté à l'ajout d'une réservation
  (c) Nouvel ajout — une réservation a été ajoutée au planning

Configuration via variables d'environnement:
  SMTP_HOST       — serveur SMTP (defaut: smtp.gmail.com)
  SMTP_PORT       — port SMTP (defaut: 587)
  SMTP_EMAIL      — adresse du compte expéditeur
  SMTP_PASSWORD   — mot de passe applicatif (app password) du compte expéditeur
  NOTIF_FROM_NAME — nom affiché de l'expéditeur (defaut: CFPDC Salles)
  NOTIF_ENABLED   — "false" pour desactiver globalement (defaut: true si SMTP_EMAIL défini)
"""

import os
import smtplib
import ssl
import threading
import time as time_module
from email.message import EmailMessage
from datetime import datetime, date, timedelta

import preferences

# Jours de la semaine en français
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]


def format_date_fr(d: date) -> str:
    """Formate une date en français: 'mercredi 27 août 2026'."""
    jour = JOURS_FR[d.weekday()]
    mois = MOIS_FR[d.month - 1]
    return f"{jour} {d.day} {mois} {d.year}"


def _smtp_config() -> dict:
    """Retourne la config SMTP depuis les variables d'environnement."""
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "email": os.environ.get("SMTP_EMAIL", ""),
        "password": os.environ.get("SMTP_PASSWORD", ""),
        "from_name": os.environ.get("NOTIF_FROM_NAME", "CFPDC Salles"),
    }


def notifications_active() -> bool:
    """Indique si l'envoi de notifications est activé (SMTP configuré)."""
    if os.environ.get("NOTIF_ENABLED", os.environ.get("NOTIF_ENABLE", "")).lower() == "false":
        return False
    cfg = _smtp_config()
    return bool(cfg["email"] and cfg["password"])


def _envoyer_email(destinataires: list, sujet: str, corps_html: str) -> tuple:
    """
    Envoie un email HTML à une liste de destinataires.
    Retourne (success, error).
    """
    if not destinataires:
        return False, "Aucun destinataire"

    cfg = _smtp_config()
    if not cfg["email"] or not cfg["password"]:
        return False, "SMTP non configuré (SMTP_EMAIL/SMTP_PASSWORD manquant)"

    msg = EmailMessage()
    msg["Subject"] = sujet
    msg["From"] = f"{cfg['from_name']} <{cfg['email']}>"
    msg["To"] = ", ".join(destinataires)
    msg.set_content("Ce message nécessite un client email compatible HTML.")
    msg.add_alternative(corps_html, subtype="html")

    try:
        context = ssl.create_default_context()
        port = cfg["port"]
        # Essayer SMTP_SSL (port 465) si configuré, sinon SMTP avec STARTTLS (587)
        if port == 465:
            with smtplib.SMTP_SSL(cfg["host"], port, timeout=30, context=context) as server:
                server.login(cfg["email"], cfg["password"])
                server.send_message(msg)
        else:
            with smtplib.SMTP(cfg["host"], port, timeout=30) as server:
                server.starttls(context=context)
                server.login(cfg["email"], cfg["password"])
                server.send_message(msg)
        return True, None
    except Exception as e:
        print(f"[Notifications] Erreur envoi email: {e}")
        return False, str(e)


# ═══════════════════════════════════════════════════════════
# (a) NOTIFICATION QUOTIDIENNE — récap du lendemain
# ═══════════════════════════════════════════════════════════
def _ligne_occupation_html(occ: dict) -> str:
    """Génère une ligne HTML pour une occupation."""
    occupant = occ.get("occupant", "Inconnu")
    activite = occ.get("activite", "")
    horaire = occ.get("horaire", "—")
    salle = occ.get("salle", "")
    telephone = occ.get("telephone", "")
    source = occ.get("source", "")

    # Badge source (planning fixe vs réservation)
    if source == "planning fixe":
        badge = '<span class="badge fixe">Fixe</span>'
    else:
        badge = '<span class="badge resa">Résa</span>'

    tel_html = f" — 📞 {telephone}" if telephone else ""
    salle_html = f"<div class='salle'>{salle}</div>" if salle else ""

    return f"""
    <tr>
      <td><strong>{occupant}</strong>{tel_html}</td>
      <td>{activite}</td>
      <td><strong>{horaire}</strong></td>
      <td>{badge}</td>
    </tr>"""


def _html_quotidien(demain: date, occupations_par_salle: dict) -> str:
    """Construit le HTML du récap quotidien."""
    titre_date = format_date_fr(demain)
    sections = []
    salles_order = ["salle principale", "salle du fond", "salle du milieu"]
    noms_salles = {
        "salle principale": "Salle principale",
        "salle du fond": "Salle du fond",
        "salle du milieu": "Salle du milieu",
    }

    for salle in salles_order:
        occs = occupations_par_salle.get(salle, [])
        # Trier par heure de début
        def _key(o):
            d = o.get("debut")
            return d.strftime("%H%M") if hasattr(d, "strftime") else "0000"
        occs_sorted = sorted(occs, key=_key)

        lignes = "".join(_ligne_occupation_html(o) for o in occs_sorted)
        if not lignes:
            lignes = '<tr><td colspan="4" class="vide">Aucune occupation prévue</td></tr>'

        sections.append(f"""
        <div class="salle-section">
          <h2>{noms_salles[salle]}</h2>
          <table>
            <thead>
              <tr><th>Occupant</th><th>Activité</th><th>Horaire</th><th>Type</th></tr>
            </thead>
            <tbody>{lignes}</tbody>
          </table>
        </div>""")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; color: #1e293b; background: #f8fafc; padding: 1.5rem; }}
  h1 {{ font-size: 1.4rem; color: #4f46e5; margin-bottom: 0.25rem; }}
  .date {{ color: #64748b; font-size: 0.95rem; margin-bottom: 1.5rem; }}
  .salle-section {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; }}
  .salle-section h2 {{ font-size: 1.1rem; margin: 0 0 0.75rem; color: #0f172a; border-bottom: 2px solid #4f46e5; padding-bottom: 0.4rem; display: inline-block; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; padding: 0.4rem 0.5rem; border-bottom: 1px solid #e2e8f0; }}
  td {{ padding: 0.55rem 0.5rem; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: top; }}
  .vide {{ color: #94a3b8; font-style: italic; text-align: center; }}
  .badge {{ display: inline-block; padding: 0.1rem 0.5rem; border-radius: 999px; font-size: 0.7rem; font-weight: 600; }}
  .badge.fixe {{ background: #e0e7ff; color: #4338ca; }}
  .badge.resa {{ background: #fef3c7; color: #92400e; }}
  .footer {{ margin-top: 2rem; color: #94a3b8; font-size: 0.8rem; text-align: center; }}
</style>
</head>
<body>
  <h1>📅 Récapitulatif des occupations</h1>
  <div class="date">Demain — {titre_date}</div>
  {''.join(sections)}
  <div class="footer">Email automatique — Application Gestion des Salles CFPDC</div>
</body>
</html>"""


def envoyer_recap_quotidien(checker, date_cible: date = None) -> tuple:
    """
    Envoie le récap des occupations de la date cible (defaut: demain).
    Retourne (success, error).
    """
    if not notifications_active():
        return False, "Notifications désactivées (SMTP non configuré)"

    if date_cible is None:
        date_cible = date.today() + timedelta(days=1)

    salles = ["salle principale", "salle du fond", "salle du milieu"]
    occupations_par_salle = {}
    for salle in salles:
        try:
            result = checker.get_all_occupations(salle, date_cible)
            occs = result.get("occupations", [])
            # Enrichir avec le nom de salle
            for o in occs:
                o["salle"] = salle
            occupations_par_salle[salle] = occs
        except Exception as e:
            print(f"[Notifications] Erreur récup occupations {salle}: {e}")
            occupations_par_salle[salle] = []

    # S'il n'y a aucune occupation nulle part, on n'envoie pas
    total = sum(len(v) for v in occupations_par_salle.values())
    if total == 0:
        print(f"[Notifications] Aucune occupation pour le {date_cible}, pas d'email envoyé")
        return True, None

    destinataires = preferences.get_subscribed_emails(checker)
    if not destinataires:
        return False, "Aucun destinataire avec email valide"

    sujet = f"📅 Récap des salles — {format_date_fr(date_cible)}"
    html = _html_quotidien(date_cible, occupations_par_salle)
    return _envoyer_email(destinataires, sujet, html)


# ═══════════════════════════════════════════════════════════
# (b) NOTIFICATION D'ALERTE DOUBLON (conflit de créneau)
# ═══════════════════════════════════════════════════════════
def envoyer_alerte_doublon(checker, nouvelle_resa: dict, existante: dict) -> tuple:
    """
    Alerte lorsqu'une nouvelle réservation entre en conflit avec une existante.
    Retourne (success, error).
    """
    if not notifications_active():
        return False, "Notifications désactivées"

    destinataires = preferences.get_subscribed_emails(checker)
    if not destinataires:
        return False, "Aucun destinataire"

    sujet = f"⚠️ Conflit de créneau — {nouvelle_resa.get('salle','')} — {nouvelle_resa.get('date','')}"

    def _detail(titre, r):
        return f"""
        <div class="resa-box">
          <h3>{titre}</h3>
          <table>
            <tr><td>Salle</td><td><strong>{r.get('salle','')}</strong></td></tr>
            <tr><td>Nom</td><td><strong>{r.get('occupant','')}</strong></td></tr>
            <tr><td>Date</td><td>{r.get('date','')}</td></tr>
            <tr><td>Horaire</td><td><strong>{r.get('horaire','')}</strong></td></tr>
            <tr><td>Téléphone</td><td>{r.get('telephone','—') or '—'}</td></tr>
            <tr><td>Ajouté par</td><td>{r.get('added_by','—') or '—'}</td></tr>
          </table>
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; color: #1e293b; background: #f8fafc; padding: 1.5rem; }}
  h1 {{ color: #dc2626; font-size: 1.3rem; }}
  .alerte {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1.25rem; color: #991b1b; font-weight: 600; }}
  .resa-box {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1rem; }}
  .resa-box h3 {{ margin: 0 0 0.5rem; font-size: 1rem; color: #4f46e5; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 0.35rem 0.5rem; font-size: 0.9rem; border-bottom: 1px solid #f1f5f9; }}
  td:first-child {{ color: #64748b; width: 120px; }}
  .footer {{ margin-top: 2rem; color: #94a3b8; font-size: 0.8rem; text-align: center; }}
</style>
</head>
<body>
  <h1>⚠️ Conflit de créneau détecté</h1>
  <div class="alerte">Deux réservations occupent le même créneau ({nouvelle_resa.get('salle','')}, {nouvelle_resa.get('date','')}, {nouvelle_resa.get('horaire','')}). Merci de vérifier le planning.</div>
  {_detail("Nouvelle réservation", nouvelle_resa)}
  {_detail("Réservation existante", existante)}
  <div class="footer">Application Gestion des Salles CFPDC</div>
</body>
</html>"""

    return _envoyer_email(destinataires, sujet, html)


# ═══════════════════════════════════════════════════════════
# (c) NOTIFICATION NOUVEL AJOUT DE RÉSERVATION
# ═══════════════════════════════════════════════════════════
def envoyer_nouvel_ajout(checker, resa: dict) -> tuple:
    """
    Notifie qu'une nouvelle réservation a été ajoutée au planning.
    Retourne (success, error).
    """
    if not notifications_active():
        return False, "Notifications désactivées"

    destinataires = preferences.get_subscribed_emails(checker)
    if not destinataires:
        return False, "Aucun destinataire"

    sujet = f"✅ Nouvelle réservation — {resa.get('salle','')} — {resa.get('occupant','')} — {resa.get('date','')}"

    lignes = []
    champs = [
        ("Salle", "salle"),
        ("Nom / Occupant", "occupant"),
        ("Date", "date"),
        ("Horaire", "horaire"),
        ("Téléphone", "telephone"),
        ("Accompte", "accompte"),
        ("Reste à payer", "reste_a_payer"),
        ("Prix location", "prix_location"),
        ("Caution", "caution_menage"),
        ("Ajouté par", "added_by"),
    ]
    for label, key in champs:
        val = resa.get(key, "")
        if val:
            lignes.append(f"<tr><td>{label}</td><td><strong>{val}</strong></td></tr>")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; color: #1e293b; background: #f8fafc; padding: 1.5rem; }}
  h1 {{ color: #16a34a; font-size: 1.3rem; }}
  .box {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 0.45rem 0.5rem; font-size: 0.9rem; border-bottom: 1px solid #f1f5f9; }}
  td:first-child {{ color: #64748b; width: 150px; }}
  .footer {{ margin-top: 2rem; color: #94a3b8; font-size: 0.8rem; text-align: center; }}
</style>
</head>
<body>
  <h1>✅ Nouvelle réservation ajoutée</h1>
  <div class="box">
    <table>{''.join(lignes)}</table>
  </div>
  <div class="footer">Application Gestion des Salles CFPDC</div>
</body>
</html>"""

    return _envoyer_email(destinataires, sujet, html)


# ═══════════════════════════════════════════════════════════
# TÂCHE PLANIFIÉE — thread/timer pour l'envoi quotidien
# ═══════════════════════════════════════════════════════════
# L'heure d'envoi du récap quotidien (heure locale), par défaut 20h00
# (le mardi soir pour le mercredi)
HEURE_ENVOI_QUOTIDIEN = int(os.environ.get("NOTIF_HEURE_QUOTIDIEN", "20"))


class NotifScheduler:
    """
    Thread daemon qui vérifie périodiquement s'il est l'heure d'envoyer
    le récap quotidien et déclenche l'envoi.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, checker):
        self.checker = checker
        self._thread = None
        self._stop_event = threading.Event()
        # Mémorise (date, envoyé) pour ne pas envoyer deux fois le même jour
        self._dernier_envoi = None

    @classmethod
    def demarrer(cls, checker):
        """Démarre le scheduler (singleton, thread daemon)."""
        with cls._lock:
            if cls._instance is not None and cls._instance._thread and cls._instance._thread.is_alive():
                return cls._instance
            cls._instance = cls(checker)
            cls._instance._start_thread()
            return cls._instance

    def _start_thread(self):
        self._thread = threading.Thread(target=self._boucle, daemon=True)
        self._thread.start()
        print(f"[Notifications] Scheduler démarré — envoi quotidien à {HEURE_ENVOI_QUOTIDIEN}h")

    def _boucle(self):
        # Vérifie toutes les 15 minutes
        while not self._stop_event.is_set():
            try:
                self._verifier_et_envoyer()
            except Exception as e:
                print(f"[Notifications] Erreur boucle scheduler: {e}")
            # Attendre 15 minutes ou jusqu'à stop
            self._stop_event.wait(15 * 60)

    def _verifier_et_envoyer(self):
        if not notifications_active():
            return
        maintenant = datetime.now()
        aujourdhui = maintenant.date()

        # Déjà envoyé aujourd'hui ?
        if self._dernier_envoi == aujourdhui:
            return

        # Heure d'envoi atteinte ?
        if maintenant.hour >= HEURE_ENVOI_QUOTIDIEN:
            print(f"[Notifications] Envoi du récap quotidien pour le {aujourdhui + timedelta(days=1)}")
            success, error = envoyer_recap_quotidien(self.checker)
            if success:
                self._dernier_envoi = aujourdhui
                print("[Notifications] Récap quotidien envoyé")
            elif error:
                print(f"[Notifications] Échec récap quotidien: {error}")