# 🚀 ISTRUZIONI RAPIDE - GESTIONALE NEGOZIO

## ⚡ AVVIO VELOCE

### Opzione 1: Doppio Click (Più Semplice)
1. **Installa dipendenze**: Doppio click su `installa_dipendenze.bat`
2. **Avvia applicazione**: Doppio click su `avvia_gestionale.bat`

### Opzione 2: PowerShell
```powershell
# 1. Installa dipendenze
python -m pip install -r requirements.txt

# 2. Avvia applicazione
python main.py
```

---

## 🔧 SE PYTHON NON È INSTALLATO

1. Vai su: **https://www.python.org/downloads/**
2. Scarica **Python 3.8 o superiore**
3. **IMPORTANTE**: Durante l'installazione spunta "**Add Python to PATH**"
4. Riavvia il computer
5. Riprova l'avvio

---

## 📋 FUNZIONALITÀ PRINCIPALI

### 📊 Vendite Giornaliere
- Inserisci i dati come nel tuo foglio Excel
- Calcoli automatici di incassi e commissioni
- Navigazione per data (oggi, ieri, avanti/indietro)

### 🏭 Fornitori e Spese
- Gestione anagrafica fornitori
- Inserimento spese con pagamenti contante/bancario
- Riepiloghi automatici

### 📈 Report e Filtri
- Analisi per periodo (oggi, settimana, mese)
- Profitti e perdite
- Dettagli per fornitore

### 📥 Import CSV
- Menu File → Importa CSV
- File di esempio inclusi: `esempio_vendite.csv`, `esempio_fornitori.csv`, `esempio_spese.csv`

---

## 🗂️ FILE IMPORTANTI

- **`main.py`** - Avvia l'applicazione
- **`gestionale.db`** - Database (creato automaticamente)
- **`avvia_gestionale.bat`** - Avvio rapido Windows
- **`installa_dipendenze.bat`** - Installazione automatica
- **`esempio_*.csv`** - File di esempio per import

---

## 🆘 PROBLEMI COMUNI

### "Python non trovato"
- Reinstalla Python con "Add to PATH" spuntato
- Riavvia il computer
- Prova con `py` invece di `python`

### "ModuleNotFoundError"
- Esegui: `pip install -r requirements.txt`
- Oppure doppio click su `installa_dipendenze.bat`

### Errori PyQt5
- Potrebbe servire Visual C++ Redistributable da Microsoft

---

## 💾 BACKUP DATI

Il file **`gestionale.db`** contiene tutti i tuoi dati.

**Per fare backup**:
- Menu Strumenti → Backup Database
- Oppure copia manualmente il file `gestionale.db`

**Per ripristinare**:
- Sostituisci `gestionale.db` con la copia di backup

---

## 📞 SUPPORTO

Se hai problemi:
1. Controlla che Python sia installato correttamente
2. Verifica che le dipendenze siano installate
3. Prova a eseguire `python test_app.py` per diagnosticare

---

## ✨ PRIMO UTILIZZO

1. **Avvia l'applicazione**
2. **Tab "Vendite Giornaliere"**: Inserisci i dati di oggi
3. **Tab "Fornitori e Spese"**: Aggiungi nuovi fornitori se necessario
4. **Tab "Report"**: Controlla i risultati

I fornitori **AIA**, **GranTerre**, **MIA** sono già precaricati.

---

**🎉 Buon lavoro con il tuo gestionale!**
