# GUIDA PER DOCUMENTO DI ANALISI SOFTWARE

## 1. INTRODUZIONE

L'introduzione deve fornire una panoramica completa del sistema sviluppato, contestualizzando il progetto e illustrando chiaramente gli obiettivi raggiunti. È importante descrivere non solo cosa è stato realizzato, ma anche il perché delle scelte tecnologiche effettuate.

### Struttura consigliata con esempio:

**Descrizione del sistema**: Iniziate presentando il dominio applicativo e il problema che il software risolve.

*Esempio*: "Il sistema LibraryAPI è stato sviluppato per digitalizzare i processi di gestione di una biblioteca universitaria. Il sistema sostituisce i tradizionali registri cartacei con un'interfaccia digitale che permette di catalogare libri, gestire utenti registrati e monitorare i prestiti attivi. L'obiettivo principale è automatizzare le operazioni quotidiane riducendo errori manuali e migliorando l'efficienza del personale bibliotecario."

**Stack tecnologico motivato**: Non limitatevi a elencare le tecnologie, ma spiegate le ragioni delle scelte.

*Esempio*: "FastAPI è stato scelto come framework web per tre ragioni principali: la generazione automatica della documentazione OpenAPI che facilita l'integrazione, le performance superiori a Flask grazie all'architettura asincrona, e il supporto nativo per type hints Python che migliora la robustezza del codice. SQLite è stato preferito a PostgreSQL per la semplicità di deployment e l'assenza di configurazioni server complesse, appropriato per il volume di dati previsto (circa 10.000 libri e 500 utenti). "

**Obiettivi e scope**: Definite chiaramente cosa il sistema fa e, altrettanto importante, cosa non fa.

*Esempio*: "Il sistema implementa le operazioni CRUD per tre entità principali (User, Book, Loan) attraverso API REST. Include autenticazione JWT, sistema di ruoli base (user/admin), e ricerca libri per titolo/autore. Il sistema NON include: gestione finanziaria per multe, integrazione con sistemi esterni, notifiche email automatiche, o supporto per contenuti multimediali."

**Sfide principali**: Identificate le problematiche più significative affrontate durante lo sviluppo.

*Esempio*: "Le sfide principali hanno riguardato l'implementazione sicura delle query SQL per prevenire injection attacks, la gestione della concorrenza per i prestiti simultanei dello stesso libro, e l'equilibrio tra semplicità architetturale e robustezza del sistema."

---

## 2. ARCHITETTURA E STRUTTURA DEL PROGETTO

L'analisi dell'architettura deve spiegare come è stato organizzato il codice e perché, mostrando comprensione dei principi di progettazione software.

### Organizzazione modulare

La struttura del progetto riflette una separazione chiara delle responsabilità:

```
library-api/
├── app/
│   ├── routers/          # Endpoint API per dominio
│   │   ├── books.py      # GET/POST/PUT/DELETE per libri
│   │   ├── users.py      # Gestione utenti e autenticazione
│   │   └── loans.py      # Sistema prestiti e restituzioni
│   ├── crud.py           # Operazioni database con SQL nativo
│   ├── security.py       # JWT e hashing password
│   └── schemas.py        # Validazione Pydantic
```

La cartella routers implementa il principio di Single Responsibility, dove ogni file gestisce un singolo dominio funzionale. Questo facilita la manutenzione perché modifiche alle funzionalità dei libri non impattano il sistema di prestiti.

*Esempio di separazione delle responsabilità*:

```python
# routers/books.py - Solo operazioni sui libri
@router.get("/books/{book_id}")
def get_book(book_id: int):
    return BookCRUD.get_book_by_id(book_id)

# routers/loans.py - Solo operazioni sui prestiti  
@router.post("/loans/")
def create_loan(loan_data: LoanCreate):
    return LoanCRUD.create_loan(loan_data)
```

### Gestione delle dipendenze

