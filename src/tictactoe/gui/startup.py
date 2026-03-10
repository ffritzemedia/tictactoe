## wird derzeit nicht benutzt, Ziel app.py zu entschlanken.

import json
import os
from pathlib import Path
import toga
from toga.style import Pack
from..resources.table import SQLTable, Local_DB

class SQL_login():
    def __init__(self):
        # Load defaults from disk (sql_login.json in the package directory)
        self.package_dir = Path(__file__).resolve().parent
        self.config_path = self.package_dir / 'sql_login.json'
        self.db : SQLTable = None
        self.defaults = self.load_defaults()
        self.cred_window = toga.Window(title="SQL Login", size=(400, 300))  
        
    
    def load_defaults(self):
            defaults = {
                'host': 'host',
                'port': '3306',
                'user': 'user',
                'pwd': '',
                'db': 'database',
                'table': 'table',
            }
            try:
                if self.config_path.exists():
                    with self.config_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Only update host/user/db from disk — do NOT load a saved password
                        defaults.update({k: data.get(k, v) for k, v in defaults.items() if k != 'pwd'})
            except Exception:
                # If any error occurs, fall back to built-in defaults
                pass
            return defaults

    def save_defaults(self, values: dict):
        try:
            with self.config_path.open('w', encoding='utf-8') as f:
                json.dump(values, f, indent=2)
            try:
                os.chmod(self.config_path, 0o600)                
            except Exception:
                pass
        except Exception:
            pass
    
    def create_cred_window(self, app):
        host_input = toga.TextInput(style=Pack(flex=1), placeholder=self.defaults['host'])
        port_input = toga.TextInput(style=Pack(flex=1), placeholder=self.defaults['port'])
        user_input = toga.TextInput(style=Pack(flex=1), placeholder=self.defaults['user'])
        pwd_input = toga.PasswordInput(style=Pack(flex=1), placeholder=self.defaults['pwd'])
        db_input = toga.TextInput(style=Pack(flex=1), placeholder=self.defaults['db'])
        table_input = toga.TextInput(style=Pack(flex=1), placeholder=self.defaults['table'])

        def on_confirm(widget):
            HOST = host_input.value or self.defaults['host']
            PORT = port_input.value or self.defaults['port']
            USER = user_input.value or self.defaults['user']
            PWD = pwd_input.value or self.defaults['pwd']
            DB = db_input.value or self.defaults['db']
            TABLE = table_input.value or self.defaults['table']
            self.db = SQLTable(HOST, PORT, USER, PWD, DB, TABLE)
            values = {
                'host': HOST,
                'port': PORT,
                'user': USER,
                'pwd': '',
                'db': DB,
                'table': TABLE,
            }
            self.save_defaults(values)
            self.cred_window.close()
        
        def on_quit(widget):
            self.cred_window.close()
            self.exit()

        btn_ok = toga.Button('OK', on_press=on_confirm)
        btn_cancel = toga.Button('Quit', on_press=on_quit)
        btn_row = toga.Box(children=[btn_ok, btn_cancel], style=Pack(direction='row', padding=10, justify_content='space-between'))

        box = toga.Box(
            children=[
                host_input,
                port_input,
                user_input,
                pwd_input,
                db_input,
                table_input,
                btn_row
            ],
            style=Pack(direction='column', padding=10)
        )

        self.cred_window.content = box
        app.windows.add(self.cred_window)