import sqlite3
from sqlite3 import Error
from pathlib import Path

# La base de datos se creará en data/metadata/parlamentarios.db
DB_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "metadata" / "parlamentarios.db"

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        # Asegurarse de que el directorio de metadata exista
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        return conn
    except Error as e:
        print(f"Error conectando a la base de datos: {e}")
    return conn

def create_tables(conn):
    """Crea las tablas en la base de datos si no existen."""
    try:
        cursor = conn.cursor()
        
        # Tabla de Parlamentarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS parlamentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            party TEXT,
            chamber TEXT,
            region TEXT,
            profile_url TEXT,
            local_photo_path TEXT,
            photo_checksum TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Tabla de Embeddings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            embedding_path TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES parlamentarios (person_id)
        );
        """)

        # Tabla de Apariciones en TV
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS apariciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT NOT NULL,
            channel_name TEXT NOT NULL,
            start_timestamp TIMESTAMP NOT NULL,
            duration_seconds INTEGER NOT NULL,
            confidence_score REAL,
            FOREIGN KEY (person_id) REFERENCES parlamentarios (person_id)
        );
        """)
        conn.commit()
    except Error as e:
        print(f"Error creando las tablas: {e}")

def insert_or_update_parlamentario(conn, data):
    """
    Inserta un nuevo parlamentario o actualiza si la foto cambió.
    Retorna 'INSERT', 'UPDATE', o 'SKIP'.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT photo_checksum FROM parlamentarios WHERE person_id = ?", (data['person_id'],))
    result = cursor.fetchone()

    if result is None:
        # No existe, insertar
        cursor.execute("""INSERT INTO parlamentarios (person_id, full_name, party, chamber, region, profile_url, local_photo_path, photo_checksum)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                       (data['person_id'], data['full_name'], data['party'], data['chamber'], data['region'], data['profile_url'], str(data['local_photo_path']), data['photo_checksum']))
        conn.commit()
        return "INSERT"
    else:
        # Existe, comprobar checksum
        if result[0] != data['photo_checksum']:
            # Checksum diferente, actualizar
            cursor.execute("""UPDATE parlamentarios SET 
                            full_name = ?, party = ?, chamber = ?, region = ?, profile_url = ?, 
                            local_photo_path = ?, photo_checksum = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE person_id = ?""",
                           (data['full_name'], data['party'], data['chamber'], data['region'], data['profile_url'], str(data['local_photo_path']), data['photo_checksum'], data['person_id']))
            conn.commit()
            return "UPDATE"
        else:
            return "SKIP"

if __name__ == '__main__':
    # Si se ejecuta este script directamente, crea la DB y las tablas
    connection = create_connection()
    if connection:
        print(f"Base de datos creada en: {DB_FILE}")
        create_tables(connection)
        print("Tablas creadas exitosamente.")
        connection.close()