L'implementazione del pattern [Dependency Injection]([Dependency injection - Wikipedia](https://it.wikipedia.org/wiki/Dependency_injection)) attraverso [FastAPI]([Dependencies - FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/)) centralizza la gestione delle risorse:

```python
def get_db_connection():
    with sqlite3.connect("library.db") as conn:
        conn.row_factory = sqlite3.Row
        yield conn

@router.get("/books/{book_id}")
def get_book(book_id: int, db = Depends(get_db_connection)):
    return BookCRUD.get_book_by_id(db, book_id)
```

Questo approccio facilita il testing permettendo di sostituire la dipendenza reale con un mock durante i test, garantendo isolamento e velocità di esecuzione.

---

## 3. PATTERN ARCHITETTURALI E PRINCIPI DI DESIGN

L'analisi dei pattern utilizzati dimostra la comprensione dei principi fondamentali dell'ingegneria del software.

### Repository Pattern

L'implementazione del [Repository Pattern]([Repository Design Pattern - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/repository-design-pattern)) centralizza l'accesso ai dati attraverso una classe CRUD dedicata:

```python
class BookCRUD:
    @staticmethod
    def get_book_by_id(db, book_id: int):
        cursor = db.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        return cursor.fetchone()

    @staticmethod
    def search_books(db, search_term: str):
        query = "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?"
        cursor = db.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        return cursor.fetchall()
```

Questo pattern offre tre vantaggi fondamentali: centralizza la logica di accesso ai dati facilitando modifiche future, permette testing isolato sostituendo l'implementazione con mock, e fornisce un'interfaccia uniforme indipendente dalla tecnologia di persistenza.

### API-First Design

```python
@router.post("/books/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, current_user: User = Depends(get_current_user)):
    """Crea un nuovo libro nel sistema. Richiede autenticazione admin."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    return BookCRUD.create_book(book)
```

FastAPI genera automaticamente documentazione OpenAPI da questi endpoint.

### Principi SOLID

