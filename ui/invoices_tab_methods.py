"""
Metodi per il tab fatture - da aggiungere alla classe InvoicesTab
"""

def load_suppliers(self):
    """Carica la lista dei fornitori"""
    suppliers = self.suppliers_repo.get_all_active()
    
    self.supplier_combo.clear()
    self.supplier_combo.addItem('-- Seleziona fornitore --', None)
    
    for supplier in suppliers:
        self.supplier_combo.addItem(supplier['name'], supplier['id'])

def load_pdf_file(self):
    """Carica un file PDF"""
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        'Seleziona File PDF',
        '',
        'File PDF (*.pdf);;Tutti i file (*.*)'
    )
    
    if file_path:
        self.current_file_path = file_path
        self.lbl_file_info.setText(f'📄 PDF: {os.path.basename(file_path)}')
        
        # Prova a estrarre testo dal PDF
        if self.ocr_service.is_available():
            self.start_ocr_processing('pdf_text')
        else:
            QMessageBox.information(
                self,
                'PDF Caricato',
                'PDF caricato. OCR non disponibile per estrazione automatica dati.'
            )

def load_image_file(self):
    """Carica un'immagine (foto fattura)"""
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        'Seleziona Immagine',
        '',
        'Immagini (*.jpg *.jpeg *.png *.bmp *.tiff);;Tutti i file (*.*)'
    )
    
    if file_path:
        # Chiedi se creare PDF
        reply = QMessageBox.question(
            self,
            'Converti in PDF',
            'Vuoi convertire l\'immagine in PDF ricercabile?\n\n'
            'Questo creerà un PDF con OCR per facilitare la ricerca.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.convert_image_to_pdf(file_path)
        else:
            self.current_file_path = file_path
            self.lbl_file_info.setText(f'📷 Immagine: {os.path.basename(file_path)}')
            
            # Avvia OCR se disponibile
            if self.ocr_service.is_available():
                self.start_ocr_processing('image_ocr')

def convert_image_to_pdf(self, image_path):
    """Converte un'immagine in PDF con OCR"""
    try:
        # Scegli dove salvare il PDF
        pdf_name = os.path.splitext(os.path.basename(image_path))[0] + '.pdf'
        pdf_path, _ = QFileDialog.getSaveFileName(
            self,
            'Salva PDF',
            pdf_name,
            'File PDF (*.pdf)'
        )
        
        if pdf_path:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminato
            
            # Crea PDF con OCR
            extracted_text = self.ocr_service.create_pdf_from_image(
                image_path, pdf_path, include_ocr=True
            )
            
            self.progress_bar.setVisible(False)
            
            # Aggiorna interfaccia
            self.current_file_path = pdf_path
            self.lbl_file_info.setText(f'📄 PDF creato: {os.path.basename(pdf_path)}')
            
            # Mostra testo estratto
            if extracted_text:
                self.ocr_text_edit.setPlainText(extracted_text)
                self.btn_extract_data.setEnabled(True)
                
                # Estrai automaticamente i dati
                self.extract_data_from_text()
            
            QMessageBox.information(
                self,
                'Conversione Completata',
                f'Immagine convertita in PDF con successo!\n\nFile salvato: {pdf_path}'
            )
    
    except Exception as e:
        self.progress_bar.setVisible(False)
        QMessageBox.critical(
            self,
            'Errore Conversione',
            f'Errore durante la conversione:\n{str(e)}'
        )

def start_ocr_processing(self, operation_type):
    """Avvia il processing OCR in background"""
    self.progress_bar.setVisible(True)
    self.progress_bar.setRange(0, 0)  # Indeterminato
    
    # Crea worker thread per OCR
    self.ocr_worker = OCRWorker(self.ocr_service, self.current_file_path, operation_type)
    self.ocr_worker.finished.connect(self.on_ocr_finished)
    self.ocr_worker.error.connect(self.on_ocr_error)
    self.ocr_worker.start()

def on_ocr_finished(self, text, extracted_data):
    """Gestisce il completamento dell'OCR"""
    self.progress_bar.setVisible(False)
    
    # Mostra testo estratto
    self.ocr_text_edit.setPlainText(text)
    self.btn_extract_data.setEnabled(True)
    
    # Popola automaticamente i campi se i dati sono stati estratti
    if any(extracted_data.values()):
        self.populate_fields_from_data(extracted_data)
        
        QMessageBox.information(
            self,
            'OCR Completato',
            'Testo estratto e dati popolati automaticamente.\n'
            'Controlla e correggi i dati se necessario.'
        )

def on_ocr_error(self, error_message):
    """Gestisce errori OCR"""
    self.progress_bar.setVisible(False)
    QMessageBox.warning(
        self,
        'Errore OCR',
        f'Errore durante l\'estrazione testo:\n{error_message}'
    )

def extract_data_from_text(self):
    """Estrae dati strutturati dal testo OCR"""
    text = self.ocr_text_edit.toPlainText()
    if not text.strip():
        QMessageBox.warning(self, 'Attenzione', 'Nessun testo da analizzare.')
        return
    
    try:
        extracted_data = self.ocr_service.extract_invoice_data(text)
        self.populate_fields_from_data(extracted_data)
        
        # Mostra risultati
        found_data = [k for k, v in extracted_data.items() if v]
        if found_data:
            QMessageBox.information(
                self,
                'Dati Estratti',
                f'Dati trovati: {", ".join(found_data)}\n\n'
                'Controlla e correggi se necessario.'
            )
        else:
            QMessageBox.information(
                self,
                'Nessun Dato',
                'Non sono stati trovati dati strutturati nel testo.\n'
                'Inserisci manualmente i dati della fattura.'
            )
    
    except Exception as e:
        QMessageBox.critical(
            self,
            'Errore',
            f'Errore durante l\'estrazione dati:\n{str(e)}'
        )

def populate_fields_from_data(self, data):
    """Popola i campi del form con i dati estratti"""
    # Numero fattura
    if data.get('invoice_number'):
        self.invoice_number_edit.setText(data['invoice_number'])
    
    # Data
    if data.get('date'):
        try:
            # Prova a parsare la data
            parts = data['date'].split('/')
            if len(parts) == 3:
                day, month, year = parts
                date = QDate(int(year), int(month), int(day))
                self.date_edit.setDate(date)
        except:
            pass
    
    # Importo
    if data.get('total_amount'):
        # Pulisci l'importo (rimuovi caratteri non numerici eccetto . e ,)
        amount_str = data['total_amount']
        amount_str = amount_str.replace(',', '.')
        try:
            # Estrai solo numeri e punto decimale
            import re
            clean_amount = re.sub(r'[^\d.]', '', amount_str)
            if clean_amount:
                self.amount_edit.setText(clean_amount)
        except:
            pass
    
    # P.IVA
    if data.get('vat_number'):
        self.vat_number_edit.setText(data['vat_number'])
    
    # Nome fornitore
    if data.get('supplier_name'):
        # Cerca se esiste già nei fornitori
        supplier_name = data['supplier_name']
        for i in range(self.supplier_combo.count()):
            if supplier_name.lower() in self.supplier_combo.itemText(i).lower():
                self.supplier_combo.setCurrentIndex(i)
                break
        else:
            # Se non trovato, imposta come testo editabile
            self.supplier_combo.setEditText(supplier_name)

def clear_ocr_text(self):
    """Pulisce il testo OCR"""
    self.ocr_text_edit.clear()
    self.btn_extract_data.setEnabled(False)

def save_invoice(self):
    """Salva la fattura nel database"""
    # Validazioni
    if not self.invoice_number_edit.text().strip():
        QMessageBox.warning(self, 'Attenzione', 'Inserisci il numero della fattura.')
        return
    
    try:
        # Determina supplier_id
        supplier_id = None
        supplier_text = self.supplier_combo.currentText().strip()
        
        if self.supplier_combo.currentData():
            supplier_id = self.supplier_combo.currentData()
        elif supplier_text and supplier_text != '-- Seleziona fornitore --':
            # Crea nuovo fornitore se non esiste
            existing = self.suppliers_repo.get_by_name(supplier_text)
            if existing:
                supplier_id = existing['id']
            else:
                supplier_id = self.suppliers_repo.create(supplier_text)
        
        # Crea l'oggetto fattura
        invoice = Invoice(
            date=self.date_edit.date().toString('yyyy-MM-dd'),
            supplier_id=supplier_id,
            invoice_number=self.invoice_number_edit.text().strip(),
            total_amount=float(self.amount_edit.text() or 0),
            file_path=self.current_file_path or '',
            ocr_text=self.ocr_text_edit.toPlainText(),
            notes=self.notes_edit.toPlainText()
        )
        
        # Salva nel database
        if self.current_invoice:
            # Aggiorna esistente
            self.invoices_repo.update(self.current_invoice.id, invoice.to_dict())
            QMessageBox.information(self, 'Successo', 'Fattura aggiornata con successo!')
        else:
            # Crea nuova
            self.invoices_repo.create(invoice.to_dict())
            QMessageBox.information(self, 'Successo', 'Fattura salvata con successo!')
        
        self.clear_form()
        self.load_invoices()
        self.invoice_saved.emit()
    
    except Exception as e:
        QMessageBox.critical(self, 'Errore', f'Errore durante il salvataggio:\n{str(e)}')

def clear_form(self):
    """Pulisce il form"""
    self.date_edit.setDate(QDate.currentDate())
    self.invoice_number_edit.clear()
    self.supplier_combo.setCurrentIndex(0)
    self.amount_edit.clear()
    self.vat_number_edit.clear()
    self.ocr_text_edit.clear()
    self.notes_edit.clear()
    self.lbl_file_info.setText('Nessun file caricato')
    self.current_file_path = None
    self.current_invoice = None
    self.btn_extract_data.setEnabled(False)

def load_invoices(self):
    """Carica tutte le fatture nella tabella"""
    invoices = self.invoices_repo.get_all(limit=1000)
    self.populate_invoices_table(invoices)

def populate_invoices_table(self, invoices):
    """Popola la tabella con le fatture"""
    self.invoices_table.setRowCount(len(invoices))
    
    for row, invoice in enumerate(invoices):
        # Data
        date_item = QTableWidgetItem(invoice.get('date', ''))
        self.invoices_table.setItem(row, 0, date_item)
        
        # Numero
        number_item = QTableWidgetItem(invoice.get('invoice_number', ''))
        self.invoices_table.setItem(row, 1, number_item)
        
        # Fornitore
        supplier_item = QTableWidgetItem(invoice.get('supplier_name', ''))
        self.invoices_table.setItem(row, 2, supplier_item)
        
        # Importo
        amount = invoice.get('total_amount', 0)
        amount_item = QTableWidgetItem(f"€ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.invoices_table.setItem(row, 3, amount_item)
        
        # File
        file_path = invoice.get('file_path', '')
        file_item = QTableWidgetItem('📄' if file_path else '❌')
        file_item.setTextAlignment(Qt.AlignCenter)
        self.invoices_table.setItem(row, 4, file_item)
        
        # Note
        notes_item = QTableWidgetItem(invoice.get('notes', ''))
        self.invoices_table.setItem(row, 5, notes_item)
        
        # Memorizza l'ID per azioni
        date_item.setData(Qt.UserRole, invoice['id'])

def filter_invoices(self):
    """Filtra le fatture in base al testo di ricerca"""
    search_text = self.search_edit.text().strip()
    
    if search_text:
        invoices = self.invoices_repo.search(search_text)
    else:
        invoices = self.invoices_repo.get_all(limit=1000)
    
    self.populate_invoices_table(invoices)

def edit_invoice(self):
    """Modifica la fattura selezionata"""
    current_row = self.invoices_table.currentRow()
    if current_row < 0:
        QMessageBox.warning(self, 'Attenzione', 'Seleziona una fattura da modificare.')
        return
    
    # Ottieni l'ID della fattura
    invoice_id = self.invoices_table.item(current_row, 0).data(Qt.UserRole)
    invoice_data = self.invoices_repo.get_by_id(invoice_id)
    
    if not invoice_data:
        QMessageBox.warning(self, 'Errore', 'Fattura non trovata.')
        return
    
    # Popola il form
    self.current_invoice = Invoice.from_dict(invoice_data)
    
    # Imposta data
    try:
        date_parts = self.current_invoice.date.split('-')
        date = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        self.date_edit.setDate(date)
    except:
        pass
    
    # Altri campi
    self.invoice_number_edit.setText(self.current_invoice.invoice_number)
    self.amount_edit.setText(str(self.current_invoice.total_amount))
    self.ocr_text_edit.setPlainText(self.current_invoice.ocr_text)
    self.notes_edit.setPlainText(self.current_invoice.notes)
    
    # Fornitore
    if self.current_invoice.supplier_id:
        for i in range(self.supplier_combo.count()):
            if self.supplier_combo.itemData(i) == self.current_invoice.supplier_id:
                self.supplier_combo.setCurrentIndex(i)
                break
    
    # File path
    if self.current_invoice.file_path:
        self.current_file_path = self.current_invoice.file_path
        self.lbl_file_info.setText(f'📄 File: {os.path.basename(self.current_invoice.file_path)}')

def view_invoice_file(self):
    """Visualizza il file della fattura selezionata"""
    current_row = self.invoices_table.currentRow()
    if current_row < 0:
        QMessageBox.warning(self, 'Attenzione', 'Seleziona una fattura.')
        return
    
    # Ottieni l'ID della fattura
    invoice_id = self.invoices_table.item(current_row, 0).data(Qt.UserRole)
    invoice_data = self.invoices_repo.get_by_id(invoice_id)
    
    if not invoice_data or not invoice_data.get('file_path'):
        QMessageBox.warning(self, 'Attenzione', 'Nessun file associato a questa fattura.')
        return
    
    file_path = invoice_data['file_path']
    
    if not os.path.exists(file_path):
        QMessageBox.warning(self, 'Errore', f'File non trovato:\n{file_path}')
        return
    
    # Apri con applicazione predefinita del sistema
    try:
        import subprocess
        import platform
        
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux
            subprocess.call(['xdg-open', file_path])
    
    except Exception as e:
        QMessageBox.critical(self, 'Errore', f'Impossibile aprire il file:\n{str(e)}')

def delete_invoice(self):
    """Elimina la fattura selezionata"""
    current_row = self.invoices_table.currentRow()
    if current_row < 0:
        QMessageBox.warning(self, 'Attenzione', 'Seleziona una fattura da eliminare.')
        return
    
    # Ottieni l'ID della fattura
    invoice_id = self.invoices_table.item(current_row, 0).data(Qt.UserRole)
    
    reply = QMessageBox.question(
        self,
        'Conferma Eliminazione',
        'Sei sicuro di voler eliminare questa fattura?\n\n'
        'ATTENZIONE: Il file associato NON verrà eliminato.',
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        try:
            self.invoices_repo.delete(invoice_id)
            QMessageBox.information(self, 'Successo', 'Fattura eliminata con successo!')
            self.load_invoices()
            self.invoice_saved.emit()
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore durante l\'eliminazione:\n{str(e)}')
