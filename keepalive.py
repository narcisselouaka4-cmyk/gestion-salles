"""
Keep-alive pour éviter la mise en veille de l'app sur les hébergeurs gratuits
(Render free : le conteneur s'endort après ~15 min sans trafic entrant).

Un thread daemon interroge périodiquement l'URL PUBLIQUE de l'app (via l'edge
de l'hébergeur), ce qui compte comme du trafic entrant et garde l'instance
éveillée. Sans URL publique (ex. en local), le keep-alive ne démarre pas.

Configuration (variables d'environnement) :
  RENDER_EXTERNAL_URL  — fournie automatiquement par Render (ex: https://xxx.onrender.com)
  KEEPALIVE_URL        — pour forcer une URL précise (prioritaire sur RENDER_EXTERNAL_URL)
  KEEPALIVE_INTERVAL   — intervalle entre deux pings, en secondes (défaut 600 = 10 min)
  KEEPALIVE_ENABLED    — "false" pour désactiver
"""

import os
import threading
import urllib.request


class KeepAlive:
    """Thread daemon (singleton) qui ping l'URL publique pour rester éveillé."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self, url: str, interval: int):
        self.url = url.rstrip("/")
        self.interval = interval
        self._thread = None
        self._stop_event = threading.Event()

    @classmethod
    def _resolve_url(cls) -> str:
        return (
            os.environ.get("KEEPALIVE_URL")
            or os.environ.get("RENDER_EXTERNAL_URL")
            or ""
        ).strip()

    @classmethod
    def demarrer(cls):
        """Démarre le keep-alive si une URL publique est disponible et l'option activée."""
        if os.environ.get("KEEPALIVE_ENABLED", "true").lower() == "false":
            return None
        url = cls._resolve_url()
        if not url or not url.startswith("http"):
            return None

        with cls._lock:
            if cls._instance is not None and cls._instance._thread and cls._instance._thread.is_alive():
                return cls._instance
            try:
                interval = int(os.environ.get("KEEPALIVE_INTERVAL", "600"))
            except (TypeError, ValueError):
                interval = 600
            interval = max(60, interval)
            cls._instance = cls(url, interval)
            cls._instance._start_thread()
            return cls._instance

    def _start_thread(self):
        self._thread = threading.Thread(target=self._boucle, daemon=True)
        self._thread.start()
        print(f"[KeepAlive] Démarré — ping {self.url} toutes les {self.interval}s")

    def _boucle(self):
        # On attend un premier intervalle avant de commencer (laisse l'app démarrer).
        while not self._stop_event.wait(self.interval):
            self._ping()

    def _ping(self):
        # L'endpoint de santé de Streamlit répond vite et sans authentification.
        target = self.url + "/_stcore/health"
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "cfpdc-keepalive"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp.read(1)
        except Exception as e:
            print(f"[KeepAlive] Ping échoué ({target}) : {e}")

    def arreter(self):
        self._stop_event.set()
