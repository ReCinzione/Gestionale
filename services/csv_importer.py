"""
Servizio per l'importazione di dati da file CSV.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox, QProgressBar, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt


class CSVImportDialog(QDialog):
    """Dialog per l'importazione di dati da CSV"""
    
    def __init__(self, parent, sales_repo, suppliers_repo, purchases_repo):
        super().__init__(parent)
        
        self.sales_repo = sales_repo
        self.suppliers_repo = suppliers_repo
        self.purchases_repo = purchases_repo
        
        self.csv_file_path = None
        self.csv_data = []
        self.csv_headers = []
        
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle('Importazione Dati da CSV')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # Selezione file
        file_group = QGroupBox('1. Selezione File CSV')
        file_layout = QHBoxLayout()
        
        self.lbl_file = QLabel('Nessun file selezionato')
        file_layout.addWidget(self.lbl_file)
        
        self.btn_browse = QPushButton('📁 Sfoglia...')
        self.btn_browse.clicked.connect(self.browse_file)
        file_layout.addWidget(self.btn_browse)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Tipo di importazione
        type_group = QGroupBox('2. Tipo di Dati')
        type_layout = QFormLayout()
        
        self.import_type_combo = QComboBox()
        self.import_type_combo.addItem('Vendite Giornaliere', 'sales')
        self.import_type_combo.addItem('Fornitori', 'suppliers')
        self.import_type_combo.addItem('Acquisti/Spese', 'purchases')
        type_layout.addRow('Tipo di dati da importare:', self.import_type_combo)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Anteprima e mappatura
        preview_group = QGroupBox('3. Anteprima e Mappatura Colonne')
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_table)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Mappatura colonne
        mapping_group = QGroupBox('4. Mappatura Colonne')
        self.mapping_layout = QFormLayout()
        mapping_group.setLayout(self.mapping_layout)
        layout.addWidget(mapping_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.btn_import = QPushButton('📥 Importa Dati')
        self.btn_import.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold;')
        self.btn_import.clicked.connect(self.import_data)
        self.btn_import.setEnabled(False)
        buttons_layout.addWidget(self.btn_import)
        
        self.btn_cancel = QPushButton('❌ Annulla')
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def browse_file(self):
        """Apre il dialog per selezionare il file CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Seleziona File CSV',
            '',
            'File CSV (*.csv);;Tutti i file (*.*)'
        )
        
        if file_path:
            self.csv_file_path = file_path
            self.lbl_file.setText(os.path.basename(file_path))
            self.load_csv_preview()
    
    def load_csv_preview(self):
        """Carica l'anteprima del file CSV"""
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8-sig') as file:
                # Prova a rilevare il delimitatore
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                
                # Leggi i dati
                self.csv_data = list(reader)
                
                if not self.csv_data:
                    QMessageBox.warning(self, 'Errore', 'Il file CSV è vuoto.')
                    return
                
                # Prima riga come headers
                self.csv_headers = self.csv_data[0]
                
                # Mostra anteprima (prime 5 righe)
                preview_data = self.csv_data[:6]  # Header + 5 righe
                
                self.preview_table.setRowCount(len(preview_data))
                self.preview_table.setColumnCount(len(self.csv_headers))
                self.preview_table.setHorizontalHeaderLabels([f"Col {i+1}" for i in range(len(self.csv_headers))])
                
                for row, row_data in enumerate(preview_data):
                    for col, cell_data in enumerate(row_data):
                        item = QTableWidgetItem(str(cell_data))
                        if row == 0:  # Header
                            item.setBackground(Qt.lightGray)
                        self.preview_table.setItem(row, col, item)
                
                self.create_mapping_controls()
                self.btn_import.setEnabled(True)
                
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore durante la lettura del file:\n{str(e)}')
    
    def create_mapping_controls(self):
        """Crea i controlli per la mappatura delle colonne"""
        # Pulisci layout esistente
        for i in reversed(range(self.mapping_layout.count())):
            self.mapping_layout.itemAt(i).widget().setParent(None)
        
        import_type = self.import_type_combo.currentData()
        
        # Definisci i campi richiesti per ogni tipo
        field_mappings = {
            'sales': [
                ('date', 'Data (YYYY-MM-DD o DD/MM/YYYY)'),
                ('start_capital', 'Capitale Iniziale'),
                ('cash_income', 'Incasso Contante'),
                ('coin_income', 'Incasso Moneta'),
                ('card_gross', 'Lordo Bancomat'),
                ('card_percent_fee', 'Percentuale Bancomat'),
                ('card_fixed_fee', 'Costo Fisso Bancomat'),
                ('satispay_gross', 'Lordo Satispay'),
                ('satispay_percent_fee', 'Percentuale Satispay'),
                ('satispay_fixed_fee', 'Costo Fisso Satispay'),
                ('notes', 'Note')
            ],
            'suppliers': [
                ('name', 'Nome Fornitore'),
                ('notes', 'Note')
            ],
            'purchases': [
                ('date', 'Data (YYYY-MM-DD o DD/MM/YYYY)'),
                ('supplier_name', 'Nome Fornitore'),
                ('description', 'Descrizione'),
                ('cash_payment', 'Pagamento Contante'),
                ('bank_payment', 'Pagamento Bancario'),
                ('notes', 'Note')
            ]
        }
        
        fields = field_mappings.get(import_type, [])
        
        # Crea combo per ogni campo
        self.field_combos = {}
        
        for field_key, field_label in fields:
            combo = QComboBox()
            combo.addItem('-- Non mappare --', None)
            
            for i, header in enumerate(self.csv_headers):
                combo.addItem(f"Colonna {i+1}: {header}", i)
            
            self.field_combos[field_key] = combo
            self.mapping_layout.addRow(f'{field_label}:', combo)
    
    def import_data(self):
        """Importa i dati dal CSV"""
        import_type = self.import_type_combo.currentData()
        
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(self.csv_data) - 1)  # Escludi header
            
            imported_count = 0
            error_count = 0
            
            for row_idx, row_data in enumerate(self.csv_data[1:], 1):  # Salta header
                self.progress_bar.setValue(row_idx - 1)
                
                try:
                    if import_type == 'sales':
                        self.import_sale_row(row_data)
                    elif import_type == 'suppliers':
                        self.import_supplier_row(row_data)
                    elif import_type == 'purchases':
                        self.import_purchase_row(row_data)
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"Errore riga {row_idx}: {e}")
                    error_count += 1
            
            self.progress_bar.setVisible(False)
            
            # Mostra risultato
            message = f"Importazione completata!\n\n"
            message += f"Righe importate: {imported_count}\n"
            if error_count > 0:
                message += f"Righe con errori: {error_count}"
            
            QMessageBox.information(self, 'Importazione Completata', message)
            self.accept()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, 'Errore', f'Errore durante l\'importazione:\n{str(e)}')
    
    def get_mapped_value(self, field_key: str, row_data: List[str]) -> Optional[str]:
        """Ottiene il valore mappato per un campo"""
        combo = self.field_combos.get(field_key)
        if not combo:
            return None
        
        col_index = combo.currentData()
        if col_index is None or col_index >= len(row_data):
            return None
        
        return row_data[col_index].strip()
    
    def parse_date(self, date_str: str) -> str:
        """Converte una data in formato YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Prova diversi formati
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Se nessun formato funziona, usa oggi
        return datetime.now().strftime('%Y-%m-%d')
    
    def import_sale_row(self, row_data: List[str]):
        """Importa una riga di vendita"""
        date_str = self.parse_date(self.get_mapped_value('date', row_data))
        
        sale_data = {
            'date': date_str,
            'start_capital': float(self.get_mapped_value('start_capital', row_data) or 0),
            'cash_income': float(self.get_mapped_value('cash_income', row_data) or 0),
            'coin_income': float(self.get_mapped_value('coin_income', row_data) or 0),
            'card_gross': float(self.get_mapped_value('card_gross', row_data) or 0),
            'card_percent_fee': float(self.get_mapped_value('card_percent_fee', row_data) or 1.95),
            'card_fixed_fee': float(self.get_mapped_value('card_fixed_fee', row_data) or 0.15),
            'satispay_gross': float(self.get_mapped_value('satispay_gross', row_data) or 0),
            'satispay_percent_fee': float(self.get_mapped_value('satispay_percent_fee', row_data) or 1.0),
            'satispay_fixed_fee': float(self.get_mapped_value('satispay_fixed_fee', row_data) or 0),
            'notes': self.get_mapped_value('notes', row_data) or ''
        }
        
        # Controlla se esiste già
        existing = self.sales_repo.get_by_date(date_str)
        if existing:
            self.sales_repo.update(date_str, sale_data)
        else:
            self.sales_repo.create(sale_data)
    
    def import_supplier_row(self, row_data: List[str]):
        """Importa una riga di fornitore"""
        name = self.get_mapped_value('name', row_data)
        if not name:
            raise ValueError("Nome fornitore mancante")
        
        # Controlla se esiste già
        existing = self.suppliers_repo.get_by_name(name)
        if not existing:
            notes = self.get_mapped_value('notes', row_data) or ''
            self.suppliers_repo.create(name, notes)
    
    def import_purchase_row(self, row_data: List[str]):
        """Importa una riga di acquisto"""
        date_str = self.parse_date(self.get_mapped_value('date', row_data))
        supplier_name = self.get_mapped_value('supplier_name', row_data)
        
        if not supplier_name:
            raise ValueError("Nome fornitore mancante")
        
        # Trova o crea il fornitore
        supplier = self.suppliers_repo.get_by_name(supplier_name)
        if not supplier:
            supplier_id = self.suppliers_repo.create(supplier_name)
        else:
            supplier_id = supplier['id']
        
        purchase_data = {
            'date': date_str,
            'supplier_id': supplier_id,
            'description': self.get_mapped_value('description', row_data) or '',
            'cash_payment': float(self.get_mapped_value('cash_payment', row_data) or 0),
            'bank_payment': float(self.get_mapped_value('bank_payment', row_data) or 0),
            'notes': self.get_mapped_value('notes', row_data) or ''
        }
        
        self.purchases_repo.create(purchase_data)
