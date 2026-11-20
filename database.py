import sqlite3

DB_FILE= "solar_calculator.db"
def create_table():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS capacity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            place TEXT NOT NULL,
            matched TEXT,
            latitude REAL,
            longitude REAL,
            peakpower REAL NOT NULL,
            tilt INTEGER NOT NULL,
            aspect REAL NOT NULL,
            loss INTEGER NOT NULL,
            yearly_kwh REAL
        )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_statistics (
            run_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            energy_kwh REAL,
            irradiation REAL,
            FOREIGN KEY (run_id) REFERENCES capacity(id)
        )
    """)
   
    connection.commit()
    connection.close()

#adding systems
def add_system(username, place, matched, lat, lon, peakpower, tilt, aspect, loss, result):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO capacity (username, place, matched, latitude, longitude, peakpower, tilt, aspect, loss, yearly_kwh) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (username, place, matched, lat, lon, peakpower, tilt, aspect, loss,
         result["yearly_kwh"]),
    )
    run_id = cursor.lastrowid
    cursor.executemany(
        "INSERT INTO monthly_statistics (run_id, month, energy_kwh, irradiation) "
        "VALUES (?, ?, ?, ?)",
        [(run_id, m["month"], m["energy_kwh"], m["irradiation"]) for m in result["monthly"]],
    )
    connection.commit()
    connection.close()
    return run_id

#reading sytem values
def get_system():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM capacity ORDER BY id DESC")
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


# reading monthly values
def load_monthly(run_ids):
    if not run_ids:
        return []
    marks = ",".join("?" * len(run_ids))
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(
        f"""SELECT m.run_id, m.month, m.energy_kwh, m.irradiation, c.place
            FROM monthly_statistics m JOIN capacity c ON c.id = m.run_id
            WHERE m.run_id IN ({marks}) ORDER BY m.run_id, m.month""",
        list(run_ids),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]

#update capacity
def update_capacity(system_id, place, matched, lat, lon, peakpower, tilt, aspect, loss, result):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE capacity SET place=?, matched=?, latitude=?, longitude=?, "
        "peakpower=?, tilt=?, aspect=?, loss=?, yearly_kwh=? WHERE id=?",
        (place, matched, lat, lon, peakpower, tilt, aspect, loss,
         result["yearly_kwh"], system_id),
    )
    if cursor.rowcount == 0:          # no system with that id
        connection.close()
        return False

    cursor.execute("DELETE FROM monthly_statistics WHERE run_id=?", (system_id,))
    cursor.executemany(
        "INSERT INTO monthly_statistics (run_id, month, energy_kwh, irradiation) "
        "VALUES (?, ?, ?, ?)",
        [(system_id, m["month"], m["energy_kwh"], m["irradiation"]) for m in result["monthly"]],
    )
    connection.commit()
    connection.close()
    return True

#deleting an entry
def delete_capacity(system_id):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM monthly_statistics WHERE run_id=?", (system_id,))
    cursor.execute("DELETE FROM capacity WHERE id=?", (system_id,))
    connection.commit()
    connection.close()
