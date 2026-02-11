import sqlite3
import os

DB_PATH = "C:\\dev\\RAR_V1\\v5_cantera_oro.db"

def inspect_schema():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(cantera_productos)")
        columns = cursor.fetchall()
        print("Columns in cantera_productos:")
        for col in columns:
            print(col)
            
    except Exception as e:
        print(f"Error inspecting schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_schema()
