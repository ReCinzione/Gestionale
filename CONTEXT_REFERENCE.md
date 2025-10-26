# 📋 Context Reference - Gestionale Negozio

## 🏗️ Architettura del Progetto

### Struttura Directory
```
Gestionale/
├── main.py                 # Entry point applicazione
├── database/              # Layer database
│   ├── schema.py          # Definizione schema DB
│   └── repository.py      # Repository pattern per CRUD
├── models/                # Modelli dati
│   ├── sale.py           # Modello vendite
│   ├── supplier.py       # Modello fornitori
│   ├── purchase.py       # Modello acquisti
│   └── invoice.py        # Modello fatture
├── services/             # Servizi business logic
│   ├── ocr_service.py    # Servizio OCR/PDF
│   ├── calculator.py     # Calcoli vendite
│   └── csv_importer.py   # Import CSV
└── ui/                   # Interfaccia utente
    ├── main_window.py    # Finestra principale
    ├── sales_tab.py      # Tab vendite
    ├── suppliers_tab.py  # Tab fornitori
    ├── reports_tab.py    # Tab report
    └── invoices_tab.py   # Tab fatture
```

### Stack Tecnologico
- **Framework UI**: PyQt5 5.15.10
- **Database**: SQLite (gestionale.db)
- **OCR**: pytesseract + Tesseract
- **PDF**: PyPDF2 3.0.1, pdf2image, reportlab
- **Imaging**: Pillow 10.2.0
- **Data**: openpyxl per Excel

## 🎯 Funzionalità Principali

### 1. Vendite Giornaliere
- Inserimento dati giornalieri (contante, carte, spese)
- Calcolo automatico profitti e perdite
- Navigazione tra giorni
- Validazione input numerici

### 2. Gestione Fornitori
- CRUD fornitori
- Tracking spese per fornitore
- Import/Export CSV
- Calcoli totali spese

### 3. Sistema Fatture
- Caricamento PDF/immagini
- OCR automatico per estrazione dati
- Associazione fornitori
- Archiviazione file

### 4. Report e Analytics
- Filtri per periodo
- Grafici vendite/spese
- Export Excel
- Statistiche aggregate

## 🔧 Problemi Identificati

### UX/UI Issues
- Design datato con PyQt5 standard
- Layout denso e poco respirabile
- Colori poco moderni
- Icone emoji invece di vettoriali
- Mancanza temi scuro/chiaro

### Problemi Tecnici OCR
- PyPDF2 obsoleto (problemi PDF moderni)
- Regex fragili per parsing fatture
- Preprocessing immagini limitato
- Dipendenza Tesseract esterna
- Scarsa accuratezza estrazione dati

### Limitazioni Architetturali
- Monolitico senza separazione concerns
- Mancanza dependency injection
- Error handling inconsistente
- Logging assente
- Testing coverage zero

## 🎨 Design Patterns Utilizzati

### Repository Pattern
```python
# database/repository.py
class SalesRepository:
    def __init__(self, connection):
        self.conn = connection
    
    def create(self, sale_data): ...
    def get_by_date(self, date): ...
    def update(self, sale_id, data): ...
```

### Observer Pattern
```python
# ui/invoices_tab.py
invoice_saved = pyqtSignal()  # Notifica altri componenti
```

### Strategy Pattern (OCR)
```python
# services/ocr_service.py
class OCRService:
    def extract_text_from_image(self): ...
    def extract_text_from_pdf(self): ...
```

## 🔐 Convenzioni Codice

### Naming
- **Classi**: PascalCase (MainWindow, OCRService)
- **Metodi**: snake_case (load_invoices, extract_data)
- **Variabili**: snake_case (current_invoice, file_path)
- **Costanti**: UPPER_SNAKE_CASE (PDF2IMAGE_AVAILABLE)

### Struttura File
```python
# Header con docstring
"""
Descrizione modulo
"""

# Import standard library
import os
import sys

# Import third party
from PyQt5.QtWidgets import QWidget

# Import locali
from models.invoice import Invoice

# Classe principale
class ComponentName:
    def __init__(self):
        self.init_ui()
    
    def init_ui(self):
        """Inizializza interfaccia"""
        pass
```

## 📊 Metriche Qualità

### Complessità Attuale
- **LOC Totali**: ~2500 linee
- **File Python**: 15
- **Classi Principali**: 8
- **Metodi Pubblici**: ~80
- **Dipendenze Esterne**: 7

### Debt Tecnico
- **Duplicazione Codice**: Media (form validation, error handling)
- **Accoppiamento**: Alto (UI dipende direttamente da DB)
- **Coesione**: Media (responsabilità miste)
- **Testabilità**: Bassa (dipendenze hard-coded)

## 🎯 Obiettivi Miglioramento

### Priorità Alta
1. **OCR Accuracy**: Sostituire PyPDF2 con pdfplumber + EasyOCR
2. **UI Modernization**: Material Design + temi
3. **Error Handling**: Logging strutturato + recovery

### Priorità Media
1. **Architecture**: Dependency injection + clean architecture
2. **Testing**: Unit tests + integration tests
3. **Performance**: Caching + background processing

### Priorità Bassa
1. **Mobile**: Companion app
2. **Cloud**: Sync + backup
3. **AI**: Smart data extraction

## 🔍 Context Engineering Guidelines

### Per Modifiche UI
1. Controllare `ui/main_window.py` per struttura generale
2. Verificare pattern esistenti in altri tab
3. Mantenere coerenza styling e layout
4. Testare su diverse risoluzioni

### Per Modifiche Database
1. Aggiornare `database/schema.py` per nuove tabelle
2. Implementare migration se necessario
3. Aggiornare repository corrispondente
4. Verificare integrità referenziale

### Per Nuove Funzionalità
1. Seguire architettura esistente (Model-Repository-UI)
2. Implementare error handling consistente
3. Aggiungere logging appropriato
4. Documentare API pubbliche

## 📚 Riferimenti Utili

### Documentazione
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [SQLite Python](https://docs.python.org/3/library/sqlite3.html)
- [Tesseract OCR](https://tesseract-ocr.github.io/)

### Best Practices
- [Clean Code Python](https://github.com/zedr/clean-code-python)
- [Python Design Patterns](https://python-patterns.guide/)
- [PyQt Best Practices](https://doc.qt.io/qt-5/qtquick-bestpractices.html)