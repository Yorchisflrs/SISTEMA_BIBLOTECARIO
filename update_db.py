import sqlite3

DATABASE = 'biblioteca.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def update_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE Usuarios ADD COLUMN foto BLOB")
            print("Columna 'foto' añadida a la tabla 'Usuarios'.")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print("La columna 'foto' ya existe en la tabla 'Usuarios'.")
            else:
                raise
        conn.commit()

if __name__ == "__main__":
    update_db()
