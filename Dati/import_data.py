import pandas as pd
import os
import requests
from io import StringIO
import sqlite3

# URL
occupazione_url = 'https://raw.githubusercontent.com/Lollo110204/DataAnalisysPython/main/Dati_csv/Andamento-occupazione-del-settore-della-pesca-per-regione.csv'
produttivita_url = 'https://raw.githubusercontent.com/Lollo110204/DataAnalisysPython/main/Dati_csv/Produttivita-del-settore-della-pesca-per-regione.csv'
economia_url = 'https://raw.githubusercontent.com/Lollo110204/DataAnalisysPython/main/Dati_csv/Importanza-economica-del-settore-della-pesca-per-regione.csv'

curr_dir = os.getcwd()
csv_dir = os.path.join(curr_dir, 'Dati/csv')

print(f"Directory corrente: {csv_dir}")

def import_data(url):   
    response = requests.get(url)
    if response.status_code == 200:
        csv_content = StringIO(response.text)
        df = pd.read_csv(csv_content, sep=';')
        df.columns = [col.replace('�', 'à') for col in df.columns]
        return df
    else:
        print(f"Errore nell'importazione dei dati da {url}")
        return None

def save_df_local(df:pd.DataFrame, filename):
    path = os.path.join(csv_dir, filename)
    df.to_csv(path, index=False, encoding = 'utf-8')
    print(f"Dataframe salvati in {path}")

df_occupazione = import_data(occupazione_url)
df_produttivita = import_data(produttivita_url)
df_economia = import_data(economia_url)

df_occupazione = df_occupazione.rename(columns={"Variazione percentuale unitŕ di lavoro della pesca":"Valore_lavoro"})
df_produttivita = df_produttivita.rename(columns={"Produttivitŕ in migliaia di euro":"Valore_produttivita"})
df_economia = df_economia.rename(columns={"Percentuale valore aggiunto pesca-piscicoltura-servizi":"Valore_aggiunto"})

save_df_local(df_occupazione, 'occupazione.csv')
save_df_local(df_produttivita, 'produttivita.csv')
save_df_local(df_economia, 'economia.csv')

# ---------------------------------------------------------------

# print(df_occupazione)

# Funzione per normalizzare i dati mancanti tramite interpolazione
def interpolate_missing_data(df, columns):
    for col in columns:
        df[col] = df[col].interpolate(method='linear')
    return df

conn = sqlite3.connect('pesca.db')
cursor = conn.cursor()

for _, row in df_occupazione.iterrows():
    regione_id = cursor.execute("SELECT id FROM regioni WHERE nome = ?", (row['Regione'],)).fetchone()[0] 
    cursor.execute('INSERT INTO occupazione ( Anno, regione_id, occupazione ) VALUES (?, ?, ? )',
                   (row['Anno'], regione_id, row['Valore_lavoro']))
    
for _, row in df_produttivita.iterrows():
    regione_id = cursor.execute("SELECT id FROM regioni WHERE nome = ?", (row['Regione'],)).fetchone()[0] 
    cursor.execute('INSERT INTO produttivita ( Anno, regione_id, produttivita ) VALUES (?, ?, ? )',
                   (row['Anno'], regione_id, row['Valore_produttivita']))
    
for _, row in df_economia.iterrows():
    regione_id = cursor.execute("SELECT id FROM regioni WHERE nome = ?", (row['Regione'],)).fetchone()[0] 
    cursor.execute('INSERT INTO economia ( Anno, regione_id, importanza_economica ) VALUES (?, ?, ? )',
                   (row['Anno'], regione_id, row['Valore_aggiunto']))

conn.commit()
conn.close()

