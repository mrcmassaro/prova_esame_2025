from fastapi import FastAPI
from typing import Optional
import sqlite3
import pandas as pd

app = FastAPI(
    title='Prova api',
    description='Prima prova fatta per vedere le api su python',
    version='1.0.0',
    contact={
        'name' : 'Marco Massaro',
        'email' : 'marco.massaro@edu.itspiemonte.it'
    }
)

def query_db(query: str, params: tuple = ()):
    conn = sqlite3.connect('prova.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

@app.get("/prova_media")
def get_prova(da_anno: Optional[int] = None, a_anno: Optional[int] = None):
    query = "SELECT GEO TEXT, TIME_PERIOD, OBS_VALUE, SPECIES FROM prova "
    params = []
    if da_anno and a_anno:
        query += "WHERE TIME_PERIOD BETWEEN ? AND ? "
        params.extend([da_anno, a_anno])
    df = query_db(query, tuple(params))
    return df.to_dict(orient='records')