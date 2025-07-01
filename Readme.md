--------------------------------------
FASE 1 : IMPORTAZIONE DEI DATI
--------------------------------------

La prima cosa da fare nel progetto è creare uno script in pyhton che ci permetta di scaricare un file csv partendo da un url.
Bisogna specificare la cartella corrente e la cartella in cui si vogliono inserire i file csv tramite os.

Dopodiche si creano 2 funzioni :
1) una per importare i dati;
2) una per salvare i dati, trasformati in df, in locale nella cartella specificata precendentemente in formato csv.

--------------------------------------
FASE 2 : CREAZIONE DEL PRIMO DB
--------------------------------------

Una volta finite di fare le operazioni della fase 1, il passo successivo è la creazione di un db a partire dal df creato precedentemente.
La creazione del db avviene tramite l'utilizzo di sqlite3, una libreria che permette di creare database embedded (integrati) direttamente tramite python,
attraverso l'utilizzo dei cursori, entità in grado di connetersi ai db e di eseguire comandi.

--------------------------------------
FASE 3 : INSERIMENTO DATI NEL DB
--------------------------------------

Prima di inserire i dati del csv nel db, dobbiamo fare in modo che questi ultimi siano effettivamente utili e non nulli.
Per questo motivi abbiamo creato una funzione che in base al dataframe inserito e ad una lista di colonne vada a controllare queste ultime 
per fare in modo che non ci siano buchi tra i dati.

Una volta effettuata questa operazione, tramite sqlite3 verranno inseriti i dati all'interno della tabella creata precedentemente.