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
NOMS_SALLES = {
    "salle principale": "Salle principale",
    "salle du fond": "Salle du fond",
    "salle du milieu": "Salle du milieu",
}
SALLES_ORDER = ["salle principale", "salle du fond", "salle du milieu"]


def _tri_occs(occs: list) -> list:
    """Trie les occupations par heure de début."""
    def _key(o):
        d = o.get("debut")
        return d.strftime("%H%M") if hasattr(d, "strftime") else str(o.get("horaire", ""))
    return sorted(occs, key=_key)


def _recap_row(occ: dict) -> str:
    """Ligne détaillée : nom, activité, horaire."""
    occupant = occ.get("occupant", "Inconnu")
    activite = occ.get("activite", "") or "—"
    horaire = occ.get("horaire", "—")
    return f"""
    <tr>
      <td><strong>{occupant}</strong></td>
      <td>{activite}</td>
      <td class="hr"><strong>{horaire}</strong></td>
    </tr>"""


def _html_recap(date_cible: date, occ_par_salle: dict) -> str:
    """
    Construit le récap : un résumé groupé (salles occupées) puis un bloc
    de détails repliable par salle (nom / activité / horaire).
    `occ_par_salle` ne contient que les salles suivies ET occupées.
    """
    titre_date = format_date_fr(date_cible)

    # Résumé groupé
    resume_items = []
    for salle in SALLES_ORDER:
        occs = occ_par_salle.get(salle)
        if not occs:
            continue
        n = len(occs)
        libelle = "occupation" if n == 1 else "occupations"
        resume_items.append(
            f'<li><span class="dot"></span><strong>{NOMS_SALLES[salle]}</strong>'
            f'<span class="count">{n} {libelle}</span></li>'
        )
    resume_html = f'<ul class="resume">{"".join(resume_items)}</ul>'

    # Détails repliables par salle
    details_sections = []
    for salle in SALLES_ORDER:
        occs = occ_par_salle.get(salle)
        if not occs:
            continue
        lignes = "".join(_recap_row(o) for o in _tri_occs(occs))
        details_sections.append(f"""
        <details open>
          <summary>{NOMS_SALLES[salle]} — en savoir plus</summary>
          <table>
            <thead><tr><th>Nom</th><th>Activité</th><th class="hr">Horaire</th></tr></thead>
            <tbody>{lignes}</tbody>
          </table>
        </details>""")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; color: #1e293b; background: #f5f6f8; padding: 1.5rem; margin: 0; }}
  .wrap {{ max-width: 560px; margin: 0 auto; }}
  h1 {{ font-size: 1.25rem; color: #0f172a; margin: 0 0 0.15rem; }}
  .date {{ color: #64748b; font-size: 0.95rem; margin-bottom: 1.25rem; }}
  .resume {{ list-style: none; padding: 0; margin: 0 0 1.25rem; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }}
  .resume li {{ display: flex; align-items: center; gap: 0.6rem; padding: 0.85rem 1.1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.95rem; }}
  .resume li:last-child {{ border-bottom: none; }}
  .resume .dot {{ width: 9px; height: 9px; border-radius: 50%; background: #d97706; flex: none; }}
  .resume .count {{ margin-left: auto; color: #64748b; font-size: 0.85rem; }}
  details {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 0.5rem 1.1rem; margin-bottom: 0.85rem; }}
  summary {{ cursor: pointer; font-weight: 600; color: #0f172a; padding: 0.5rem 0; font-size: 0.98rem; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: #94a3b8; padding: 0.4rem 0.5rem; border-bottom: 1px solid #e2e8f0; }}
  td {{ padding: 0.55rem 0.5rem; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  .hr {{ white-space: nowrap; text-align: right; }}
  th.hr {{ text-align: right; }}
  .footer {{ margin-top: 1.5rem; color: #94a3b8; font-size: 0.78rem; text-align: center; }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Salles occupées demain</h1>
    <div class="date">{titre_date}</div>
    {resume_html}
    {''.join(details_sections)}
    <div class="footer">Email automatique — Gestion des Salles CFPDC</div>
  </div>
</body>
</html>"""


def _occupations_du_jour(checker, date_cible: date) -> dict:
    """Récupère les occupations de toutes les salles pour une date."""
    occupations_par_salle = {}
    for salle in SALLES_ORDER:
        try:
            result = checker.get_all_occupations(salle, date_cible)
            occs = result.get("occupations", [])
            for o in occs:
                o["salle"] = salle
            occupations_par_salle[salle] = occs
        except Exception as e:
            print(f"[Notifications] Erreur récup occupations {salle}: {e}")
            occupations_par_salle[salle] = []
    return occupations_par_salle


def _envoyer_recap_a_destinataire(r: dict, date_cible: date, occupations_par_salle: dict, sujet: str) -> tuple:
    """
    Envoie (ou non) le récap personnalisé à UN destinataire.
    Retourne (status, detail) avec status ∈ {"sent", "ignored", "error"}.
    """
    weekday = date_cible.weekday()
    if weekday not in r.get("jours", preferences.JOURS):
        return "ignored", "jour désactivé"

    salles_suivies = r.get("salles", preferences.SALLES)
    occ_filtre = {
        s: occupations_par_salle.get(s, [])
        for s in salles_suivies
        if occupations_par_salle.get(s)
    }
    if not occ_filtre:
        return "ignored", "aucune salle suivie occupée"

    html = _html_recap(date_cible, occ_filtre)
    success, error = _envoyer_email([r["email"]], sujet, html)
    return ("sent", None) if success else ("error", error)


def envoyer_recap_quotidien(checker, date_cible: date = None) -> tuple:
    """
    Envoie, la veille pour le lendemain, un récap PERSONNALISÉ à chaque
    destinataire abonné selon ses préférences :
      - jours actifs (le récap n'est envoyé que si le jour cible est suivi) ;
      - salles suivies (filtrage du contenu) ;
      - aucun email si aucune des salles suivies n'est occupée.

    Retourne (success, info).
    """
    if not notifications_active():
        return False, "Notifications désactivées (SMTP non configuré)"

    if date_cible is None:
        date_cible = date.today() + timedelta(days=1)
    weekday = date_cible.weekday()

    recipients = preferences.get_recipients(checker)
    if not recipients:
        return False, "Aucun destinataire abonné avec email valide"

    occupations_par_salle = _occupations_du_jour(checker, date_cible)
    sujet = f"Salles occupées — {format_date_fr(date_cible)}"

    envoyes, ignores, erreurs = 0, 0, []
    for r in recipients:
        status, detail = _envoyer_recap_a_destinataire(r, date_cible, occupations_par_salle, sujet)
        if status == "sent":
            envoyes += 1
        elif status == "ignored":
            ignores += 1
        else:
            erreurs.append(f"{r['email']}: {detail}")

    if erreurs:
        return (envoyes > 0), f"{envoyes} envoyé(s), {ignores} ignoré(s). Erreurs: {'; '.join(erreurs)}"
    if envoyes == 0:
        return True, f"Aucun email à envoyer ({ignores} destinataire(s) ignoré(s) : aucune salle suivie occupée ou jour désactivé)"
    return True, f"{envoyes} récap(s) envoyé(s), {ignores} ignoré(s)"


# ═══════════════════════════════════════════════════════════
# CODE DE VÉRIFICATION — réinitialisation du mot de passe
# ═══════════════════════════════════════════════════════════
def envoyer_code_verification(email: str, code: str, nom: str = "") -> tuple:
    """
    Envoie un code de vérification à un utilisateur qui a oublié son mot de
    passe. Retourne (success, error).
    """
    if not notifications_active():
        return False, "Service email indisponible (SMTP non configuré). Contactez l'administrateur."
    if not email or "@" not in email:
        return False, "Adresse email invalide"

    salutation = f"Bonjour {nom}," if nom else "Bonjour,"
    sujet = "Votre code de vérification — Gestion des Salles CFPDC"
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; color: #1e293b; background: #f5f6f8; padding: 1.5rem; margin: 0; }}
  .wrap {{ max-width: 460px; margin: 0 auto; background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.75rem; }}
  h1 {{ font-size: 1.15rem; color: #0f172a; margin: 0 0 1rem; }}
  p {{ font-size: 0.95rem; line-height: 1.5; color: #334155; }}
  .code {{ font-size: 2rem; font-weight: 800; letter-spacing: 0.3em; text-align: center; color: #0f172a; background: #f1f5f9; border-radius: 10px; padding: 1rem; margin: 1.25rem 0; }}
  .note {{ font-size: 0.82rem; color: #64748b; }}
  .footer {{ margin-top: 1.5rem; color: #94a3b8; font-size: 0.78rem; text-align: center; }}
</style></head>
<body>
  <div class="wrap">
    <h1>Réinitialisation du mot de passe</h1>
    <p>{salutation}</p>
    <p>Voici votre code de vérification. Saisissez-le dans l'application pour définir un nouveau mot de passe :</p>
    <div class="code">{code}</div>
    <p class="note">Ce code est valable 10 minutes. Si vous n'êtes pas à l'origine de cette demande, ignorez cet email — votre mot de passe reste inchangé.</p>
  </div>
  <div class="footer">Email automatique — Gestion des Salles CFPDC</div>
</body>
</html>"""
    return _envoyer_email([email], sujet, html)


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
        # Mémorise, par utilisateur, la date du dernier traitement (envoi ou
        # ignoré) pour ne pas renvoyer deux fois le même jour.
        self._envois = {}

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
        print(f"[Notifications] Scheduler démarré — heure d'envoi par défaut {HEURE_ENVOI_QUOTIDIEN}h (personnalisable par utilisateur)")

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

        try:
            recipients = preferences.get_recipients(self.checker)
        except Exception as e:
            print(f"[Notifications] Erreur récupération destinataires: {e}")
            return
        if not recipients:
            return

        # Destinataires dont l'heure choisie est atteinte et pas encore traités aujourd'hui
        dus = [
            r for r in recipients
            if self._envois.get(r["username"]) != aujourdhui
            and maintenant.hour >= r.get("heure", HEURE_ENVOI_QUOTIDIEN)
        ]
        if not dus:
            return

        date_cible = aujourdhui + timedelta(days=1)
        occupations = _occupations_du_jour(self.checker, date_cible)
        sujet = f"Salles occupées — {format_date_fr(date_cible)}"

        for r in dus:
            try:
                status, detail = _envoyer_recap_a_destinataire(r, date_cible, occupations, sujet)
                if status in ("sent", "ignored"):
                    # Traité pour aujourd'hui (évite les renvois toutes les 15 min)
                    self._envois[r["username"]] = aujourdhui
                    if status == "sent":
                        print(f"[Notifications] Récap envoyé à {r['email']} (heure {r.get('heure')}h)")
                else:
                    print(f"[Notifications] Échec récap {r['email']}: {detail}")
            except Exception as e:
                print(f"[Notifications] Erreur envoi récap {r.get('email')}: {e}")