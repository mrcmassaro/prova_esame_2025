import sqlite3

#Connessione al database
conn = sqlite3.connect('prova.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS prova (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        GEO TEXT,
        TIME_PERIOD INT,
        OBS_VALUE FLOAT,
        SPECIES TEXT
    );
    '''
)


cursor.execute('CREATE INDEX IF NOT EXISTS index_time_period ON prova (TIME_PERIOD)')

conn.commit()
conn.close()