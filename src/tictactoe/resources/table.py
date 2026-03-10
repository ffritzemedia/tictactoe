import os
import pymysql
import json
import pathlib
from pathlib import Path

class SQLTable:
    def __init__(self, host, port, user, pwd, db, table):
        self.host = host
        self.port : int = port
        self.user = user
        self.pwd = pwd
        self.database = db
        self.table = table
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.pwd,
                database=self.database
            )
            if not self.show_tables().__contains__(self.table):
                self.create_matchboxes()
        except pymysql.MySQLError as e:
            self.connection = None
    
    def __del__(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def create_matchboxes(self):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {self.table} (
                            state VARCHAR(9) PRIMARY KEY,
                            moves VARCHAR(50) NOT NULL
                        )
                    """)
                self.connection.commit()
                print(f"{self.table} table created or already exists.")
            except pymysql.MySQLError as e:
                print(f"Error creating {self.table} table: {e}")
        else:
            print("No database connection.")
    
    def query_database(self):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT DATABASE()")
                    db = cursor.fetchone()
                    return db[0]
            except pymysql.MySQLError as e:
                print(f"Error querying database: {e}")
                return None
        else:
            print("No database connection.")
            return None
    
    def show_tables(self):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    return [table[0] for table in tables]
            except pymysql.MySQLError as e:
                print(f"Error fetching tables: {e}")
                return []
        else:
            print("No database connection.")
            return []
        
    def clear_all_tables(self):
        tables = self.show_tables()
        for table in tables:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                self.connection.commit()
                print(f"Table {table} cleared.")
            except pymysql.MySQLError as e:
                print(f"Error clearing table {table}: {e}")
        else:
            print("No database connection.")
            
    def empty_active_table(self):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(f"TRUNCATE TABLE {self.table}")
                self.connection.commit()
                print(f"Table {self.table} emptied.")
            except pymysql.MySQLError as e:
                print(f"Error emptying table {self.table}: {e}")
        else:
            print("No database connection.")
            
    def has_state(self, state):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM matchboxes WHERE state=%s", (state,))
                    result = cursor.fetchone()
                    return result is not None
            except pymysql.MySQLError as e:
                print(f"Error checking state: {e}")
                return False
        else:
            print("No database connection.")
            return False

    def set_state(self, state, moves):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("INSERT INTO matchboxes (state, moves) VALUES (%s, %s)", (state, moves))
                self.connection.commit()
                print("State set in database.")
            except pymysql.MySQLError as e:
                print(f"Error setting state: {e}")
        else:
            print("No database connection.")

    def get_moves(self, state):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT moves FROM matchboxes WHERE state=%s", (state,))
                    result = cursor.fetchone()
                    return result[0] if result else None
            except pymysql.MySQLError as e:
                print(f"Error retrieving moves: {e}")
                return None
        else:
            print("No database connection.")
            return None
        
    def update_moves(self, state, moves):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("UPDATE matchboxes SET moves=%s WHERE state=%s", (moves, state))
                self.connection.commit()
                print("Moves updated in database.")
            except pymysql.MySQLError as e:
                print(f"Error updating moves: {e}")
        else:
            print("No database connection.")
            
class Local_DB():
    def __init__(self, local_file):
        self.datapath = Path(local_file)
        
    def has_state(self, state):
        if self.datapath.exists():
            try:
                with self.datapath.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    return state in data
            except Exception as e:
                print(f"Error checking state in local DB: {e}")
                return False
        else:
            print("Local database file does not exist.")
            return False
        
    def set_state(self, state, moves):
        data = {}
        if self.datapath.exists():
            try:
                with self.datapath.open('r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading local DB: {e}")
        data[state] = moves
        try:
            with self.datapath.open('w', encoding='utf-8') as f:
                json.dump(data, f)
            print("State set in local DB.")
        except Exception as e:
            print(f"Error writing to local DB: {e}")
            
    def get_moves(self, state):
        if self.datapath.exists():
            try:
                with self.datapath.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(state, None)
            except Exception as e:
                print(f"Error retrieving moves from local DB: {e}")
                return None
        else:
            print("Local database file does not exist.")
            return None
        
    def update_moves(self, state, moves):
        data = {}
        if self.datapath.exists():
            try:
                with self.datapath.open('r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading local DB: {e}")
        data[state] = moves
        try:
            with self.datapath.open('w', encoding='utf-8') as f:
                json.dump(data, f)
            print("Moves updated in local DB.")
        except Exception as e:
            print(f"Error writing to local DB: {e}")