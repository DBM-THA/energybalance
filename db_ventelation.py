import sqlite3

DB_NAME = "ventilation.db"


def init_db():
    """Erstellt die DB und füllt Standardwerte, falls leer."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kategorien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bezeichnung TEXT UNIQUE,
        std_personen REAL,
        std_luftwechsel REAL,
        std_h_tag REAL,
        std_d_jahr REAL
    );
    """)
    conn.commit()

    # Standardwerte prüfen und anlegen
    cursor.execute("SELECT COUNT(*) FROM kategorien")
    if cursor.fetchone()[0] == 0:
        defaults = [
            ("Wohngebäude", 4, 0.5, 24, 365),
            ("Büro (Einzel)", 1, 0.7, 12, 200),
            ("Großraumbüro", 1.5, 1.2, 12, 200),
            ("Besprechung", 10, 2.0, 4, 200),
            ("Schule/Klasse", 25, 1.0, 8, 200),
            ("Kita", 15, 1.0, 10, 250),
            ("Flur/Verkehr", 0, 0.2, 12, 250),
            ("Lager", 0, 0.2, 8, 250),
            ("WC/Sanitär", 0, 2.0, 12, 250),
            ("Kantine", 50, 4.0, 4, 220)
        ]
        cursor.executemany("""
            INSERT INTO kategorien (bezeichnung, std_personen, std_luftwechsel, std_h_tag, std_d_jahr) 
            VALUES (?, ?, ?, ?, ?)
        """, defaults)
        conn.commit()

    conn.close()


def get_kategorien_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT bezeichnung FROM kategorien ORDER BY bezeichnung ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_kategorie_defaults(bezeichnung):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT std_personen, std_luftwechsel, std_h_tag, std_d_jahr FROM kategorien WHERE bezeichnung = ?",
                   (bezeichnung,))
    row = cursor.fetchone()
    conn.close()
    return row