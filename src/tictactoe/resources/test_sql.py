#import os
#import pymysql
from tictactoe.src.tictactoe.resources.table import SQLTable

db = SQLTable()
print(db.query_database())
print(db.show_tables())



'''
HOST = '192.168.1.7'
os.environ['DB_USER'] = 'menace'
os.environ['DB_PWD'] = '4123TelMi-XO-'
DB = 'menace_db'

def get_connection():
    return pymysql.connect(
        host=HOST,
        user=os.environ['DB_USER'],
        password=os.environ['DB_PWD'],
        database=DB
    )
    
def test_connection():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
        print("Connection test passed.")
    except Exception as e:
        print(f"Connection test failed: {e}")
    finally:
        conn.close()
        
test_connection()
'''