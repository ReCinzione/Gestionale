"""Tab per la gestione completa delle fatture con OCR e PDF."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit, QComboBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QSplitter, QAbstractItemView, QProgressBar,
    QTabWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QThread
from PyQt5.QtGui import QDoubleValidator, QFont, QPixmap
from datetime import datetime
import os
import tempfile
from models.invoice import Invoice
from services.ocr_service import OCRService


class OCRWorker(QThread):
    """Worker thread per operazioni OCR lunghe"""
    
    finished = pyqtSignal(str, dict)  # testo, dati_estratti
    error = pyqtSignal(str)
    
    def __init__(self, ocr_service, file_path, operation_type):
        super().__init__()
        self.ocr_service = ocr_service
        self.file_path = file_path
        self.operation_type = operation_type
    
    def run(self):
        try:
            if self.operation_type == 'image_ocr':
                text = self.ocr_service.extract_text_from_image(self.file_path)
                data = self.ocr_service.extract_invoice_data(text)
                self.finished.emit(text, data)
            elif self.operation_type == 'pdf_text':
                text = self.ocr_service.extract_text_from_pdf(self.file_path)
                data = self.ocr_service.extract_invoice_data(text)
                self.finished.emit(text, data)
        except Exception as e:
            self.error.emit(str(e))


class InvoicesTab(QWidget):
    """Tab per la gestione completa delle fatture"""
    
    invoice_saved = pyqtSignal()  # Segnale emesso quando si salva una fattura
    
    def __init__(self, invoices_repo, suppliers_repo):
        super().__init__()
        
        self.invoices_repo = invoices_repo
        self.suppliers_repo = suppliers_repo
        self.ocr_service = OCRService()
        
        self.current_invoice = None
        self.current_file_path = None
        
        self.init_ui()
        self.load_invoices()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        # Applica stile moderno al tab fatture
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
            }
            
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QLineEdit, QComboBox {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #2196F3;
            }
            
            QDateEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
                min-width: 120px;
            }
            
            QDateEdit:focus {
                border-color: #2196F3;
            }
            
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #333333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #fafafa;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #fafafa;
            }
            
            QLabel {
                font-size: 13px;
                color: #555555;
            }
            
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #e3f2fd;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 13px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: 600;
                font-size: 13px;
            }
            
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
            }
            
            QTextEdit:focus {
                border-color: #2196F3;
            }
            
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
            }
            
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 4px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Controllo disponibilità OCR
        if not self.ocr_service.is_available():
            ocr_warning = QLabel(
                '<p><b>⚠️ OCR non disponibile</b></p>'
                '<p>Per utilizzare l\'estrazione automatica dati:</p>'
                f'<pre>{self.ocr_service.get_installation_instructions()}</pre>'
            )
            ocr_warning.setStyleSheet('QLabel { background-color: #fff3e0; padding: 15px; border: 2px solid #ff9800; border-radius: 8px; color: #e65100; }')
            layout.addWidget(ocr_warning)
        
        # Splitter principale
        splitter = QSplitter(Qt.Horizontal)
        
        # Pannello sinistro: Form inserimento fattura
        left_panel = self.create_input_panel()
        splitter.addWidget(left_panel)
        
        # Pannello destro: Lista fatture e anteprima
        right_panel = self.create_list_panel()
        splitter.addWidget(right_panel)
        
        # Imposta proporzioni
        splitter.setSizes([500, 700])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def create_input_panel(self):
        """Crea il pannello di inserimento fatture"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Gruppo: Caricamento File
        file_group = QGroupBox('📁 CARICAMENTO FILE')
        file_layout = QVBoxLayout()
        file_layout.setSpacing(10)
        
        # Pulsanti caricamento
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.btn_load_pdf = QPushButton('📄 Carica PDF')
        self.btn_load_pdf.setStyleSheet('QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #45a049; }')
        self.btn_load_pdf.clicked.connect(self.load_pdf_file)
        self.btn_load_pdf.setMinimumSize(140, 40)
        buttons_layout.addWidget(self.btn_load_pdf)
        
        self.btn_load_image = QPushButton('📷 Carica Foto')
        self.btn_load_image.clicked.connect(self.load_image_file)
        self.btn_load_image.setMinimumSize(140, 40)
        buttons_layout.addWidget(self.btn_load_image)
        
        file_layout.addLayout(buttons_layout)
        
        # Info file caricato
        self.lbl_file_info = QLabel('Nessun file caricato')
        self.lbl_file_info.setStyleSheet('QLabel { padding: 8px; background-color: #f5f5f5; border: 1px solid #e0e0e0; border-radius: 4px; color: #666666; }')
        self.lbl_file_info.setMinimumHeight(30)
        file_layout.addWidget(self.lbl_file_info)
        
        # Progress bar per OCR
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(25)
        file_layout.addWidget(self.progress_bar)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Gruppo: Dati Fattura
        data_group = QGroupBox('📋 DATI FATTURA')
        data_layout = QFormLayout()
        data_layout.setSpacing(10)
        
        # Data fattura
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('dd/MM/yyyy')
        self.date_edit.setMinimumHeight(35)
        data_layout.addRow('Data Fattura:', self.date_edit)
        
        # Numero fattura
        self.invoice_number_edit = QLineEdit()
        self.invoice_number_edit.setPlaceholderText('Numero fattura...')
        self.invoice_number_edit.setMinimumHeight(35)
        data_layout.addRow('Numero Fattura:', self.invoice_number_edit)
        
        # Fornitore
        self.supplier_combo = QComboBox()
        self.supplier_combo.setEditable(True)
        self.supplier_combo.setMinimumHeight(35)
        self.load_suppliers()
        data_layout.addRow('Fornitore:', self.supplier_combo)
        
        # Importo
        self.amount_edit = QLineEdit()
        self.amount_edit.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.amount_edit.setPlaceholderText('0.00')
        self.amount_edit.setMinimumHeight(35)
        self.amount_edit.setStyleSheet('QLineEdit { background-color: #f0fff0; border: 2px solid #90EE90; }')
        data_layout.addRow('Importo (€):', self.amount_edit)
        
        # P.IVA
        self.vat_number_edit = QLineEdit()
        self.vat_number_edit.setPlaceholderText('Partita IVA...')
        self.vat_number_edit.setMinimumHeight(35)
        data_layout.addRow('P.IVA:', self.vat_number_edit)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # Gruppo: Testo OCR
        ocr_group = QGroupBox('🔍 TESTO ESTRATTO (OCR)')
        ocr_layout = QVBoxLayout()
        ocr_layout.setSpacing(8)
        
        self.ocr_text_edit = QTextEdit()
        self.ocr_text_edit.setMaximumHeight(150)
        self.ocr_text_edit.setMinimumHeight(100)
        self.ocr_text_edit.setPlaceholderText('Il testo estratto apparirà qui...')
        ocr_layout.addWidget(self.ocr_text_edit)
        
        # Pulsanti OCR
        ocr_buttons_layout = QHBoxLayout()
        ocr_buttons_layout.setSpacing(10)
        
        self.btn_extract_data = QPushButton('🎯 Estrai Dati')
        self.btn_extract_data.setEnabled(False)
        self.btn_extract_data.clicked.connect(self.extract_data_from_text)
        self.btn_extract_data.setMinimumSize(120, 35)
        ocr_buttons_layout.addWidget(self.btn_extract_data)
        
        self.btn_clear_ocr = QPushButton('🗑️ Pulisci')
        self.btn_clear_ocr.clicked.connect(self.clear_ocr_text)
        self.btn_clear_ocr.setMinimumSize(120, 35)
        ocr_buttons_layout.addWidget(self.btn_clear_ocr)
        
        ocr_buttons_layout.addStretch()
        ocr_layout.addLayout(ocr_buttons_layout)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # Note
        notes_group = QGroupBox('📝 NOTE')
        notes_layout = QVBoxLayout()
        notes_layout.setSpacing(8)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setMinimumHeight(60)
        self.notes_edit.setPlaceholderText('Note aggiuntive...')
        notes_layout.addWidget(self.notes_edit)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Pulsanti azione
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(15)
        
        self.btn_save = QPushButton('💾 Salva Fattura')
        self.btn_save.setStyleSheet('QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #45a049; }')
        self.btn_save.clicked.connect(self.save_invoice)
        self.btn_save.setMinimumSize(150, 45)
        action_buttons_layout.addWidget(self.btn_save)
        
        self.btn_clear = QPushButton('🗑️ Pulisci Form')
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_clear.setMinimumSize(150, 45)
        action_buttons_layout.addWidget(self.btn_clear)
        
        layout.addLayout(action_buttons_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_list_panel(self):
        """Crea il pannello lista fatture"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Filtri
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel('Filtri:'))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Cerca per numero, fornitore...')
        self.search_edit.textChanged.connect(self.filter_invoices)
        self.search_edit.setMinimumHeight(35)
        filters_layout.addWidget(self.search_edit)
        
        self.btn_refresh = QPushButton('🔄 Aggiorna')
        self.btn_refresh.clicked.connect(self.load_invoices)
        self.btn_refresh.setMinimumSize(100, 35)
        filters_layout.addWidget(self.btn_refresh)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        # Tabella fatture
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels([
            'Data', 'Numero', 'Fornitore', 'Importo', 'File', 'Note'
        ])
        
        # Configura tabella
        header = self.invoices_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Numero
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Fornitore
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Importo
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # File
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Note
        
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.doubleClicked.connect(self.edit_invoice)
        
        layout.addWidget(QLabel('<b>📋 ELENCO FATTURE</b>'))
        layout.addWidget(self.invoices_table)
        
        # Pulsanti tabella
        table_buttons_layout = QHBoxLayout()
        
        self.btn_view_file = QPushButton('👁️ Visualizza File')
        self.btn_view_file.clicked.connect(self.view_invoice_file)
        table_buttons_layout.addWidget(self.btn_view_file)
        
        self.btn_edit = QPushButton('✏️ Modifica')
        self.btn_edit.clicked.connect(self.edit_invoice)
        table_buttons_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton('❌ Elimina')
        self.btn_delete.setStyleSheet('background-color: #f44336; color: white;')
        self.btn_delete.clicked.connect(self.delete_invoice)
        table_buttons_layout.addWidget(self.btn_delete)
        
        table_buttons_layout.addStretch()
        layout.addLayout(table_buttons_layout)
        
        widget.setLayout(layout)
        return widget
    
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
            self.lbl_file_info.setText(f'PDF: {os.path.basename(file_path)}')
            
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
                'Vuoi convertire l\'immagine in PDF ricercabile?\\n\\n'
                'Questo creerà un PDF con OCR per facilitare la ricerca.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.convert_image_to_pdf(file_path)
            else:
                self.current_file_path = file_path
                self.lbl_file_info.setText(f'Immagine: {os.path.basename(file_path)}')
                
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
                self.lbl_file_info.setText(f'PDF creato: {os.path.basename(pdf_path)}')
                
                # Mostra testo estratto
                if extracted_text:
                    self.ocr_text_edit.setPlainText(extracted_text)
                    self.btn_extract_data.setEnabled(True)
                    
                    # Estrai automaticamente i dati
                    self.extract_data_from_text()
                
                QMessageBox.information(
                    self,
                    'Conversione Completata',
                    f'Immagine convertita in PDF con successo!\\n\\nFile salvato: {pdf_path}'
                )
        
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(
                self,
                'Errore Conversione',
                f'Errore durante la conversione:\\n{str(e)}'
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
                'Testo estratto e dati popolati automaticamente.\\n'
                'Controlla e correggi i dati se necessario.'
            )

    def on_ocr_error(self, error_message):
        """Gestisce errori OCR"""
        self.progress_bar.setVisible(False)
        QMessageBox.warning(
            self,
            'Errore OCR',
            f'Errore durante l\'estrazione testo:\\n{error_message}'
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
                    f'Dati trovati: {", ".join(found_data)}\\n\\n'
                    'Controlla e correggi se necessario.'
                )
            else:
                QMessageBox.information(
                    self,
                    'Nessun Dato',
                    'Non sono stati trovati dati strutturati nel testo.\\n'
                    'Inserisci manualmente i dati della fattura.'
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                'Errore',
                f'Errore durante l\'estrazione dati:\\n{str(e)}'
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
            # Pulisci l'importo
            amount_str = data['total_amount']
            amount_str = amount_str.replace(',', '.')
            try:
                import re
                clean_amount = re.sub(r'[^\\d.]', '', amount_str)
                if clean_amount:
                    self.amount_edit.setText(clean_amount)
            except:
                pass
        
        # P.IVA
        if data.get('vat_number'):
            self.vat_number_edit.setText(data['vat_number'])
        
        # Nome fornitore
        if data.get('supplier_name'):
            supplier_name = data['supplier_name']
            for i in range(self.supplier_combo.count()):
                if supplier_name.lower() in self.supplier_combo.itemText(i).lower():
                    self.supplier_combo.setCurrentIndex(i)
                    break
            else:
                self.supplier_combo.setEditText(supplier_name)

    def clear_ocr_text(self):
        """Pulisce il testo OCR"""
        self.ocr_text_edit.clear()
        self.btn_extract_data.setEnabled(False)

    def save_invoice(self):
        """Salva la fattura nel database"""
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
                self.invoices_repo.update(self.current_invoice.id, invoice.to_dict())
                QMessageBox.information(self, 'Successo', 'Fattura aggiornata con successo!')
            else:
                self.invoices_repo.create(invoice.to_dict())
                QMessageBox.information(self, 'Successo', 'Fattura salvata con successo!')
            
            self.clear_form()
            self.load_invoices()
            self.invoice_saved.emit()
        
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore durante il salvataggio:\\n{str(e)}')

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
            self.lbl_file_info.setText(f'File: {os.path.basename(self.current_invoice.file_path)}')

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
            QMessageBox.warning(self, 'Errore', f'File non trovato:\\n{file_path}')
            return
        
        # Apri con applicazione predefinita del sistema
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:
                import subprocess
                subprocess.call(['xdg-open', file_path])
        
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Impossibile aprire il file:\\n{str(e)}')

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
            'Sei sicuro di voler eliminare questa fattura?\\n\\n'
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
                QMessageBox.critical(self, 'Errore', f'Errore durante l\'eliminazione:\\n{str(e)}')
