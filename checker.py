"""
Module de vérification de disponibilité des salles.
Logique métier complète pour lire les fichiers Excel et Google Sheets.
"""

import re
import os
from datetime import datetime, time, date
from openpyxl import load_workbook

# Import pour Google Sheets
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# Mapping des jours
DAY_MAPPING = {
    "lundi": "lundi",
    "mardi": "mardi",
    "mercredi": "mercredi",
    "jeudi": "jeudi",
    "vendredi": "vendredi",
    "vendredi (nuit)": "vendredi",
    "vendredi (soir)": "vendredi",
    "samedi": "samedi",
    "dimanche": "dimanche",
}

PYTHON_WEEKDAY_TO_FR = {
    0: "lundi",
    1: "mardi",
    2: "mercredi",
    3: "jeudi",
    4: "vendredi",
    5: "samedi",
    6: "dimanche"
}

SALLE_KEYWORDS = {
    "salle principale": ["principale", "principal"],
    "salle du fond": ["fond"],
    "salle du milieu": ["milieu"],
}


def normalize_day(cell_value: str) -> str:
    """Normalise une valeur de cellule vers un jour de la semaine."""
    if not cell_value:
        return ""
    val = str(cell_value).lower().strip()
    for key, day in DAY_MAPPING.items():
        if key in val:
            return day
    return val.split()[0] if val else ""


def nth_occurrence_in_month(d: date) -> int:
    """Retourne le rang de ce jour dans le mois (1er lundi = 1, 2ème lundi = 2, etc.)."""
    return (d.day - 1) // 7 + 1


def parse_horaire(horaire_str: str):
    """
    Parse une chaîne horaire et retourne (debut, fin).
    Gère les formats : "15H30 - 18H00", "22H-06H", "09H-12H", etc.
    """
    if not horaire_str:
        raise ValueError("Horaire vide")

    horaire_str = str(horaire_str).upper().replace(" ", "")
    parts = re.split(r"[-–]", horaire_str, maxsplit=1)
    if len(parts) != 2:
        raise ValueError(f"Horaire non parseable : {horaire_str}")

    def parse_time(s: str) -> time:
        s = s.strip().replace("H", ":")
        if s.endswith(":"):
            s += "00"
        if ":" not in s:
            s += ":00"
        h, m = s.split(":")
        return time(int(h), int(m) if m else 0)

    return parse_time(parts[0]), parse_time(parts[1])


def time_in_range(t: time, debut: time, fin: time) -> bool:
    """Vérifie si l'heure t est dans le créneau [debut, fin], avec gestion overnight."""
    if debut <= fin:
        return debut <= t <= fin
    else:
        # Overnight : le créneau va de debut jusqu'à minuit, puis de minuit jusqu'à fin
        return t >= debut or t <= fin


def salle_matches(cell_value: str, target_salle: str) -> bool:
    """Vérifie si une valeur de cellule correspond à une salle cible."""
    if not cell_value:
        return False
    salle_norm = str(cell_value).lower().strip()
    keywords = SALLE_KEYWORDS.get(target_salle, [target_salle])
    return any(kw in salle_norm for kw in keywords)


def parse_dates(date_cell):
    """
    Parse une ou plusieurs dates depuis une cellule.
    Retourne une liste de dates.
    """
    dates = []

    if date_cell is None:
        return dates

    # Si c'est déjà un datetime
    if isinstance(date_cell, datetime):
        return [date_cell.date()]

    # Si c'est une date
    if isinstance(date_cell, date):
        return [date_cell]

    # Si c'est une chaîne
    date_str = str(date_cell).strip()

    # Cas des multi-dates séparées par "et" ou ","
    separators = ['et', ',', 'et ', ', ']
    parts = [date_str]
    for sep in separators:
        new_parts = []
        for p in parts:
            new_parts.extend([x.strip() for x in p.split(sep) if x.strip()])
        parts = new_parts

    for part in parts:
        # Essayer différents formats
        formats_to_try = [
            '%d/%m/%y',    # 28/02/25
            '%d/%m/%Y',    # 28/02/2025
            '%Y-%m-%d',    # 2025-02-28
        ]

        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(part.strip(), fmt)
                dates.append(dt.date())
                break
            except ValueError:
                continue

    return dates


