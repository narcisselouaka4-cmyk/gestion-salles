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