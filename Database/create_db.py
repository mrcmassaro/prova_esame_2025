import sqlite3

#Connessione al database
conn = sqlite3.connect('pesca.db')
cursor = conn.cursor()

# Creazione delle tabelle
cursor.execute('''
    CREATE TABLE IF NOT EXISTS regioni (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        area_geografica TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS occupazione (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Anno INTEGER  ,
        regione_id INTEGER,
        occupazione FLOAT,
        FOREIGN KEY (regione_id) REFERENCES regioni(id)
    )
    '''
)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS produttivita (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Anno INTEGER  ,
        regione_id INTEGER,
        produttivita FLOAT,
        FOREIGN KEY (regione_id) REFERENCES regioni(id)
    )                   
    '''
)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS economia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Anno INTEGER  ,
        regione_id INTEGER,
        importanza_economica FLOAT,
        FOREIGN KEY (regione_id) REFERENCES regioni(id)
    )                    
               
    '''
)

regioni = [
    ('Valle d\'Aosta', 'Nord-ovest'),
    ('Piemonte', 'Nord-ovest'),
    ('Liguria', 'Nord-ovest'),
    ('Lombardia', 'Nord-ovest'),
    ('Trentino-Alto Adige', 'Nord-est'),
    ('Veneto', 'Nord-est'),
    ('Friuli-Venezia Giulia', 'Nord-est'),
    ('Emilia-Romagna', 'Nord-est'),
    ('Toscana', 'Centro'),
    ('Umbria', 'Centro'),
    ('Marche', 'Centro'),
    ('Lazio', 'Centro'),
    ('Abruzzo', 'Centro'),
    ('Molise', 'Sud'),
    ('Campania', 'Sud'),
    ('Puglia', 'Sud'),
    ('Basilicata', 'Sud'),
    ('Calabria', 'Sud'),
    ('Sicilia', 'Isole'),
    ('Sardegna', 'Isole')
]

cursor.executemany('INSERT INTO regioni (nome, area_geografica) VALUES (?, ?)', regioni)

conn.commit()
conn.close()