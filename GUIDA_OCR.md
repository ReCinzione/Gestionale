# 🔍 GUIDA INSTALLAZIONE OCR (TESSERACT)

## 📋 Cos'è l'OCR?

L'**OCR (Optical Character Recognition)** permette di:
- ✅ **Estrarre testo** da foto di fatture
- ✅ **Convertire foto in PDF** ricercabili
- ✅ **Compilare automaticamente** i campi delle fatture
- ✅ **Cercare testo** dentro le fatture

## 🚀 INSTALLAZIONE RAPIDA

### 1. Scarica Tesseract OCR

**Link diretto:** https://github.com/UB-Mannheim/tesseract/wiki

1. Clicca su **"tesseract-ocr-w64-setup-5.x.x.exe"** (versione più recente)
2. Scarica il file (circa 60 MB)

### 2. Installa Tesseract

1. **Esegui il file** scaricato come **Amministratore**
2. **Percorso consigliato:** `C:\Program Files\Tesseract-OCR` (default)
3. **Importante:** Durante l'installazione, seleziona:
   - ✅ **Italian language pack** (per fatture in italiano)
   - ✅ **English language pack** (già selezionato)
4. Completa l'installazione

### 3. Verifica Installazione

1. **Riavvia l'applicazione** gestionale
2. Vai nel tab **"📄 Fatture"**
3. Se vedi il messaggio **"⚠️ OCR non disponibile"** → ripeti l'installazione
4. Se **non vedi il messaggio** → OCR installato correttamente! 🎉

## 🖼️ COME USARE L'OCR

### Carica Foto Fattura

1. **Tab Fatture** → **"📷 Carica Foto"**
2. Seleziona foto della fattura (JPG, PNG, etc.)
3. Scegli **"Sì"** per convertire in PDF ricercabile
4. **Attendi** l'elaborazione (può richiedere 10-30 secondi)
5. I **dati vengono estratti automaticamente**!

### Carica PDF Esistente

1. **Tab Fatture** → **"📄 Carica PDF"**
2. Seleziona file PDF
3. Se contiene testo, viene **estratto automaticamente**
4. Se è un'immagine scansionata, usa l'OCR

### Estrazione Dati Automatica

L'OCR cerca automaticamente:
- 📋 **Numero fattura**
- 📅 **Data fattura**
- 💰 **Importo totale**
- 🏭 **Nome fornitore**
- 🔢 **Partita IVA**

## ⚙️ RISOLUZIONE PROBLEMI

### "OCR non disponibile"

**Soluzioni:**
1. **Reinstalla Tesseract** in `C:\Program Files\Tesseract-OCR`
2. **Riavvia il computer**
3. **Riavvia l'applicazione** gestionale
4. Controlla che il file `tesseract.exe` esista in:
   ```
   C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

### OCR lento o impreciso

**Suggerimenti:**
- 📸 **Foto nitide**: evita sfocature
- 💡 **Buona illuminazione**: evita ombre
- 📐 **Foto dritte**: non inclinate
- 🔍 **Zoom adeguato**: testo leggibile
- 🖼️ **Formato consigliato**: JPG o PNG

### Dati estratti sbagliati

**Normale!** L'OCR non è perfetto:
- ✏️ **Controlla sempre** i dati estratti
- 🔧 **Correggi manualmente** se necessario
- 💾 **Salva** dopo le correzioni

## 🎯 CONSIGLI PER FOTO PERFETTE

### ✅ BUONE PRATICHE
- 📱 Usa la **fotocamera del telefono**
- 🔆 **Luce naturale** o buona illuminazione
- 📏 **Inquadra tutta la fattura**
- 🎯 **Metti a fuoco** il testo
- 📐 **Tieni il telefono dritto**

### ❌ DA EVITARE
- 🌑 Foto al buio o con flash
- 📐 Foto inclinate o storte
- 🔍 Zoom eccessivo (solo una parte)
- 👆 Dita che coprono il testo
- 💧 Riflessi o ombre sul documento

## 🔧 PERCORSI ALTERNATIVI

Se Tesseract non si installa in `C:\Program Files\Tesseract-OCR`, l'applicazione cerca anche in:

- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Users\[TuoNome]\AppData\Local\Programs\Tesseract-OCR\tesseract.exe`

## 📞 SUPPORTO

**L'OCR non funziona?**
1. Controlla che Tesseract sia installato
2. Riavvia l'applicazione
3. Prova con una foto di test semplice
4. L'applicazione funziona anche **senza OCR** (inserimento manuale)

---

**🎉 Con l'OCR attivo, la gestione fatture diventa automatica!**
