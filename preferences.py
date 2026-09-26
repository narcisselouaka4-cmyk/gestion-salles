"""
Gestion des préférences utilisateur (notifications, etc.).
Stockage local dans un fichier JSON (pas de Google Sheet).
"""
import os
import json
import threading

PREFS_DIR = os.path.join(os.path.dirname(__file__), "preferences")
PREFS_FILE = os.path.join(PREFS_DIR, "preferences.json")

_lock = threading.Lock()

# Salles gérées (clés canoniques) et jours de la semaine (0 = lundi … 6 = dimanche)
SALLES = ["salle principale", "salle du fond", "salle du milieu"]
JOURS = [0, 1, 2, 3, 4, 5, 6]


def _load_all() -> dict:
    """Charge toutes les préférences depuis le fichier JSON."""
    try:
        with open(PREFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_all(data: dict):
    """Sauvegarde toutes les préférences dans le fichier JSON."""
    os.makedirs(PREFS_DIR, exist_ok=True)
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_pref(username: str, key: str, default=None):
    """Récupère une préférence pour un utilisateur."""
    with _lock:
        data = _load_all()
        user_prefs = data.get(username, {})
        return user_prefs.get(key, default)


def set_pref(username: str, key: str, value):
    """Définit une préférence pour un utilisateur."""
    with _lock:
        data = _load_all()
        if username not in data:
            data[username] = {}
        data[username][key] = value
        _save_all(data)


def is_subscribed(username: str) -> bool:
    """Indique si l'utilisateur est abonné aux notifications (défaut: True)."""
    return get_pref(username, "notifications", True)


def set_subscribed(username: str, subscribed: bool):
    """Active/désactive les notifications pour un utilisateur."""
    set_pref(username, "notifications", subscribed)


def get_notif_jours(username: str) -> list:
    """
    Jours (0=lundi … 6=dimanche) pour lesquels l'utilisateur veut recevoir
    le récap. Le jour concerné est le lendemain (date du récap).
    Défaut : tous les jours.
    """
    val = get_pref(username, "notif_jours", None)
    if not isinstance(val, list):
        return list(JOURS)
    return [j for j in val if j in JOURS]


def set_notif_jours(username: str, jours: list):
    """Définit les jours actifs pour les notifications."""
    set_pref(username, "notif_jours", [j for j in jours if j in JOURS])


def get_notif_salles(username: str) -> list:
    """
    Salles suivies par l'utilisateur pour les notifications.
    Défaut : toutes les salles.
    """
    val = get_pref(username, "notif_salles", None)
    if not isinstance(val, list):
        return list(SALLES)
    return [s for s in val if s in SALLES]


def set_notif_salles(username: str, salles: list):
    """Définit les salles suivies pour les notifications."""
    set_pref(username, "notif_salles", [s for s in salles if s in SALLES])


def get_user_email(username: str, checker=None) -> str:
    """
    Récupère l'email d'un utilisateur.
    Priorité : préférence locale, puis Google Sheet (si checker fourni).
    """
    email = get_pref(username, "email", "")
    if email:
        return email
    if checker is not None:
        try:
            return checker.get_user_email(username)
        except Exception:
            pass
    return ""


def set_user_email(username: str, email: str):
    """Enregistre l'email d'un utilisateur dans les préférences locales."""
    set_pref(username, "email", email)


def get_subscribed_emails(checker) -> list:
    """
    Récupère la liste des emails des utilisateurs abonnés.
    Combine préférences locales et Google Sheet.
    """
    emails = []
    # 1. Emails depuis les préférences locales (abonnés uniquement)
    data = _load_all()
    for username, prefs in data.items():
        if prefs.get("notifications", True) is True:
            email = prefs.get("email", "")
            if email and "@" in email:
                emails.append(email)

    # 2. Emails depuis le Google Sheet (pour les users sans préférence locale)
    if checker is not None:
        try:
            users = checker.get_users_google()
            for username, udata in users.items():
                # Si l'utilisateur a une préférence locale, on l'ignore ici
                if username in data:
                    continue
                email = (udata.get("email") or "").strip()
                if email and "@" in email:
                    emails.append(email)
        except Exception:
            pass

    # Dédupliquer
    return list(dict.fromkeys(emails))


def get_recipients(checker) -> list:
    """
    Retourne la liste des destinataires abonnés avec leurs préférences fines.
    Chaque entrée : {username, email, jours, salles}.

    Combine les préférences locales et l'onglet 'Utilisateurs' du Google Sheet.
    Les utilisateurs sans préférence locale reçoivent les valeurs par défaut
    (tous les jours, toutes les salles).
    """
    recipients = []
    seen_emails = set()
    data = _load_all()

    # 1. Utilisateurs avec préférences locales (abonnés uniquement)
    for username, prefs in data.items():
        if prefs.get("notifications", True) is not True:
            continue
        email = (prefs.get("email") or "").strip()
        if not email or "@" not in email:
            continue
        if email in seen_emails:
            continue
        seen_emails.add(email)
        recipients.append({
            "username": username,
            "email": email,
            "jours": get_notif_jours(username),
            "salles": get_notif_salles(username),
        })

    # 2. Utilisateurs du Google Sheet sans préférence locale (défauts)
    if checker is not None:
        try:
            users = checker.get_users_google()
            for username, udata in users.items():
                if username in data:
                    continue
                email = (udata.get("email") or "").strip()
                if not email or "@" not in email:
                    continue
                if email in seen_emails:
                    continue
                seen_emails.add(email)
                recipients.append({
                    "username": username,
                    "email": email,
                    "jours": list(JOURS),
                    "salles": list(SALLES),
                })
        except Exception:
            pass

    return recipients