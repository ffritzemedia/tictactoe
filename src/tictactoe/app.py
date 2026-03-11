"""
Tic Tac Toe versus QBot
"""
import locale
original_setlocale = locale.setlocale
def safe_setlocale(category, locale_str):
    try:
        return original_setlocale(category, locale_str)
    except locale.Error:
        pass  # Ignore unsupported locale
locale.setlocale = safe_setlocale
import toga
import json
import os
from pathlib import Path
from toga.style.pack import COLUMN, ROW, Pack
from .gui.board import Board
from .gui.player import Ch_Player
from .gui.autoplay import AutoPlay
from .gui.statusdisplay import StatusDisplay
from .resources.state import State
from .resources.qbot import QBot
from .resources.table import SQLTable, Local_DB


class TicTacToe(toga.App):
    def startup(self):
        # progarm folder
        prog_dir = Path(__file__).resolve().parent
        # Load defaults from disk (sql_login.json in the package directory)
        home_docs = Path.home() / 'Documents'
        #package_dir = home_docs / 'tictactoe'
        # ensure the folder in Documents exists so we can store the config there
        #try:
        #    package_dir.mkdir(parents=True, exist_ok=True)
        #except Exception:
        #    pass
        #package_dir = Path(__file__).resolve().parent
        #config_path = package_dir / 'sql_login.json'

        def load_defaults():
            defaults = {
                'host': 'host',
                'port': '3306',
                'user': 'user',
                'pwd': 'password',
                'db': 'database',
                'table': 'table',
            }
            try:
                if (Path(defaults_local['path']) / 'sql_login.json').exists():
                    print("Loading SQL login from Documents folder")
                    with (Path(defaults_local['path']) / 'sql_login.json').open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        defaults.update({k: data.get(k, v) for k, v in defaults.items()})
            except Exception:
                # If any error occurs, fall back to built-in defaults
                pass
            return defaults

        def load_defaults_local():
            defaults = {
                'path': str(home_docs / 'tictactoe'),
                'file': 'menace.json',
            }
            config_dir = Path(defaults['path'])
            config_dir.mkdir(parents=True, exist_ok=True)
            full_path = config_dir / 'local_conf.json'
            try:
                if full_path.exists():
                    with full_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        defaults.update({k: data.get(k, v) for k, v in defaults.items()})
            except Exception:
                # If any error occurs, fall back to built-in defaults
                pass
            return defaults
        
        def save_defaults(path, values: dict):
            config_dir = Path(path)
            config_dir.mkdir(parents=True, exist_ok=True)  # Ordner anlegen
            config_path = config_dir / 'sql_login.json'
            try:
                with config_path.open('w', encoding='utf-8') as f:
                    json.dump(values, f, indent=2)
                # chmod nur dort, wo sinnvoll
                try:
                    if os.name != 'nt':  # nicht unter Windows
                        os.chmod(config_path, 0o600)
                except Exception:
                    pass
            except Exception:
                pass
            
        def save_defaults_local(values: dict):
            config_dir = Path(values.get('path', home_docs / 'tictactoe'))
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / 'local_conf.json'
            try:
                with config_path.open('w', encoding='utf-8') as f:
                    json.dump(values, f, indent=2)
                try:
                    if os.name != 'nt':
                        os.chmod(config_path, 0o600)
                except Exception:
                    pass
            except Exception:
                pass
        
        defaults_local = load_defaults_local()
        defaults = load_defaults()

        path_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults_local['path'])
        host_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults['host'])
        port_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults['port'])
        user_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults['user'])
        pwd_input = toga.PasswordInput(style=Pack(flex=1), placeholder=defaults['pwd'])
        db_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults['db'])
        table_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults['table'])
        file_input = toga.TextInput(style=Pack(flex=1), placeholder=defaults_local['file'])

        def sql_confirm(widget): # OK button pressed (SQL login confirmed)
            PATH = path_input.value or defaults_local['path']
            HOST = host_input.value or defaults['host']
            PORT = int(port_input.value) if port_input.value else int(defaults['port'])
            USER = user_input.value or defaults['user']
            PWD = pwd_input.value or defaults['pwd']
            DB = db_input.value or defaults['db']
            TABLE = table_input.value or defaults['table']

            # Persist the entered values so next startup uses them
            # Persist only host/user/db; do NOT persist the password
            save_defaults(PATH, {'host': HOST, 'port': PORT, 'user': USER, 'pwd': PWD, 'db': DB, 'table': TABLE})
            save_defaults_local({'path': PATH})

            # Klassen erstellen und gegenseitig verlinken
            board = Board()
            state = State()
            status_display = StatusDisplay()
            player = Ch_Player(state)
            board._player = player
            db = SQLTable(HOST, PORT, USER, PWD, DB, TABLE)
            qbot = QBot(db, state)
            board._state = state
            board._qbot = qbot
            auto = AutoPlay(qbot, board)
            # link status display to board so board can update it on game end
            board.status_display = status_display

            main_box = toga.Box(style=Pack(direction=ROW, align_items='start', flex=1))
            main_box.add(player.player)
            main_box.add(board.canvas)
            main_box.add(auto.autoplay_box)
            # Wrap in a container so the window content itself can expand
            container = toga.Box(style=Pack(direction=COLUMN, align_items='start', flex=1))
            container.add(main_box)
            status_display_box = toga.Box(style=Pack(margin_bottom=20))
            status_display_box.add(toga.Box(style=Pack(flex=1)))
            status_display_box.add(status_display.status_box)
            status_display_box.add(toga.Box(style=Pack(flex=1)))
            container.add(status_display_box)
            self.main_window.content = container

        def local_confirm(widget): # Local play button pressed
            PATH = path_input.value or defaults_local['path']
            FILE = file_input.value or defaults_local['file']

            # Persist the entered config path so next startup uses it
            save_defaults_local({'path': PATH, 'file': FILE})

            # Klassen erstellen und gegenseitig verlinken
            board = Board()
            state = State()
            status_display = StatusDisplay()
            player = Ch_Player(state)
            board._player = player
            board.status_display = status_display
            if not (Path(PATH) / FILE).exists():
                # create empty file
                try:
                    with (Path(PATH) / FILE).open('w', encoding='utf-8') as f:
                        json.dump({}, f)
                except Exception:
                    pass
            db = Local_DB(local_file=Path(PATH) / FILE)
            qbot = QBot(db, state)
            board._state = state
            board._qbot = qbot
            auto = AutoPlay(qbot, board)

            main_box = toga.Box(style=Pack(direction=ROW, align_items='start', flex=1))
            main_box.add(player.player)
            canvas_box = toga.Box(style=Pack(align_items='center', justify_content='center', flex=1))
            canvas_box.add(board.canvas)
            main_box.add(canvas_box)
            main_box.add(auto.autoplay_box)
            v_box = toga.Box(style=Pack(direction=COLUMN, align_items='start', flex=1))
            #v_box.add(toga.Box(style=Pack(flex=1)))
            v_box.add(main_box)
            status_display_box = toga.Box(style=Pack(margin_bottom=20))
            status_display_box.add(toga.Box(style=Pack(flex=1)))
            status_display_box.add(status_display.status_box)
            status_display_box.add(toga.Box(style=Pack(flex=1)))
            v_box.add(status_display_box)
            self.main_window = toga.MainWindow(title=self.formal_name)
            self.main_window.content = v_box
            
        def on_cancel(widget): # Cancel button pressed (SQL login cancelled)
            self.exit()

        row_path_label = toga.Label('Config Path:')
        row_path = toga.Box(children=[toga.Label('Config Path:'), path_input], style=Pack(direction=ROW))
        row_sql_label = toga.Label('SQL Login:')
        row_host = toga.Box(children=[toga.Label('Host:'), host_input], style=Pack(direction=ROW))
        row_port = toga.Box(children=[toga.Label('Port:'), port_input], style=Pack(direction=ROW))
        row_user = toga.Box(children=[toga.Label('User:'), user_input], style=Pack(direction=ROW))
        row_pwd = toga.Box(children=[toga.Label('Password:'), pwd_input], style=Pack(direction=ROW))
        row_db = toga.Box(children=[toga.Label('Database:'), db_input], style=Pack(direction=ROW))
        row_table = toga.Box(children=[toga.Label('Table:'), table_input], style=Pack(direction=ROW))
        row_local_label = toga.Label('Local Play:')
        row_local = toga.Box(children=[toga.Label('JSON File:'), file_input], style=Pack(direction=ROW))
        

        btn_ok = toga.Button('sql', on_press=sql_confirm) # SQL login confirmed
        btn_local = toga.Button('local', on_press=local_confirm) # Local play confirmed
        btn_cancel = toga.Button('quit', on_press=on_cancel) # SQL login cancelled
        btn_row = toga.Box(
            children=[btn_ok, btn_local, btn_cancel],
            style=Pack(direction=ROW, padding_top=10, spacing=8)
        )

        cred_box = toga.Box(children=[row_path_label, 
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
                                      row_local
                                      ], style=Pack(direction=COLUMN))

        # Ensure the application has a main_window object before showing other windows
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = cred_box
        self.main_window.show()


def main():
    return TicTacToe()
