import pandas as pd
import sqlite3

conn = sqlite3.connect('pesca.db')

def interpolate_missing_data(df, columns):
    for col in columns:
        df[col] = df[col].interpolate(method='linear')
    return df

# Interpolazione dei dati mancanti
for table, column in [('occupazione', 'occupazione'),
                      ('economia', 'importanza_economica'),
                      ('produttivita', 'produttivita')]:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    df = interpolate_missing_data(df, [column])
    df.to_sql(table, conn, if_exists='replace', index=False)

conn.close()