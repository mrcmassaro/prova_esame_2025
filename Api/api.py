from fastapi import FastAPI
from typing import Optional
import sqlite3
import pandas as pd

app = FastAPI(
    title='Pesca api',
    description='Api dedicate alle consegne a noi assegnate per effettuare delle analisi su dati inerenti alla pesca',
    version='1.0.0',
    contact={
        'name' : 'Marco Massaro',
        'email' : 'marco.massaro@edu.itspiemonte.it'
    }
)

def query_db(query: str, params: tuple = ()):
    conn = sqlite3.connect('pesca.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


@app.get("/produttivita")
def get_all_incidenza_spese():
    query = "SELECT * FROM produttivita" 
    params = []
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')

@app.get("/occupazione")
def get_all_partecipazione_popolazione():
    query = "SELECT * FROM occupazione" 
    params = []
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')

@app.get("/economia")
def get_all_sopravvivenza_imprese():
    query = "SELECT * FROM economia" 
    params = []
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')


@app.get("/prod_aree")
def get_produzione_aree(da_anno: Optional[int] = None, a_anno: Optional[int] = None):
    query = "SELECT anno, area_geografica, produttivita FROM Produttività_totala_aree "
    params = []
    if da_anno and a_anno:
        query += "WHERE anno BETWEEN ? AND ? "
        params.extend([da_anno, a_anno])
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')

@app.get("/prod_totale")
def get_produzione_nazionale(da_anno: Optional[int] = None, a_anno: Optional[int] = None):
    query = "SELECT anno, produttivita from Produttività_totale_nazionale "
    params = []
    if da_anno and a_anno:
        query += "WHERE anno BETWEEN ? AND ? "
        params.extend([da_anno, a_anno])
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')

@app.get("/media_valore_aggiunto")
def get_media_valore_aggiunto(da_anno: Optional[int] = None, a_anno: Optional[int] = None):
    query = "SELECT anno, area_geografica, importanza_economica from Media_valore_aggiunto_aree "
    params = []
    if da_anno and a_anno:
        query += "WHERE anno BETWEEN ? AND ? "
        params.extend([da_anno, a_anno])
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')

@app.get("/media_variazione_occupazione_nazionale")
def get_produzione_nazionale(da_anno: Optional[int] = None, a_anno: Optional[int] = None):
    query = "SELECT anno, occupazione from Media_variazione_percentuale_occupazione_nazionale "
    params = []
    if da_anno and a_anno:
        query += "WHERE anno BETWEEN ? AND ? "
        params.extend([da_anno, a_anno])
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')

@app.get("/media_variazione_occupazione_aree")
def get_produzione_nazionale(da_anno: Optional[int] = None, a_anno: Optional[int] = None):
    query = "SELECT anno, occupazione from Media_variazione_percentuale_occupazione_aree "
    params = []
    if da_anno and a_anno:
        query += "WHERE anno BETWEEN ? AND ? "
        params.extend([da_anno, a_anno])
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')

@app.get("/dati_brutti")
def get_dati_brutti(da_anno: Optional[int] = None, a_anno: Optional[int] = None, tabella: str = 'economia'):
    query = f"SELECT * FROM {tabella}"
    params = []
    if da_anno and a_anno:
        query += " WHERE anno BETWEEN ? AND ?"
        params.extend([da_anno, a_anno])
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')
