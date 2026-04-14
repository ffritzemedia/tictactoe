"""
Tic Tac Toe versus QBot
"""

# iOS: Locale früh absichern (einige Locales wie C.UTF-8 sind auf iOS nicht verfügbar)
import sys, os, locale
original_setlocale = locale.setlocale
def safe_setlocale(category, locale_str):
    try:
        return original_setlocale(category, locale_str)
    except locale.Error:
        pass # Fehler ignorieren, damit App nicht crasht
IS_IOS = (sys.platform == "ios")
if IS_IOS:
    for var in ("LC_ALL", "LC_CTYPE", "LANG"):
        val = os.environ.get(var, "")
        if val.upper().startswith("C.UTF-8") or val in ("", "C.UTF8"):
            os.environ.pop(var, None)
    locale.setlocale = safe_setlocale

import json
from pathlib import Path
import toga
from toga.style.pack import COLUMN, ROW, Pack

from .gui.board import Board
from .gui.player import Ch_Player
from .gui.autoplay import AutoPlay
from .gui.statusdisplay import StatusDisplay
from .resources.state import State
from .resources.qbot import QBot
from .resources.table import SQLTable, Local_DB


class TicTacToe(toga.App):
    # -------------------------
    # Pfad-/Datei-Helfer
    # -------------------------
    def app_data_dir(self) -> Path:
        """Beschreibbares App-Datenverzeichnis."""
        d = self.paths.data / "tictactoe"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _ensure_dir(self, path) -> Path:
        """Sorgt dafür, dass path als Verzeichnis existiert (Dateipfad -> parent)."""
        p = Path(path)
        if p.suffix and not p.name.endswith("/"):
            # Sieht aus wie eine Datei -> weiche auf parent aus
            p = p.parent
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _write_json(self, dirpath: Path, filename: str, data: dict) -> Path:
        """Schreibt JSON sicher in dirpath/filename und setzt restriktive Rechte, wenn möglich."""
        d = self._ensure_dir(dirpath)
        fp = d / filename
        with fp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        try:
            os.chmod(fp, 0o600)
        except Exception:
            pass
        return fp

    def _read_json_defaults(self, fp: Path, defaults: dict) -> dict:
        """Liest JSON, mapt nur bekannte Keys aus defaults, bleibt bei Fehlern robust."""
        try:
            if fp.exists():
                with fp.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    defaults.update({k: data.get(k, v) for k, v in defaults.items()})
        except Exception:
            pass
        return defaults

    # -------------------------
    # Defaults laden/speichern
    # -------------------------
    def _load_defaults_local(self) -> dict:
        """Lokale Defaults (Ablagepfad/Datei) aus app_data_dir/local_conf.json."""
        defaults = {
            "path": str(self.app_data_dir()),
            "file": "menace.json",
        }
        config_path = self.app_data_dir() / "local_conf.json"
        return self._read_json_defaults(config_path, defaults)

    def _save_defaults_local(self, values: dict) -> None:
        """Lokale Defaults speichern (local_conf.json in app_data_dir)."""
        self._write_json(self.app_data_dir(), "local_conf.json", values)

    def _load_sql_defaults(self, defaults_local: dict) -> dict:
        """SQL-Login-Defaults aus <path>/sql_login.json (fällt bei Problemen auf Defaults zurück)."""
        defaults = {
            "host": "host",
            "port": "3306",
            "user": "user",
            "pwd": "password",
            "db": "database",
            "table": "table",
        }
        cfg_dir = Path(defaults_local.get("path", str(self.app_data_dir())))
        cfg = cfg_dir / "sql_login.json"
        return self._read_json_defaults(cfg, defaults)

    def _save_sql_defaults(self, path: str, values: dict) -> None:
        """SQL-Login-Defaults nach <path>/sql_login.json speichern. Legt Ordner sauber an."""
        target_dir = Path(path)
        # iOS-Sandbox-Sicherheit: Wenn außerhalb des App-Datenordners, auf app_data_dir fallen
        try:
            if IS_IOS and not str(target_dir).startswith(str(self.app_data_dir())):
                target_dir = self.app_data_dir()
        except Exception:
            target_dir = self.app_data_dir()
        self._write_json(target_dir, "sql_login.json", values)

    def _ensure_local_file(self, folder: Path, filename: str) -> Path:
        """Sicherstellen, dass die lokale JSON-Datei existiert; leere anlegen, falls nötig."""
        folder = self._ensure_dir(folder)
        p = folder / filename
        if not p.exists():
            try:
                with p.open("w", encoding="utf-8") as f:
                    json.dump({}, f)
            except Exception:
                pass
        return p

    # -------------------------
    # App-Startup
    # -------------------------
    def startup(self):
        import traceback
        print("startup entered (iOS/macOS)")

        try:
            # Defaults laden
            defaults_local = self._load_defaults_local()
            # Wenn der gespeicherte Pfad nicht existiert, nutze App-Datenordner
            if not Path(defaults_local["path"]).exists():
                print("defaults_local path does not exist; using app data dir")
                defaults_local["path"] = str(self.app_data_dir())

            defaults = self._load_sql_defaults(defaults_local)

            def on_path_confirm(widget):
                nonlocal defaults, defaults_local
                new_path = path_input.value or defaults_local["path"]
                if not Path(new_path).exists():
                    new_path = str(self.app_data_dir())
                defaults_local["path"] = new_path
                path_input.value = new_path

                defaults = self._load_sql_defaults(defaults_local)
                host_input.placeholder = defaults["host"]
                port_input.placeholder = defaults["port"]
                user_input.placeholder = defaults["user"]
                pwd_input.placeholder = defaults["pwd"]
                db_input.placeholder = defaults["db"]
                table_input.placeholder = defaults["table"]

            # Eingabefelder
            print("building inputs")
            path_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults_local["path"], on_confirm=on_path_confirm)
            host_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults["host"])
            port_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults["port"])
            user_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults["user"])
            pwd_input = toga.PasswordInput(style=Pack(flex=1), placeholder=defaults["pwd"])
            db_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults["db"])
            table_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults["table"])
            file_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults_local["file"])

            # Callbacks
            def sql_confirm(widget):
                print("sql_confirm pressed")

                PATH = path_input.value or defaults_local["path"]
                HOST = host_input.value or defaults["host"]
                PORT = int(port_input.value) if port_input.value else int(defaults["port"])
                USER = user_input.value or defaults["user"]
                PWD = pwd_input.value or defaults["pwd"]
                DB = db_input.value or defaults["db"]
                TABLE = table_input.value or defaults["table"]

                self._save_sql_defaults(PATH, {"host": HOST, "port": PORT, "user": USER, "pwd": PWD, "db": DB, "table": TABLE})
                self._save_defaults_local({"path": PATH})

                # Spielobjekte
                board = Board()
                state = State()
                status_display = StatusDisplay()
                player = Ch_Player(state)
                board._player = player
                db_obj = SQLTable(HOST, PORT, USER, PWD, DB, TABLE)
                qbot = QBot(db_obj, state)
                board._state = state
                board._qbot = qbot
                auto = AutoPlay(qbot, board)
                board.status_display = status_display

                # Layout
                main_box = toga.Box(style=Pack(direction=ROW, align_items="start", flex=1))
                main_box.add(player.player)

                canvas_box = toga.Box(style=Pack(align_items="center", justify_content="center", flex=1))
                canvas_box.add(board.canvas)
                main_box.add(canvas_box)

                main_box.add(auto.autoplay_box)

                container = toga.Box(style=Pack(direction=COLUMN, align_items="start", flex=1))
                container.add(toga.Label("Tic Tac Toe", style=Pack(padding=10)))
                container.add(main_box)

                status_display_box = toga.Box(style=Pack(padding_bottom=20))
                status_display_box.add(toga.Box(style=Pack(flex=1)))
                status_display_box.add(status_display.status_box)
                status_display_box.add(toga.Box(style=Pack(flex=1)))
                container.add(status_display_box)

                self.main_window.content = container
                print("sql UI shown")

            def local_confirm(widget):
                print("local_confirm pressed")
            
                PATH = path_input.value or defaults_local["path"]
                FILE = file_input.value or defaults_local["file"]

                # iOS-Sandbox: Wenn Pfad außerhalb, auf App-Datenordner fallen
                target_dir = Path(PATH)
                if IS_IOS:
                    try:
                        if not str(target_dir).startswith(str(self.app_data_dir())):
                            print("PATH outside sandbox; using app data dir")
                            target_dir = self.app_data_dir()
                    except Exception:
                        target_dir = self.app_data_dir()

                self._save_defaults_local({"path": str(target_dir), "file": FILE})

                # Lokale JSON-Datei sichern/erstellen
                local_file = self._ensure_local_file(target_dir, FILE)

                # Spielobjekte
                board = Board()
                state = State()
                status_display = StatusDisplay()
                player = Ch_Player(state)
                board._player = player
                board.status_display = status_display

                db_obj = Local_DB(local_file=local_file)
                qbot = QBot(db_obj, state)
                board._state = state
                board._qbot = qbot
                auto = AutoPlay(qbot, board)

                # Layout
                main_box = toga.Box(style=Pack(direction=ROW, align_items="start", flex=1))
                main_box.add(player.player)

                canvas_box = toga.Box(style=Pack(align_items="center", justify_content="center", flex=1))
                canvas_box.add(board.canvas)
                main_box.add(canvas_box)

                main_box.add(auto.autoplay_box)

                v_box = toga.Box(style=Pack(direction=COLUMN, align_items="start", flex=1))
                v_box.add(toga.Label("Tic Tac Toe (Local)", style=Pack(padding=10)))
                v_box.add(main_box)

                status_display_box = toga.Box(style=Pack(padding_bottom=20))
                status_display_box.add(toga.Box(style=Pack(flex=1)))
                status_display_box.add(status_display.status_box)
                status_display_box.add(toga.Box(style=Pack(flex=1)))
                v_box.add(status_display_box)

                self.main_window.content = v_box
                print("local UI shown")

            def on_cancel(widget):
                print("quit pressed")
                self.exit()

            # UI: Cred-Box
            print("building cred_box")
            row_path_label = toga.Label("Config Path:")
            row_path = toga.Box(children=[toga.Label("Config Path:"), path_input], style=Pack(direction=ROW))
            row_sql_label = toga.Label("SQL Login:")
            row_host = toga.Box(children=[toga.Label("Host:"), host_input], style=Pack(direction=ROW))
            row_port = toga.Box(children=[toga.Label("Port:"), port_input], style=Pack(direction=ROW))
            row_user = toga.Box(children=[toga.Label("User:"), user_input], style=Pack(direction=ROW))
            row_pwd = toga.Box(children=[toga.Label("Password:"), pwd_input], style=Pack(direction=ROW))
            row_db = toga.Box(children=[toga.Label("Database:"), db_input], style=Pack(direction=ROW))
            row_table = toga.Box(children=[toga.Label("Table:"), table_input], style=Pack(direction=ROW))
            row_local_label = toga.Label("Local Play:")
            row_local = toga.Box(children=[toga.Label("JSON File:"), file_input], style=Pack(direction=ROW))

            btn_ok = toga.Button("sql", on_press=sql_confirm)
            btn_local = toga.Button("local", on_press=local_confirm)
            btn_cancel = toga.Button("quit", on_press=on_cancel)
            btn_row = toga.Box(children=[btn_ok, btn_local, btn_cancel], style=Pack(direction=ROW, padding_top=8))

            cred_box = toga.Box(
                children=[
                    row_path_label,
                    row_path,
                    row_sql_label,
                    row_host,
                    row_port,
                    row_user,
                    row_pwd,
                    row_db,
                    row_table,
                    btn_row,
                    row_local_label,
                    row_local,
                ],
                style=Pack(direction=COLUMN, flex=1, padding=12),
            )

            # Fenster erstellen und zeigen
            print("creating main_window")
            self.main_window = toga.MainWindow(title=self.formal_name)
            print("assign content")
            self.main_window.content = cred_box
            print("show window")
            self.main_window.show()
            print("UI shown ok")

        except Exception:
            traceback.print_exc()
            raise


def main():
    return TicTacToe()