class SalleChecker:
    """Classe principale pour vérifier la disponibilité des salles."""

    def __init__(self, salles_dir: str, google_sheet_id: str = None):
        self.salles_dir = salles_dir
        self.salles_files = {
            "salle principale": f"{salles_dir}/SALLE_PRINCIPALE.xlsx",
            "salle du fond": f"{salles_dir}/SALLE_DU_FOND.xlsx",
            "salle du milieu": f"{salles_dir}/Salle_du_Milieu.xlsx",
        }

        # ID du Google Sheet pour les réservations (optionnel)
        self.google_sheet_id = google_sheet_id
        self._google_client = None

        # Cache pour les fichiers de salles (stables)
        self._salles_cache = {}

    def _get_google_client(self):
        """
        Initialise et retourne le client Google Sheets.
        Retourne (client, error) où error est None si succès, ou un message d'erreur string.
        """
        if not GSPREAD_AVAILABLE:
            return None, "Module gspread non installé"

        if self._google_client is not None:
            return self._google_client, None

        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']

            # Essayer de charger depuis Streamlit secrets (pour Streamlit Cloud)
            # ou depuis les variables d'environnement (pour Render)
            try:
                import streamlit as st
                if "google_credentials" in st.secrets:
                    creds_info = dict(st.secrets["google_credentials"])
                    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
                    self._google_client = gspread.authorize(creds)
                    return self._google_client, None
            except Exception:
                pass  # Pas sur Streamlit ou pas de secrets

            # Essayer depuis les variables d'environnement (Render)
            import os
            if os.environ.get("GOOGLE_CREDENTIALS_TYPE"):
                try:
                    private_key = os.environ.get("GOOGLE_CREDENTIALS_PRIVATE_KEY", "")
                    # Gérer plusieurs formats possibles de la clé
                    if "\\n" in private_key:
                        private_key = private_key.replace("\\n", "\n")
                    creds_info = {
                        "type": os.environ.get("GOOGLE_CREDENTIALS_TYPE"),
                        "project_id": os.environ.get("GOOGLE_CREDENTIALS_PROJECT_ID"),
                        "private_key_id": os.environ.get("GOOGLE_CREDENTIALS_PRIVATE_KEY_ID"),
                        "private_key": private_key,
                        "client_email": os.environ.get("GOOGLE_CREDENTIALS_CLIENT_EMAIL"),
                        "client_id": os.environ.get("GOOGLE_CREDENTIALS_CLIENT_ID"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
                    self._google_client = gspread.authorize(creds)
                    return self._google_client, None
                except Exception as e:
                    # Essayer avec un fichier secret si les variables échouent
                    import os
                    possible_paths = [
                        "/etc/secrets/google-credentials.json",
                        "/mnt/secrets/google-credentials.json",
                        "/secrets/google-credentials.json",
                        "google-credentials.json",
                    ]
                    for secret_path in possible_paths:
                        if os.path.exists(secret_path):
                            try:
                                creds = Credentials.from_service_account_file(secret_path, scopes=scopes)
                                self._google_client = gspread.authorize(creds)
                                return self._google_client, None
                            except Exception as file_error:
                                return None, f"Erreur fichier secret {secret_path}: {str(file_error)}"
                    return None, f"Erreur variables d'environnement: {str(e)}"

            # Sinon, chercher le fichier credentials.json local
            credentials_paths = [
                os.path.join(os.path.dirname(__file__), "credentials.json"),
                "/home/visiteur/projet_salles/credentials.json",
                "credentials.json",
            ]

            creds_path = None
            for path in credentials_paths:
                if os.path.exists(path):
                    creds_path = path
                    break

            if creds_path:
                creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
                self._google_client = gspread.authorize(creds)
                return self._google_client, None

            return None, "Aucune méthode d'authentification Google trouvée (ni secrets ni credentials.json)"

        except Exception as e:
            return None, f"Erreur connexion Google Sheets: {str(e)}"

    def _load_salle_data(self, salle_name: str):
        """Charge les données d'un fichier de salle avec mise en cache."""
        if salle_name in self._salles_cache:
            return self._salles_cache[salle_name]

        file_path = self.salles_files.get(salle_name)
        if not file_path:
            return []

        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active

            # Convertir en liste de lignes pour le cache
            data = list(ws.iter_rows(values_only=True))
            self._salles_cache[salle_name] = data
            return data
        except Exception as e:
            print(f"Erreur chargement {file_path}: {e}")
            return []

    def _build_name_index(self, rows) -> dict:
        """
        Pré-indexe toutes les lignes qui ont un nom en colonne N (index 13).
        Retourne un dict {row_index_0based: nom_occupant}.
        """
        name_index = {}
        for i, row in enumerate(rows):
            if row and len(row) > 13 and row[13] is not None:
                name = str(row[13]).strip()
                if name:
                    name_index[i] = name
        return name_index

    def _find_closest_occupant(self, row_idx: int, name_index: dict) -> str:
        """
        Retourne le nom de l'occupant dont la ligne est la plus proche de row_idx.
        """
        if not name_index:
            return "Inconnu"

        # Vérifier la distance maximale (20 lignes)
        closest_row = min(name_index.keys(), key=lambda r: abs(r - row_idx))
        distance = abs(closest_row - row_idx)

        if distance > 20:
            return "Occupant non identifié"

        return name_index[closest_row]

    def check_fixed_schedule(self, salle_name: str, d: date, time_requested: time) -> list:
        """
        Vérifie le planning fixe d'une salle pour une date et heure données.
        Retourne une liste d'occupations.
        """
        results = []
        rows = self._load_salle_data(salle_name)

        if not rows:
            return results

        # Construire l'index des noms d'occupants
        name_index = self._build_name_index(rows)

        # Déterminer le jour de la semaine
        day_name = PYTHON_WEEKDAY_TO_FR[d.weekday()]

        # Déterminer la semaine
        week_number = nth_occurrence_in_month(d)
        week_col_map = {1: 0, 2: 2, 3: 4, 4: 6}
        WEEK_COLS = [0, 2, 4, 6]

        in_5th_week_section = False

        for i, row in enumerate(rows):
            if not row:
                continue

            # Détecter section 5ème semaine
            if row[0] is not None and str(row[0]).strip().upper().startswith("EN PLUS"):
                in_5th_week_section = True
                continue

            # Si la ligne a un nom, on reste dans le bloc, sinon on continue
            # Le nom est trouvé via _find_closest_occupant

            # Déterminer la cellule jour à vérifier
            day_in_cell = None

            # Vérifier si la ligne a une valeur dans au moins une colonne semaine
            has_any_week_col = any(row[col] is not None for col in WEEK_COLS if col < len(row))

            # Vérifier si la ligne a un nom (colonne N = index 13)
            # Si oui, c'est une ligne de déclaration de bloc, pas une entrée de réservation
            has_name = len(row) > 13 and row[13] is not None and str(row[13]).strip()

            if has_any_week_col:
                # Entrée régulière → ignorer in_5th_week_section
                if week_number <= 4:
                    col_idx = week_col_map.get(week_number)
                    if col_idx is not None and col_idx < len(row):
                        day_in_cell = row[col_idx]
                else:
                    # Semaine 5 → une entrée régulière ne s'applique pas à la 5ème semaine
                    day_in_cell = None
            else:
                # Ligne sans colonne semaine → section "EN PLUS DES MOIS DE 5 DIMANCHES"
                # Cette section ne concerne que les DIMANCHES de la 5ème semaine
                if in_5th_week_section and week_number == 5 and not has_name and day_name == "dimanche":
                    # Ces entrées s'appliquent uniquement aux dimanches de la 5ème semaine
                    day_in_cell = day_name  # Force le match
                else:
                    day_in_cell = None

            if day_in_cell is None:
                continue

            # Normaliser et comparer le jour (si c'est une entrée régulière)
            if has_any_week_col:
                cell_day = normalize_day(str(day_in_cell))
                if cell_day != day_name:
                    continue

            # Trouver le nom de l'occupant le plus proche
            occupant = self._find_closest_occupant(i, name_index)

            # Extraire activité (colonne I = index 8) et horaire (colonne M = index 12)
            activite = str(row[8]).strip() if len(row) > 8 and row[8] else "Non précisée"
            horaire_str = str(row[12]).strip() if len(row) > 12 and row[12] else None

            if horaire_str is None:
                continue

            try:
                debut, fin = parse_horaire(horaire_str)

                # Gestion spéciale pour les créneaux overnight
                if time_in_range(time_requested, debut, fin):
                    results.append({
                        "occupant": occupant,
                        "activite": activite,
                        "horaire": horaire_str,
                        "debut": debut,
                        "fin": fin,
                        "source": "planning fixe"
                    })

            except ValueError:
                # Horaire non parseable → sécurité : considérer occupé
                results.append({
                    "occupant": occupant,
                    "activite": activite,
                    "horaire": horaire_str,
                    "debut": time(0, 0),
                    "fin": time(23, 59),
                    "source": "planning fixe",
                    "warning": "Horaire non parseable"
                })

        return results

    def _handle_horaire_cell(self, horaire_cell):
        """
        Gère une cellule horaire et retourne (debut, fin, label, is_parseable).
        - is_parseable = True si on a pu extraire des heures numériques
        - label = texte à afficher dans l'interface
        """
        if horaire_cell is None:
            return None, None, "Horaire non indiqué", False

        horaire_str = str(horaire_cell).strip()

        if not horaire_str:
            return None, None, "Horaire non indiqué", False

        # Tenter le parsing numérique
        try:
            debut, fin = parse_horaire(horaire_str)
            return debut, fin, horaire_str, True
        except Exception:
            # Pas parseable → afficher tel quel
            return None, None, horaire_str, False

    def check_reservations_google(self, salle_name: str, d: date, time_requested: time) -> tuple:
        """
        Vérifie les réservations depuis Google Sheets.
        Retourne (results, error) où error est None si succès.
        """
        results = []

        if not self.google_sheet_id or not GSPREAD_AVAILABLE:
            return results, None

        try:
            client, error = self._get_google_client()
            if error:
                return results, error
            if not client:
                return results, "Client Google Sheets non initialisé"

            # Ouvrir le spreadsheet et la feuille "Planning quotidien"
            spreadsheet = client.open_by_key(self.google_sheet_id)
            try:
                worksheet = spreadsheet.worksheet("Planning quotidien")
            except gspread.exceptions.WorksheetNotFound:
                # Essayer la première feuille si "Planning quotidien" n'existe pas
                worksheet = spreadsheet.get_worksheet(0)

            # Récupérer toutes les valeurs (à partir de la ligne 6 comme dans l'Excel)
            all_values = worksheet.get_all_values()

            for row_idx, row in enumerate(all_values[5:], start=6):  # Commencer à la ligne 6 (index 5)
                if len(row) < 5:
                    continue

                salle_cell = row[1] if len(row) > 1 else None  # Colonne B
                nom_cell = row[2] if len(row) > 2 else None    # Colonne C
                horaire_cell = row[3] if len(row) > 3 else None  # Colonne D
                date_cell = row[4] if len(row) > 4 else None    # Colonne E

                if not salle_cell or not date_cell:
                    continue

                # Vérifier la correspondance de la salle
                if not salle_matches(str(salle_cell).lower().strip(), salle_name):
                    continue

                # Parser la date
                dates = self._parse_date_from_sheet(date_cell)
                if d not in dates:
                    continue

                nom = str(nom_cell).strip() if nom_cell else "Inconnu"

                # Gérer l'horaire
                debut, fin, label, is_parseable = self._handle_horaire_cell(horaire_cell)

                if is_parseable:
                    if time_in_range(time_requested, debut, fin):
                        results.append({
                            "occupant": nom,
                            "activite": "Réservation ponctuelle",
                            "horaire": label,
                            "debut": debut,
                            "fin": fin,
                            "source": "réservation"
                        })
                else:
                    results.append({
                        "occupant": nom,
                        "activite": "Réservation ponctuelle",
                        "horaire": label,
                        "debut": time(0, 0),
                        "fin": time(23, 59),
                        "source": "réservation",
                        "warning": "Horaire non indiqué"
                    })

        except Exception as e:
            return results, f"Erreur lecture Google Sheets: {str(e)}"

        return results, None

    def _parse_date_from_sheet(self, date_cell):
        """Parse une date depuis Google Sheets (qui renvoie des chaînes)."""
        dates = []

        if not date_cell:
            return dates

        # Si c'est déjà un objet date/datetime (rare avec gspread mais possible)
        if isinstance(date_cell, (datetime, date)):
            return [date_cell.date() if isinstance(date_cell, datetime) else date_cell]

        # Sinon traiter comme une chaîne
        date_str = str(date_cell).strip()

        # Essayer de parser différents formats
        formats_to_try = [
            '%d/%m/%y',
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
        ]

        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(date_str, fmt)
                dates.append(dt.date())
                return dates
            except ValueError:
                continue

        return dates

    def check_reservations(self, salle_name: str, d: date, time_requested: time) -> tuple:
        """
        Vérifie les réservations extérieures pour une salle/date/heure.
        Retourne (occupations, error) où error est None si succès.
        """
        # Si un Google Sheet est configuré, l'utiliser en priorité
        if self.google_sheet_id:
            return self.check_reservations_google(salle_name, d, time_requested)

        # Sinon fallback sur le fichier Excel
        results = []

        try:
            wb = load_workbook(self.planning_file, data_only=True)

            if "Planning quotidien" not in wb.sheetnames:
                return results

            ws = wb["Planning quotidien"]
            rows = list(ws.iter_rows(min_row=6, values_only=True))

            for row in rows:
                if not row or len(row) < 5:
                    continue

                salle_cell = row[1]  # Colonne B
                nom_cell = row[2]    # Colonne C
                horaire_cell = row[3]  # Colonne D
                date_cell = row[4]   # Colonne E

                if salle_cell is None or date_cell is None:
                    continue

                # Vérifier la correspondance de la salle
                if not salle_matches(str(salle_cell).lower().strip(), salle_name):
                    continue

                # Parser la/les date(s)
                dates = parse_dates(date_cell)
                if d not in dates:
                    continue

                nom = str(nom_cell).strip() if nom_cell else "Inconnu"

                # Gérer l'horaire
                debut, fin, label, is_parseable = self._handle_horaire_cell(horaire_cell)

                if is_parseable:
                    # Horaire numérique → vérifier si dans le créneau
                    if time_in_range(time_requested, debut, fin):
                        results.append({
                            "occupant": nom,
                            "activite": "Réservation ponctuelle",
                            "horaire": label,
                            "debut": debut,
                            "fin": fin,
                            "source": "réservation"
                        })
                else:
                    # Horaire textuel ou non indiqué
                    results.append({
                        "occupant": nom,
                        "activite": "Réservation ponctuelle",
                        "horaire": label,
                        "debut": time(0, 0),
                        "fin": time(23, 59),
                        "source": "réservation",
                        "warning": "Horaire non indiqué"
                    })

        except Exception as e:
            return results, f"Erreur lecture réservations: {str(e)}"

        return results, None

    def get_all_fixed_occupations(self, salle_name: str, d: date) -> list:
        """
        Récupère TOUTES les occupations fixes d'une journée (sans filtrer par heure).
        """
        results = []
        rows = self._load_salle_data(salle_name)

        if not rows:
            return results

        # Construire l'index des noms d'occupants
        name_index = self._build_name_index(rows)

        day_name = PYTHON_WEEKDAY_TO_FR[d.weekday()]
        week_number = nth_occurrence_in_month(d)
        week_col_map = {1: 0, 2: 2, 3: 4, 4: 6}
        WEEK_COLS = [0, 2, 4, 6]

        in_5th_week_section = False

        for i, row in enumerate(rows):
            if not row:
                continue

            if row[0] is not None and str(row[0]).strip().upper().startswith("EN PLUS"):
                in_5th_week_section = True
                continue

            day_in_cell = None

            # Vérifier si la ligne a une valeur dans au moins une colonne semaine
            has_any_week_col = any(row[col] is not None for col in WEEK_COLS if col < len(row))

            # Vérifier si la ligne a un nom (colonne N = index 13)
            has_name = len(row) > 13 and row[13] is not None and str(row[13]).strip()

            if has_any_week_col:
                # Entrée régulière
                if week_number <= 4:
                    col_idx = week_col_map.get(week_number)
                    if col_idx is not None and col_idx < len(row):
                        day_in_cell = row[col_idx]
                else:
                    # Semaine 5 (hors dimanche) → pas d'occupation fixe
                    # Seul le dimanche de la 5ème semaine peut avoir des occupations (via section "EN PLUS")
                    day_in_cell = None
            else:
                # Ligne sans colonne semaine → section "EN PLUS DES MOIS DE 5 DIMANCHES"
                # Cette section ne concerne que les DIMANCHES de la 5ème semaine
                if in_5th_week_section and week_number == 5 and not has_name and day_name == "dimanche":
                    day_in_cell = day_name
                else:
                    day_in_cell = None

            if day_in_cell is None:
                continue

            if has_any_week_col:
                cell_day = normalize_day(str(day_in_cell))
                if cell_day != day_name:
                    continue

            # Trouver le nom de l'occupant le plus proche
            occupant = self._find_closest_occupant(i, name_index)

            activite = str(row[8]).strip() if len(row) > 8 and row[8] else "Non précisée"
            horaire_str = str(row[12]).strip() if len(row) > 12 and row[12] else None

            if horaire_str is None:
                continue

            try:
                debut, fin = parse_horaire(horaire_str)
                results.append({
                    "occupant": occupant,
                    "activite": activite,
                    "horaire": horaire_str,
                    "debut": debut,
                    "fin": fin,
                    "source": "planning fixe"
                })
            except ValueError:
                results.append({
                    "occupant": occupant,
                    "activite": activite,
                    "horaire": horaire_str,
                    "debut": time(0, 0),
                    "fin": time(23, 59),
                    "source": "planning fixe",
                    "warning": "Horaire non parseable"
                })

        return results

    def get_all_reservations_google(self, salle_name: str, d: date) -> tuple:
        """
        Récupère TOUTES les réservations ponctuelles depuis Google Sheets.
        Retourne (results, error) où error est None si succès.
        """
        results = []

        if not self.google_sheet_id or not GSPREAD_AVAILABLE:
            return results, None

        try:
            client, error = self._get_google_client()
            if error:
                return results, error
            if not client:
                return results, "Client Google Sheets non initialisé"

            spreadsheet = client.open_by_key(self.google_sheet_id)
            try:
                worksheet = spreadsheet.worksheet("Planning quotidien")
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.get_worksheet(0)

            all_values = worksheet.get_all_values()

            for row_idx, row in enumerate(all_values[5:], start=6):
                if len(row) < 5:
                    continue

                salle_cell = row[1] if len(row) > 1 else None
                nom_cell = row[2] if len(row) > 2 else None
                horaire_cell = row[3] if len(row) > 3 else None
                date_cell = row[4] if len(row) > 4 else None

                if not salle_cell or not date_cell:
                    continue

                if not salle_matches(str(salle_cell).lower().strip(), salle_name):
                    continue

                dates = self._parse_date_from_sheet(date_cell)
                if d not in dates:
                    continue

                nom = str(nom_cell).strip() if nom_cell else "Inconnu"

                debut, fin, label, is_parseable = self._handle_horaire_cell(horaire_cell)

                if is_parseable:
                    results.append({
                        "occupant": nom,
                        "activite": "Réservation ponctuelle",
                        "horaire": label,
                        "debut": debut,
                        "fin": fin,
                        "source": "réservation"
                    })
                else:
                    results.append({
                        "occupant": nom,
                        "activite": "Réservation ponctuelle",
                        "horaire": label,
                        "debut": time(0, 0),
                        "fin": time(23, 59),
                        "source": "réservation",
                        "warning": "Horaire non indiqué"
                    })

        except Exception as e:
            return results, f"Erreur lecture Google Sheets (get_all): {str(e)}"

        return results, None

    def get_all_reservations(self, salle_name: str, d: date) -> tuple:
        """
        Récupère TOUTES les réservations ponctuelles d'une journée (sans filtrer par heure).
        Retourne (results, error) où error est None si succès.
        """
        # Utiliser Google Sheets si configuré
        if self.google_sheet_id:
            return self.get_all_reservations_google(salle_name, d)

        results = []

        try:
            wb = load_workbook(self.planning_file, data_only=True)

            if "Planning quotidien" not in wb.sheetnames:
                return results

            ws = wb["Planning quotidien"]
            rows = list(ws.iter_rows(min_row=6, values_only=True))

            for row in rows:
                if not row or len(row) < 5:
                    continue

                salle_cell = row[1]
                nom_cell = row[2]
                horaire_cell = row[3]
                date_cell = row[4]

                if salle_cell is None or date_cell is None:
                    continue

                if not salle_matches(str(salle_cell).lower().strip(), salle_name):
                    continue

                dates = parse_dates(date_cell)
                if d not in dates:
                    continue

                nom = str(nom_cell).strip() if nom_cell else "Inconnu"

                # Gérer l'horaire avec la même logique
                debut, fin, label, is_parseable = self._handle_horaire_cell(horaire_cell)

                if is_parseable:
                    results.append({
                        "occupant": nom,
                        "activite": "Réservation ponctuelle",
                        "horaire": label,
                        "debut": debut,
                        "fin": fin,
                        "source": "réservation"
                    })
                else:
                    # Horaire textuel ou non indiqué
                    results.append({
                        "occupant": nom,
                        "activite": "Réservation ponctuelle",
                        "horaire": label,
                        "debut": time(0, 0),
                        "fin": time(23, 59),
                        "source": "réservation",
                        "warning": "Horaire non indiqué"
                    })

        except Exception as e:
            return results, f"Erreur lecture réservations: {str(e)}"

        return results, None

    def get_all_occupations(self, salle_name: str, d: date) -> dict:
        """
        Récupère TOUTES les occupations d'une journée (mode sans heure précise).
        Retourne un dict avec 'error' si la connexion Google Sheets a échoué.
        """
        fixed_occupations = self.get_all_fixed_occupations(salle_name, d)
        reservations, error = self.get_all_reservations(salle_name, d)
        all_occupations = fixed_occupations + reservations

        # Trier par heure de début
        all_occupations.sort(key=lambda x: x["debut"])

        result = {
            "salle": salle_name,
            "date": d,
            "occupations": all_occupations
        }
        if error:
            result["error"] = error
        return result

    def check_availability(self, salle_name: str, d: date, time_requested: time) -> dict:
        """
        Vérifie complètement la disponibilité d'une salle.
        Retourne un dict avec le statut et les détails.
        Ajoute 'error' si la connexion Google Sheets a échoué.
        """
        # Vérifier le planning fixe
        fixed_occupations = self.check_fixed_schedule(salle_name, d, time_requested)

        # Vérifier les réservations ponctuelles
        reservations, error = self.check_reservations(salle_name, d, time_requested)

        # Combiner toutes les occupations
        all_occupations = fixed_occupations + reservations

        # Déterminer le statut
        result = {
            "libre": not all_occupations,
            "salle": salle_name,
            "date": d,
            "heure": time_requested,
            "occupations": all_occupations
        }
        if error:
            result["error"] = error
        return result
