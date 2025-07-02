import pandas as pd
import os
import requests
from io import StringIO
import sqlite3

# URL
occupazione_url = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/fish_ld_it?format=SDMX-CSV'

curr_dir = os.getcwd()
csv_dir = os.path.join(curr_dir, 'Dati/csv')

print(f"Directory corrente: {csv_dir}")

def import_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        csv_content = StringIO(response.text)
        df = pd.read_csv(csv_content, sep=',')
        df.columns = [col.replace('�', 'à') for col in df.columns]
        return df
    else:
        print(f"Errore nell'importazione dei dati da {url}")
        return None

def save_df_local(df, filename):
    os.makedirs(csv_dir, exist_ok=True)
    path = os.path.join(csv_dir, filename)
    df.to_csv(path, index=False, encoding = 'utf-8')
    print(f"Dataframe salvati in {path}")

df_occupazione = import_data(occupazione_url)

df_occupazione = df_occupazione.rename(columns={"LAST UPDATE":"LAST_UPDATE"})

save_df_local(df_occupazione, 'occupazione.csv')

# print(df_occupazione)

# Funzione per normalizzare i dati mancanti tramite interpolazione
def interpolate_missing_data(df, columns):
    for col in columns:
        df[col] = df[col].interpolate(method='linear')
    return df

conn = sqlite3.connect('prova.db')
cursor = conn.cursor()

for _, row in df_occupazione.iterrows():
    cursor.execute('INSERT INTO prova (GEO, TIME_PERIOD, OBS_VALUE, SPECIES) VALUES (?, ?, ? , ?)',
                   (row['geo'], row['TIME_PERIOD'], row['OBS_VALUE'], row['species']))

conn.commit()
conn.close()

