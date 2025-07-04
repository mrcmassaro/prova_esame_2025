------------------------------------------------------------------------------------------------------
FASE 1 : IMPORTAZIONE DEI DATI  ----------> import_data.py
------------------------------------------------------------------------------------------------------

La prima cosa da fare nel progetto è creare uno script in pyhton che ci permetta di scaricare un file csv partendo da un url.
Se il raw proviene dal github, basta copiare l'url della pagine in cui è contenuto e modificarlo sostituendo la parte 
subito dopo l'https con questa raw.githubusercontent.com e togliendo la parte relativa al blob.
Bisogna specificare la cartella corrente e la cartella in cui si vogliono inserire i file csv tramite os.

Dopodiche si creano 2 funzioni :
1) una per importare i dati;
2) una per salvare i dati, trasformati in df, in locale nella cartella specificata precendentemente in formato csv.

------------------------------------------------------------------------------------------------------
FASE 2 : CREAZIONE DEL PRIMO DB  ----------> create_db.py
------------------------------------------------------------------------------------------------------

Una volta finite di fare le operazioni della fase 1, il passo successivo è la creazione di un db a partire dal df creato precedentemente.
La creazione del db avviene tramite l'utilizzo di sqlite3, una libreria che permette di creare database embedded (integrati) direttamente tramite python,
attraverso l'utilizzo dei cursori, entità in grado di connetersi ai db e di eseguire comandi.

Per velocizzare le operazioni dei db creiamo degli indici sulle colonne che sapremo di usare.

Per visualizzare il db facilmente usare l'estensione di vscode: Sqlite viewer

------------------------------------------------------------------------------------------------------
FASE 3 : INSERIMENTO DATI NEL DB  ----------> import_data.py
------------------------------------------------------------------------------------------------------

Prima di inserire i dati del csv nel db, dobbiamo fare in modo che questi ultimi siano effettivamente utili e non nulli.
Per questo motivi abbiamo creato una funzione che in base al dataframe inserito e ad una lista di colonne vada a controllare queste ultime 
per fare in modo che non ci siano buchi tra i dati.

Una volta effettuata questa operazione, tramite sqlite3 verranno inseriti i dati all'interno della tabella creata precedentemente.

------------------------------------------------------------------------------------------------------
FASE 4 : Creazione di tabelle specifiche per le serie  ----------> calculate_series.py
------------------------------------------------------------------------------------------------------

Dopo aver inserito i dati nella tabella, possiamo usarli per fare delle analisi specifiche su diversi argomenti.
In questo caso, faremo una prova sulla media di OBS_VALUE risultante dal raggruppamento delle colonne SPECIES e TIME_PERIOD.
Prima di iniziare dovremo però fare una funzione che ci permetta di leggere all'interno del db embedded le nostre query.

def query_db(query: str, params: tuple = ()):
    conn = sqlite3.connect('prova.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

Una volta creata questa funzione possiamo creare una tabella campione, chiamata prova_media, e creeremo una variabile che contenga la stringa con il comando da eseguire.

Verrà quindi creata una nuova variabile che chiama la funzione scritta in precedenza, passandogli come parametri la stringa con il comando, per ottenere i dati derivanti da esso.

Dopo questa operazione verranno inseriti i dati nella tabella appena creata.

------------------------------------------------------------------------------------------------------
FASE 5 : Pulizia dei dati   ----------> post_process.py
------------------------------------------------------------------------------------------------------

Dopo aver inserito nelle seconda tabella i nostri dati campione, c'è bisogno di effettuare una pulizia di questi ultimi.
Questa operazione avverrà attraverso l'utilizzo di una funzione da utilizzare in un ciclo for che sarà in grado di leggere il nome della tabella da utilizzare e le colonne sulla quale verrà fatta la pulizia dei dati.

------------------------------------------------------------------------------------------------------
FASE 5 : Creazione delle api  ----------> api.py
------------------------------------------------------------------------------------------------------

Per far funzionare le api ci serve un enviroment virtuale che creeremo usando questo comando, python -m venv venv.

Per attivare la macchina virtuale si usa questo comando .\(nome-venv)\Scripts\Activate.ps1   . 
Nel caso questo comando dia un errore bisogna usare questo prima dell'attivazione della venv Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Una volta fatte queste operezioni bisogna importare le librerie necessarie per far funzionare le librerie del modulo delle api.

Una volta importate potremo eseguire il comando che ci permetterà di visualizzare sul browser le nostre api, uvicorn Api.api:app --reload
uvicorn (nome_della_cartella , se non si trova nella parte principale).(nome_del_file):app --reload

uvicorn Api.api:app --reload

------------------------------------------------------------------------------------------------------
FASE 6 : Analisi dei dati----------> Notebook.ipynb
------------------------------------------------------------------------------------------------------

Per la parte di analisi dei dati, utilizzeremo Jupiter, utile per la sua struttura modulare.
In questa parte dovremo dividere in diversi moduli la nostra analisi.
Nel primo mopdulo dovranno esserci le importazioni delle librerie che verranno utilizzate inj questo file.
Nei moduli seguenti andremo a leggere i csv di cui siamo interessati e andremo ad inserire i loro dati dentro dei dataframe che verranno visualizzati tramite display().
Nel caso serva prima dell'analisi andremo a rinominare le colonne scritte in maniera errata.
Dopodiche potremo effettuare le nostre analisi in base alle varie richieste. 
Di norma ciò avviene creando nuovi df in cui sulla base dei precedenti vengono fatte varie operazioni.
Infine vengono fatti i grafici veri e proprio attraverso la libreria plotly.express




------------------------------------------------------------------------------------------------------
PUNTI DI FORZA DEL PROGETTO
------------------------------------------------------------------------------------------------------

La parte di importazione dei dati garantisce che i dati presi tramite url siano sempre aggiornati.

-------------------------------------------------------------------------------------------------------

Struttura ordinata e modulare

-------------------------------------------------------------------------------------------------------

create_db.py: definisce la struttura di base dei dati (regioni, produttività, occupazione, economia). È un primo step chiaro: crea un database SQLite relazionale ben normalizzato.

calculate_series.py: prende i dati grezzi, li trasforma (merge, gruppi, medie, somme) e popola nuove tabelle di serie calcolate. Così separi dati grezzi e aggregati.

api.py: espone i dati tramite un’API FastAPI. Quindi rendi questi dati interrogabili da frontend, dashboard o altre applicazioni.

-------------------------------------------------------------------------------------------------------

Database normalizzato e geograficamente dettagliato

-------------------------------------------------------------------------------------------------------

Usare le aree geografiche per aggregare regioni permette di:

Fare analisi per macroaree (Nord, Centro, Sud, Isole).

Facilitare confronti territoriali.

Ridurre complessità: non lavori sempre sui dettagli regionali, ma puoi risalirci.

-------------------------------------------------------------------------------------------------------

API REST standard

-------------------------------------------------------------------------------------------------------

Esporre i dati tramite FastAPI:

Ti permette di connettere i dati a strumenti di visualizzazione (Tableau, Power BI, Grafana, frontend custom).

Usa filtri parametrici (es. da_anno e a_anno): rispondi solo coi dati necessari.

È un approccio moderno, compatibile con CI/CD e cloud.