Il design rispetta i principi [SOLID]([SOLID - Wikipedia](https://it.wikipedia.org/wiki/SOLID)). Single Responsibility è evidente nella separazione modulare, Open/Closed nell'estendibilità attraverso nuovi router:

```python
# Aggiungere nuove funzionalità senza modificare codice esistente
# routers/categories.py (nuovo modulo)
@router.get("/categories/")  
def get_categories():
    return CategoryCRUD.get_all_categories()
```

---

## 4. DESIGN DEL DATABASE E MODELLAZIONE DATI

La progettazione del database rappresenta uno degli aspetti più critici del sistema, influenzando performance, scalabilità e integrità dei dati.

### Schema e normalizzazione

Il database implementa la [Normalizzazione]([Normalizzazione (informatica) - Wikipedia](https://it.wikipedia.org/wiki/Normalizzazione_(informatica))) attraverso questa struttura:

```sql
-- Entità principale utenti
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);

-- Entità principale libri
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE,
    available_copies INTEGER DEFAULT 1 CHECK (available_copies >= 0)
);

-- Relazione molti-a-molti con attributi
CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    loan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NOT NULL,
    is_returned INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);
```

La normalizzazione elimina ridondanze: informazioni utente e libro sono separate, con la tabella loans che gestisce le relazioni temporali tra entità.

### Vincoli di integrità e automazione

I vincoli CHECK garantiscono coerenza dei dati, mentre i trigger automatizzano operazioni complesse:

```sql
-- Vincolo per prevenire stati inconsistenti
CHECK (available_copies >= 0)

-- Trigger per automazione disponibilità
CREATE TRIGGER update_availability_on_loan
AFTER INSERT ON loans WHEN NEW.is_returned = 0
BEGIN
    UPDATE books SET available_copies = available_copies - 1 
    WHERE id = NEW.book_id;
END;
```

### Ottimizzazioni per performance

Gli indici strategici migliorano le performance delle query frequenti:

```sql
CREATE INDEX idx_users_email ON users(email);        -- Login
CREATE INDEX idx_books_title ON books(title);        -- Ricerca titolo
CREATE INDEX idx_loans_user_id ON loans(user_id);    -- Prestiti utente
```

---

## 5. SICUREZZA E GESTIONE DELLE VULNERABILITÀ

La sicurezza è stata progettata come aspetto trasversale dell'intero sistema, implementando multiple linee di difesa.

### Prevenzione SQL Injection

L'uso esclusivo di prepared statements elimina il rischio di SQL injection:

```python
# APPROCCIO SICURO - Prepared statements
def search_books_safe(db, search_term: str):
    query = "SELECT * FROM books WHERE title LIKE ?"
    return db.execute(query, (f"%{search_term}%",)).fetchall()

# VS approccio vulnerabile (MAI usare):
# query = f"SELECT * FROM books WHERE title LIKE '%{search_term}%'"
```

Anche input malevoli come `'; DROP TABLE books; --` vengono trattati come stringhe letterali senza eseguire codice SQL.

### Gestione sicura delle password

L'implementazione di [bcrypt]([bcrypt·PyPI](https://pypi.org/project/bcrypt/)) garantisce hashing sicuro con [salt]([Salt (crittografia) - Wikipedia](https://it.wikipedia.org/wiki/Salt_(crittografia))) automatici:

```python
import bcrypt

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), 
                         hashed_password.encode('utf-8'))
```

Il cost factor di 12 bilancia sicurezza (150ms per hash) e usabilità del sistema.

### Autenticazione JWT e rate limiting

Il sistema implementa autenticazione stateless e protezione contro abusi:

```python
# Rate limiting per prevenire brute force
@router.post("/auth/login")
@limiter.limit("5/minute")
def login(request: Request, credentials: UserLogin):
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenziali non valide")

    token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
```

### Validazione input rigorosa

Pydantic fornisce validazione automatica con controlli personalizzati:

```python
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str

    @validator('title', 'author')
    def validate_text_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Campo obbligatorio')

        # Blocca pattern SQL pericolosi
        dangerous_patterns = [';', '--', '/*', '*/']
        if any(pattern in v.lower() for pattern in dangerous_patterns):
            raise ValueError('Caratteri non permessi rilevati')

        return v.strip()
```

---

## 6. API DESIGN E INTERFACCE

Il design delle API segue i principi RESTful e le best practice per la creazione di interfacce intuitive e consistenti.

### Struttura RESTful degli endpoint

La mappatura risorsa-endpoint segue convenzioni standard:

```python
# Operazioni standard sui libri
@router.get("/books/")                    # Lista libri
@router.get("/books/{id}")               # Dettaglio libro
@router.post("/books/")                  # Crea libro
@router.put("/books/{id}")               # Aggiorna libro
@router.delete("/books/{id}")            # Elimina libro

# Operazioni specifiche di dominio
@router.get("/books/search/{term}")      # Ricerca libri
@router.post("/loans/")                  # Crea prestito
@router.put("/loans/{id}/return")        # Restituisci libro
```

### Gestione centralizzata degli errori

Il sistema implementa error handling consistente:

```python
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Errore di validazione",
            "details": [{
                "field": error["loc"][-1],
                "message": error["msg"]
            } for error in exc.errors()]
        }
    )
```

Questo garantisce risposte di errore strutturate e informative per tutti gli endpoint.

### Documentazione automatica

FastAPI genera documentazione interattiva con esempi:

```python
class BookCreate(BaseModel):
    title: str = Field(..., example="Il Nome della Rosa")
    author: str = Field(..., example="Umberto Eco")
    isbn: str = Field(None, example="978-8845292613")

    class Config:
        schema_extra = {
            "example": {
                "title": "Il Nome della Rosa",
                "author": "Umberto Eco", 
                "isbn": "978-8845292613"
            }
        }
```

---

## 7. TESTING E QUALITÀ DEL CODICE

La strategia di testing adottata garantisce affidabilità attraverso multiple tipologie di test.

### Test di sicurezza

I test verificano specificamente la resistenza agli attacchi:

```python
def test_sql_injection_prevention():
    """Verifica resistenza a SQL injection"""
    malicious_input = "'; DROP TABLE books; --"

    response = client.get(f"/books/search/{malicious_input}")
    assert response.status_code == 200  # Non dovrebbe crashare

    # Verifica che la tabella esista ancora
    response = client.get("/books/")
    assert response.status_code == 200
```

### Test di business logic

I test validano le regole applicative:

```python
def test_loan_availability_logic():
    """Verifica gestione disponibilità libri"""
    # Crea libro con 1 copia
    book_data = {"title": "Test Book", "author": "Test Author", "isbn": "123"}
    book_response = client.post("/books/", json=book_data)
    book_id = book_response.json()["id"]

    # Primo prestito dovrebbe funzionare
    loan_data = {"book_id": book_id, "user_id": 1}
    response = client.post("/loans/", json=loan_data)
    assert response.status_code == 201

    # Secondo prestito dovrebbe fallire (libro non disponibile)
    response = client.post("/loans/", json=loan_data)
    assert response.status_code == 400
```

### Test di integrazione

I test verificano l'intera pipeline API-Database:

```python
def test_book_creation_integration():
    """Test completo: API -> Database -> Response"""
    book_data = {"title": "Integration Test", "author": "Test Author"}

    # Creazione via API
    response = client.post("/books/", json=book_data)
    assert response.status_code == 201
    book_id = response.json()["id"]

    # Verifica persistenza in database
    with get_test_db() as db:
        cursor = db.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        db_book = cursor.fetchone()
        assert db_book["title"] == book_data["title"]
```

---

## 8. DEPLOYMENT E CONFIGURAZIONE

Le scelte di deployment bilanciano semplicità e robustezza.

### Configurazione dell'ambiente

La gestione delle configurazioni segue best practice DevOps:

```python
import os
from typing import Optional

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "library.db")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    # Sicurezza
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    RATE_LIMIT_LOGIN: str = os.getenv("RATE_LIMIT_LOGIN", "5/minute")
```

### Inizializzazione del database

Lo schema viene creato automaticamente all'avvio:

```python
def create_tables():
    with sqlite3.connect("library.db") as conn:
        with open("sql/create_tables.sql", "r") as f:
            conn.executescript(f.read())

@app.on_event("startup")
def startup_event():
    create_tables()
```

### Sicurezza in produzione

Per deployment produttivo, sono necessarie configurazioni aggiuntive:

- HTTPS obbligatorio con certificati SSL
- SECRET_KEY generata con crittografia sicura
- Backup automatici del database SQLite
- Monitoring dei log per rilevare tentativi di attacco
- Update regolari delle dipendenze Python

---

## 9. CONCLUSIONI E VALUTAZIONE CRITICA

### Obiettivi raggiunti

Il sistema implementa con successo tutte le funzionalità core richieste. L'architettura modulare facilita manutenzione ed estensione, mentre le implementazioni di sicurezza proteggono efficacemente contro vulnerabilità comuni.

*Completezza funzionale*: Le operazioni CRUD sono implementate e testate, l'autenticazione JWT è sicura, la ricerca libri supporta pattern matching flessibile, e il sistema di prestiti gestisce correttamente la disponibilità attraverso trigger database.

### Punti di forza

L'approccio security-first garantisce robustezza contro attacchi SQL injection e brute force. L'uso di query SQL native fornisce controllo completo e performance ottimali. La separazione delle responsabilità facilita testing e manutenzione:

```python
# Esempio di modularità: modifiche isolate
# Aggiungere caching richiede solo modifiche al CRUD layer
class BookCRUD:
    @staticmethod
    @cache(ttl=300)  # Solo questa modifica
    def search_books(db, search_term: str):
        # Query invariata
        pass
```

### Obiettivi mancati

Es. 

**Funzionalità core non implementate per mancanza di tempo**

Il sistema di ricerca avanzata con filtri multipli era pianificato ma non sviluppato. La ricerca implementata supporta solo title/author, mentre era prevista filtrazione per categoria, anno pubblicazione, disponibilità e range di date.

## 10. LIBRERIE PYTHON E RISORSE TECNICHE

### Framework Web e API

**FastAPI**

- **Sito ufficiale**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Documentazione**: [Tutorial - User Guide - FastAPI](https://fastapi.tiangolo.com/tutorial/)
- **GitHub**: [GitHub - fastapi/fastapi: FastAPI framework, high performance, easy to learn, fast to code, ready for production](https://github.com/tiangolo/fastapi)
- **Caso d'uso**: Framework moderno per API REST con generazione automatica documentazione OpenAPI
- **Esempio base**:

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

- **Tutorial consigliato**: "FastAPI Tutorial" su Real Python
- **Alternative**: Flask, Django REST Framework

**Flask**

- **Sito ufficiale**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- **Documentazione**: [Tutorial &#8212; Flask Documentation (3.2.x)](https://flask.palletsprojects.com/en/latest/tutorial/)
- **Caso d'uso**: Micro-framework per applicazioni web semplici e prototipazione rapida
- **Tutorial**: Flask Mega-Tutorial di Miguel Grinberg

### Database e ORM

**SQLAlchemy**

- **Sito ufficiale**: [https://www.sqlalchemy.org/](https://www.sqlalchemy.org/)
- **Documentazione**: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)
- **Tutorial**: https://docs.sqlalchemy.org/en/20/tutorial/
- **Caso d'uso**: ORM completo per gestione database relazionali
- **Esempio**:

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
```

**sqlite3** (Standard Library)

- **Documentazione**: [sqlite3 — DB-API 2.0 interface for SQLite databases &#8212; Python 3.13.5 documentation](https://docs.python.org/3/library/sqlite3.html)
- **Tutorial**: [10. Brief Tour of the Standard Library &#8212; Python 3.13.5 documentation](https://docs.python.org/3/tutorial/stdlib.html#database-access)
- **Caso d'uso**: Database leggero per prototipazione e applicazioni semplici

### Sicurezza e Autenticazione

**bcrypt**

- **PyPI**: [bcrypt·PyPI](https://pypi.org/project/bcrypt/)
- **Documentazione**: [GitHub - pyca/bcrypt: Modern(-ish) password hashing for your software and your servers](https://github.com/pyca/bcrypt/)
- **Caso d'uso**: Hashing sicuro delle password
- **Esempio**:

```python
import bcrypt
password = b"super_secret"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
```

**python-jose**

- **PyPI**: [python-jose·PyPI](https://pypi.org/project/python-jose/)
- **GitHub**: [GitHub - mpdavis/python-jose: A JOSE implementation in Python](https://github.com/mpdavis/python-jose)
- **Caso d'uso**: Implementazione JWT (JSON Web Tokens)
- **Documentazione JWT**: [JSON Web Token Introduction - jwt.io](https://jwt.io/introduction)

**passlib**

- **Sito ufficiale**: [https://passlib.readthedocs.io/](https://passlib.readthedocs.io/)
- **Caso d'uso**: Libreria completa per gestione password e hashing

### Validazione Dati

**Pydantic**

- **Sito ufficiale**: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)
- **GitHub**: [GitHub - pydantic/pydantic: Data validation using Python type hints](https://github.com/pydantic/pydantic)
- **Tutorial**: https://docs.pydantic.dev/latest/usage/
- **Caso d'uso**: Validazione dati e serialization con type hints
- **Esempio**:

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    name: str
    email: EmailStr
    age: int = None
```

### Testing

**pytest**

- **Sito ufficiale**: [https://docs.pytest.org/](https://docs.pytest.org/)
- **Tutorial**: [Get Started - pytest documentation](https://docs.pytest.org/en/stable/getting-started.html)
- **Caso d'uso**: Framework di testing Python più popolare
- **Plugin utili**: pytest-cov (coverage), pytest-mock (mocking)

**httpx**

- **GitHub**: [GitHub - encode/httpx: A next generation HTTP client for Python. ](https://github.com/encode/httpx)
- **Documentazione**: [https://www.python-httpx.org/](https://www.python-httpx.org/)
- **Caso d'uso**: Client HTTP moderno per testing API

### Analisi Dati e Reporting

**pandas**

- **Sito ufficiale**: [https://pandas.pydata.org/](https://pandas.pydata.org/)
- **Documentazione**: [pandas documentation &#8212; pandas 2.3.0 documentation](https://pandas.pydata.org/docs/)
- **Tutorial**: "10 Minutes to pandas" - [10 minutes to pandas &#8212; pandas 2.3.0 documentation](https://pandas.pydata.org/docs/user_guide/10min.html)
- **Caso d'uso**: Analisi dati, report, manipolazione dataset
- **Esempio**:

```python
import pandas as pd
df = pd.read_csv('library_data.csv')
monthly_stats = df.groupby('month')['loans'].sum()
```

**matplotlib**

- **Sito ufficiale**: [https://matplotlib.org/](https://matplotlib.org/)
- **Tutorial**: https://matplotlib.org/stable/tutorials/introductory/pyplot.html
- **Caso d'uso**: Generazione grafici e visualizzazioni

### Configurazione e Environment

**python-dotenv**

- **GitHub**: [GitHub - theskumar/python-dotenv: Reads key-value pairs from a .env file and can set them as environment variables. It helps in developing applications following the 12-factor principles.](https://github.com/theskumar/python-dotenv)
- **Caso d'uso**: Gestione variabili d'ambiente da file .env
- **Esempio**:

```python
from dotenv import load_dotenv
import os

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
```

**pydantic-settings**

- **Documentazione**: [Settings Management - Pydantic](https://docs.pydantic.dev/latest/usage/settings/)
- **Caso d'uso**: Gestione configurazioni con validazione Pydantic

### Deployment e Production

**uvicorn**

- **GitHub**: [GitHub - encode/uvicorn: An ASGI web server, for Python. 🦄](https://github.com/encode/uvicorn)
- **Documentazione**: [https://www.uvicorn.org/](https://www.uvicorn.org/)
- **Caso d'uso**: Server ASGI per FastAPI in produzione

**gunicorn**

- **Sito ufficiale**: [https://gunicorn.org/](https://gunicorn.org/)
- **Caso d'uso**: Server WSGI per Flask e Django

### Risorse di Apprendimento Generali

**Documentazione Python Ufficiale**

- **Python.org**: [3.13.5 Documentation](https://docs.python.org/3/)
- **Tutorial ufficiale**: [The Python Tutorial &#8212; Python 3.13.5 documentation](https://docs.python.org/3/tutorial/)

**Real Python**

- **Sito**: [https://realpython.com/](https://realpython.com/)
- **Tutorial consigliati**:
  - "Python REST APIs With FastAPI"
  - "Working With JSON Data in Python"
  - "Python SQL Libraries"

**Awesome Python**

- **GitHub**: [GitHub - vinta/awesome-python: An opinionated list of awesome Python frameworks, libraries, software and resources.](https://github.com/vinta/awesome-python)
- **Descrizione**: Lista curata di librerie Python per ogni scopo

**Python Package Index (PyPI)**

- **Sito**: [https://pypi.org/](https://pypi.org/)
- **Uso**: Repository centrale per tutti i package Python

### Esempio di requirements.txt completo

```txt
# Framework web
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlite3  # Standard library

# Sicurezza
bcrypt==4.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Validazione
pydantic==2.5.0
email-validator==2.1.0

# Testing
pytest==7.4.3
httpx==0.25.2
pytest-cov==4.1.0

# Configurazione
python-dotenv==1.0.0

# Analisi dati (opzionale)
pandas==2.1.3
matplotlib==3.8.2
```
