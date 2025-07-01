import sqlite3

#Connessione al database
conn = sqlite3.connect('prova.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS occupazione (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        GEO TEXT,
        TIME_PERIOD TEXT,
        OBS_VALUE FLOAT,
        SPECIES TEXT
    );
    '''
)

conn.commit()
conn.close()