import sqlite3
import pandas as pd

def query_db(query: str, params: tuple = ()):
    conn = sqlite3.connect('prova.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Connessione al database
conn = sqlite3.connect('prova.db')
cursor = conn.cursor()

# Creazione delle tabelle per le serie calcolate
cursor.execute('''
    CREATE TABLE IF NOT EXISTS prova_media (
        TIME_PERIOD TEXT,
        SPECIES TEXT,
        media_OBS_VALUE FLOAT,
        PRIMARY KEY (TIME_PERIOD, SPECIES)
    )
''')


# Query per ottenere i dati necessari   
query_prova = "SELECT * FROM prova"

df_occupazione = query_db(query_prova)

prova_media= df_occupazione.groupby(['SPECIES', 'TIME_PERIOD'])['OBS_VALUE'].mean().reset_index()

prova_media.rename(columns={'OBS_VALUE': 'media_OBS_VALUE'}, inplace=True)

prova_media.to_sql('prova_media', conn, if_exists='replace', index=False)

conn.close()