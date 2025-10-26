# Gestionale Negozio - Applicazione Desktop

Applicazione gestionale offline per la gestione di vendite, fornitori, spese e fatture.

## Requisiti

- Python 3.8 o superiore
- Windows (testato su Windows 10/11)

## Installazione

### 1. Installa Python

**IMPORTANTE**: Se Python non è installato, segui questi passi:

1. Vai su [python.org/downloads](https://www.python.org/downloads/)
2. Scarica Python 3.8 o superiore per Windows
3. **Durante l'installazione, assicurati di spuntare "Add Python to PATH"**
4. Riavvia il computer dopo l'installazione

### 2. Verifica Installazione Python

Apri PowerShell e verifica che Python sia installato:

```powershell
python --version
```

Se ottieni un errore, prova con:
```powershell
py --version
```

### 3. Installa Dipendenze

Apri PowerShell nella cartella del progetto e esegui:

```powershell
# Opzione 1: Con python
python -m pip install -r requirements.txt

# Opzione 2: Se python non funziona, prova con py
py -m pip install -r requirements.txt
```

### 4. Ambiente Virtuale (Opzionale ma Consigliato)

```powershell
# Crea ambiente virtuale
python -m venv venv

# Attiva ambiente virtuale
.\venv\Scripts\Activate.ps1

# Installa dipendenze nell'ambiente virtuale
pip install -r requirements.txt
```

## Avvio Applicazione

### Test Preliminare (Consigliato)

Prima di avviare l'applicazione, testa che tutto funzioni:

```powershell
# Opzione 1
python test_app.py

# Opzione 2 (se python non funziona)
py test_app.py
```

### Avvio Applicazione

```powershell
# Opzione 1
python main.py

# Opzione 2 (se python non funziona)
py main.py
```

### Risoluzione Problemi Comuni

**Errore "Python non trovato":**
- Reinstalla Python assicurandoti di spuntare "Add Python to PATH"
- Riavvia il computer
- Prova con `py` invece di `python`

**Errore "ModuleNotFoundError":**
- Assicurati di aver installato le dipendenze: `pip install -r requirements.txt`
- Se usi un ambiente virtuale, assicurati che sia attivato

**Errore PyQt5:**
- Su alcuni sistemi potrebbe essere necessario installare Visual C++ Redistributable
- Scaricalo da Microsoft se richiesto

Al primo avvio verrà creato automaticamente il database SQLite `gestionale.db` nella cartella del progetto.

## Funzionalità

### 1. Gestione Vendite Giornaliere
- Inserimento dati giornata (capitale iniziale, incassi, transazioni)
- Calcolo automatico di:
  - Incasso Contante
  - Incasso Bancario (con commissioni configurabili)
  - Corrispettivo
  - Ricavo Giornaliero
- Visualizzazione e modifica dati storici

### 2. Gestione Fornitori e Spese
- Gestione anagrafica fornitori
- Registrazione acquisti con pagamenti contante/bancario
- Riepiloghi per fornitore e periodo

### 3. Filtri e Report
- Filtri per data: giornaliero, settimanale, mensile, intervallo personalizzato
- Ricerca testuale
- Esportazione dati

### 4. Gestione Fatture (COMPLETA!)
- 📄 **Caricamento PDF** fatture esistenti
- 📷 **Conversione foto → PDF** ricercabili con OCR
- 🎯 **Estrazione automatica dati**: numero, data, importo, fornitore, P.IVA
- 🔍 **Ricerca testuale** nelle fatture
- 👁️ **Visualizzazione** file con app di sistema
- 📋 **Archiviazione completa** con note e collegamenti fornitori

### 5. Import Dati
- Importazione massiva da file CSV
- Mappatura colonne personalizzabile

## 🔍 Configurazione OCR (ALTAMENTE CONSIGLIATA!)

**Per foto fatture → PDF ricercabili:**

1. **Scarica Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki
2. **Installa** in: `C:\Program Files\Tesseract-OCR` (default)
3. **Seleziona Italian language pack** durante l'installazione
4. **Riavvia l'applicazione**

**📖 Guida completa**: Vedi `GUIDA_OCR.md` per istruzioni dettagliate

## Backup Database

Il file `gestionale.db` contiene tutti i dati. Per backup:
- Copia il file `gestionale.db` in una posizione sicura
- Per ripristino, sostituisci il file con la copia di backup

## Struttura Progetto

```
Gestionale/
├── main.py                 # Entry point applicazione
├── requirements.txt        # Dipendenze Python
├── database/
│   ├── __init__.py
│   ├── schema.py          # Schema database SQLite
│   └── repository.py      # Layer accesso dati
├── models/
│   ├── __init__.py
│   ├── sale.py           # Model vendita
│   ├── supplier.py       # Model fornitore
│   ├── purchase.py       # Model acquisto
│   └── invoice.py        # Model fattura
├── ui/
│   ├── __init__.py
│   ├── main_window.py    # Finestra principale
│   ├── sales_tab.py      # Tab vendite
│   ├── suppliers_tab.py  # Tab fornitori
│   ├── reports_tab.py    # Tab report
│   └── invoices_tab.py   # Tab fatture
├── services/
│   ├── __init__.py
│   ├── calculator.py     # Logica calcoli
│   ├── csv_importer.py   # Import CSV
│   └── ocr_service.py    # Servizio OCR
└── gestionale.db         # Database SQLite (creato al primo avvio)
```

## Supporto

Per problemi o domande, consulta il codice sorgente commentato.
