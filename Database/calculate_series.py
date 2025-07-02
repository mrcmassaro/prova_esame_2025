import sqlite3
import pandas as pd

def query_db(query: str, params: tuple = ()):
    conn = sqlite3.connect('pesca.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Connessione al database
conn = sqlite3.connect('pesca.db')
cursor = conn.cursor()

# Creazione delle tabelle per le serie calcolate
# Prima richiesta
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Produttività_totala_aree (
        anno INTEGER,
        area_geografica TEXT,
        produttivita_totale FLOAT,
        PRIMARY KEY (anno, area_geografica)
    )
''')

# Seconda richiesta
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Produttività_totale_nazionale (
        anno INTEGER,
        produttivita_totale FLOAT,
        PRIMARY KEY (anno)
    )
''')

# Terza richiesta
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Media_valore_aggiunto_aree (
        anno INTEGER,
        area_geografica TEXT,
        media_valore_aggiunto_perc FLOAT,
        PRIMARY KEY (anno, area_geografica)
    )
''')

#Quarta richiesta
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Media_variazione_percentuale_occupazione_nazionale (
        anno INTEGER,
        media_valore_lavoro FLOAT,
        PRIMARY KEY (anno)
    )       
''')

#Quinta richiesta
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Media_variazione_percentuale_occupazione_aree (
        anno INTEGER,
        area_geografica TEXT,
        media_alore_lavoro FLOAT,
        PRIMARY KEY (anno, area_geografica)
    )       
''')


# Query per ottenere i dati necessari   
query_regione = "SELECT * FROM regioni"
query_occupazione = "SELECT * FROM occupazione"
query_produttivita = "SELECT * FROM produttivita"
query_economia = "SELECT * FROM economia"

df_regione = query_db(query_regione)
df_occupazione = query_db(query_occupazione)
df_produttivita = query_db(query_produttivita)
df_economia = query_db(query_economia)

df_produttivita = pd.merge(df_produttivita, df_regione, left_on='regione_id', right_on='id')
df_occupazione= pd.merge(df_occupazione, df_regione, left_on='regione_id', right_on='id')
df_economia = pd.merge(df_economia, df_regione, left_on='regione_id', right_on='id')

#Primi 2 punti
produttivita_aree = df_produttivita.groupby(['Anno', 'area_geografica'])['produttivita'].sum().reset_index()
produttivita_nazionale = df_produttivita.groupby(['Anno'])['produttivita'].sum().reset_index()
# print(produttivita_aree)
#print(produttivita_nazionale)

# 3 punto
economia_media_valore_aggiunto = df_economia.groupby(['Anno', 'area_geografica'])['importanza_economica'].mean().reset_index()
#print(economia_media_valore_aggiunto)

# 4 Punto
occupazione_nazionale = df_occupazione.groupby(['Anno'])['occupazione'].mean().reset_index()
# print(occupazione_nazionale)

#5 punto
occupazione_aree = df_occupazione.groupby(['Anno', 'area_geografica'])['occupazione'].mean().reset_index()
# print(occupazione_aree)

# prova_media.to_sql('prova_media', conn, if_exists='replace', index=False)

produttivita_aree.to_sql('Produttività_totala_aree', conn, if_exists='replace', index=False)
produttivita_nazionale.to_sql('Produttività_totale_nazionale', conn, if_exists='replace', index=False)
economia_media_valore_aggiunto.to_sql('Media_valore_aggiunto_aree', conn, if_exists='replace', index=False)
occupazione_nazionale.to_sql('Media_variazione_percentuale_occupazione_nazionale', conn, if_exists='replace', index=False)
occupazione_aree.to_sql('Media_variazione_percentuale_occupazione_aree', conn, if_exists='replace', index=False)

conn.close()