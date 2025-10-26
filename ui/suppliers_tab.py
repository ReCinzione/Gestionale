"""
Tab per la gestione dei fornitori e delle spese.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit, QComboBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QFont
from datetime import datetime
from models.supplier import Supplier
from models.purchase import Purchase


class SuppliersTab(QWidget):
    """Tab per la gestione di fornitori e spese"""
    
    supplier_added = pyqtSignal()  # Segnale emesso quando si aggiunge un fornitore
    purchase_saved = pyqtSignal()  # Segnale emesso quando si salva un acquisto
    
    def __init__(self, suppliers_repo, purchases_repo):
        super().__init__()
        
        self.suppliers_repo = suppliers_repo
        self.purchases_repo = purchases_repo
        
        self.init_ui()
        self.load_suppliers()
        self.load_purchases()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        # Applica stili CSS moderni
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                font-size: 11px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                font-size: 11px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
            QDateEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                font-size: 11px;
                background-color: white;
            }
            QDateEdit:focus {
                border-color: #2196F3;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #333333;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #FAFAFA;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
                border-radius: 4px;
            }
            QLabel {
                color: #333333;
                font-size: 11px;
                font-weight: 500;
            }
            QTableWidget {
                gridline-color: #E0E0E0;
                background-color: white;
                alternate-background-color: #F5F5F5;
                selection-background-color: #E3F2FD;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
                color: #333333;
            }
            QTextEdit {
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #2196F3;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Splitter principale
        splitter = QSplitter(Qt.Horizontal)
        
        # Pannello sinistro: Gestione fornitori e inserimento spese
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Gruppo: Gestione Fornitori
        suppliers_group = QGroupBox('🏭 GESTIONE FORNITORI')
        suppliers_layout = QVBoxLayout()
        suppliers_layout.setSpacing(12)
        
        # Form nuovo fornitore
        new_supplier_layout = QHBoxLayout()
        new_supplier_layout.setSpacing(10)
        new_supplier_layout.addWidget(QLabel('Nuovo Fornitore:'))
        
        self.new_supplier_edit = QLineEdit()
        self.new_supplier_edit.setPlaceholderText('Nome fornitore...')
        self.new_supplier_edit.setMinimumHeight(35)
        new_supplier_layout.addWidget(self.new_supplier_edit)
        
        self.btn_add_supplier = QPushButton('➕ Aggiungi')
        self.btn_add_supplier.setStyleSheet('QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #45a049; }')
        self.btn_add_supplier.clicked.connect(self.add_supplier)
        self.btn_add_supplier.setMinimumSize(100, 35)
        new_supplier_layout.addWidget(self.btn_add_supplier)
        
        suppliers_layout.addLayout(new_supplier_layout)
        
        # Lista fornitori esistenti
        self.suppliers_combo = QComboBox()
        self.suppliers_combo.setEditable(False)
        self.suppliers_combo.setMinimumHeight(35)
        suppliers_layout.addWidget(QLabel('Fornitori Esistenti:'))
        suppliers_layout.addWidget(self.suppliers_combo)
        
        suppliers_group.setLayout(suppliers_layout)
        left_layout.addWidget(suppliers_group)
        
        # Gruppo: Inserimento Spese/Acquisti
        expenses_group = QGroupBox('💰 INSERIMENTO SPESE/ACQUISTI')
        expenses_layout = QFormLayout()
        expenses_layout.setSpacing(12)
        
        # Data
        self.expense_date_edit = QDateEdit()
        self.expense_date_edit.setCalendarPopup(True)
        self.expense_date_edit.setDate(QDate.currentDate())
        self.expense_date_edit.setDisplayFormat('dd/MM/yyyy')
        self.expense_date_edit.setMinimumHeight(35)
        expenses_layout.addRow('Data:', self.expense_date_edit)
        
        # Fornitore
        self.expense_supplier_combo = QComboBox()
        self.expense_supplier_combo.setMinimumHeight(35)
        expenses_layout.addRow('Fornitore:', self.expense_supplier_combo)
        
        # Descrizione (Faccilongo)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText('Descrizione acquisto/spesa...')
        self.description_edit.setMinimumHeight(35)
        expenses_layout.addRow('Descrizione:', self.description_edit)
        
        # Validatore per importi
        double_validator = QDoubleValidator(0.0, 999999.99, 2)
        
        # Pagamento Contante
        self.cash_payment_edit = QLineEdit()
        self.cash_payment_edit.setValidator(double_validator)
        self.cash_payment_edit.setText('0.00')
        self.cash_payment_edit.textChanged.connect(self.calculate_expense_total)
        self.cash_payment_edit.setMinimumHeight(35)
        self.cash_payment_edit.setStyleSheet('QLineEdit { background-color: #f0fff0; border: 2px solid #90EE90; }')
        expenses_layout.addRow('Pagamento Contante (€):', self.cash_payment_edit)
        
        # Pagamento Bancario
        self.bank_payment_edit = QLineEdit()
        self.bank_payment_edit.setValidator(double_validator)
        self.bank_payment_edit.setText('0.00')
        self.bank_payment_edit.textChanged.connect(self.calculate_expense_total)
        self.bank_payment_edit.setMinimumHeight(35)
        self.bank_payment_edit.setStyleSheet('QLineEdit { background-color: #f0fff0; border: 2px solid #90EE90; }')
        expenses_layout.addRow('Pagamento Bancario (€):', self.bank_payment_edit)
        
        # Totale
        self.lbl_expense_total = QLabel('€ 0,00')
        self.lbl_expense_total.setStyleSheet('QLabel { background-color: #fff3cd; padding: 10px; font-weight: bold; border: 2px solid #ffc107; border-radius: 4px; color: #856404; }')
        self.lbl_expense_total.setMinimumHeight(35)
        expenses_layout.addRow('Totale:', self.lbl_expense_total)
        
        # Note
        self.expense_notes_edit = QTextEdit()
        self.expense_notes_edit.setMaximumHeight(60)
        self.expense_notes_edit.setMinimumHeight(50)
        self.expense_notes_edit.setPlaceholderText('Note aggiuntive...')
        expenses_layout.addRow('Note:', self.expense_notes_edit)
        
        expenses_group.setLayout(expenses_layout)
        left_layout.addWidget(expenses_group)
        
        # Pulsanti azione spese
        expense_buttons_layout = QHBoxLayout()
        expense_buttons_layout.setSpacing(15)
        
        self.btn_save_expense = QPushButton('💾 Salva Spesa')
        self.btn_save_expense.setStyleSheet('QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #45a049; }')
        self.btn_save_expense.clicked.connect(self.save_expense)
        self.btn_save_expense.setMinimumSize(140, 40)
        expense_buttons_layout.addWidget(self.btn_save_expense)
        
        self.btn_clear_expense = QPushButton('🗑️ Pulisci')
        self.btn_clear_expense.clicked.connect(self.clear_expense_form)
        self.btn_clear_expense.setMinimumSize(140, 40)
        expense_buttons_layout.addWidget(self.btn_clear_expense)
        
        left_layout.addLayout(expense_buttons_layout)
        left_layout.addStretch()
        
        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)
        
        # Pannello destro: Lista spese e riepiloghi
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Filtri per le spese
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel('Filtri:'))
        
        self.filter_date_edit = QDateEdit()
        self.filter_date_edit.setCalendarPopup(True)
        self.filter_date_edit.setDate(QDate.currentDate())
        self.filter_date_edit.setDisplayFormat('dd/MM/yyyy')
        self.filter_date_edit.dateChanged.connect(self.filter_purchases)
        filters_layout.addWidget(QLabel('Data:'))
        filters_layout.addWidget(self.filter_date_edit)
        
        self.btn_show_all = QPushButton('📅 Mostra Tutti')
        self.btn_show_all.clicked.connect(self.show_all_purchases)
        filters_layout.addWidget(self.btn_show_all)
        
        self.btn_show_today = QPushButton('📅 Oggi')
        self.btn_show_today.clicked.connect(self.show_today_purchases)
        filters_layout.addWidget(self.btn_show_today)
        
        filters_layout.addStretch()
        right_layout.addLayout(filters_layout)
        
        # Tabella spese
        self.purchases_table = QTableWidget()
        self.purchases_table.setColumnCount(6)
        self.purchases_table.setHorizontalHeaderLabels([
            'Data', 'Fornitore', 'Descrizione', 'Contante', 'Bancario', 'Totale'
        ])
        
        # Configura tabella
        header = self.purchases_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fornitore
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Descrizione
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Contante
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Bancario
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Totale
        
        self.purchases_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.purchases_table.setAlternatingRowColors(True)
        self.purchases_table.doubleClicked.connect(self.edit_purchase)
        
        right_layout.addWidget(QLabel('<b>📋 ELENCO SPESE/ACQUISTI</b>'))
        right_layout.addWidget(self.purchases_table)
        
        # Riepiloghi
        summary_group = QGroupBox('📊 RIEPILOGO')
        summary_group.setStyleSheet('QGroupBox { font-weight: bold; background-color: #F0FFF0; }')
        summary_layout = QFormLayout()
        
        self.lbl_total_cash = QLabel('€ 0,00')
        self.lbl_total_cash.setStyleSheet('background-color: #FFE4E1; padding: 5px; font-weight: bold;')
        summary_layout.addRow('Totale Pagamenti Contanti:', self.lbl_total_cash)
        
        self.lbl_total_bank = QLabel('€ 0,00')
        self.lbl_total_bank.setStyleSheet('background-color: #E0FFFF; padding: 5px; font-weight: bold;')
        summary_layout.addRow('Totale Pagamenti Bancari:', self.lbl_total_bank)
        
        self.lbl_grand_total = QLabel('€ 0,00')
        self.lbl_grand_total.setStyleSheet('background-color: #FFFF99; padding: 5px; font-weight: bold; font-size: 12pt;')
        summary_layout.addRow('TOTALE GENERALE:', self.lbl_grand_total)
        
        summary_group.setLayout(summary_layout)
        right_layout.addWidget(summary_group)
        
        # Pulsanti azione tabella
        table_buttons_layout = QHBoxLayout()
        
        self.btn_edit_purchase = QPushButton('✏️ Modifica')
        self.btn_edit_purchase.clicked.connect(self.edit_purchase)
        table_buttons_layout.addWidget(self.btn_edit_purchase)
        
        self.btn_delete_purchase = QPushButton('❌ Elimina')
        self.btn_delete_purchase.setStyleSheet('background-color: #f44336; color: white;')
        self.btn_delete_purchase.clicked.connect(self.delete_purchase)
        table_buttons_layout.addWidget(self.btn_delete_purchase)
        
        table_buttons_layout.addStretch()
        right_layout.addLayout(table_buttons_layout)
        
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        
        # Imposta proporzioni splitter
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def load_suppliers(self):
        """Carica la lista dei fornitori"""
        suppliers = self.suppliers_repo.get_all_active()
        
        # Aggiorna combo principale
        self.suppliers_combo.clear()
        for supplier in suppliers:
            self.suppliers_combo.addItem(supplier['name'], supplier['id'])
        
        # Aggiorna combo spese
        self.expense_supplier_combo.clear()
        for supplier in suppliers:
            self.expense_supplier_combo.addItem(supplier['name'], supplier['id'])
    
    def add_supplier(self):
        """Aggiunge un nuovo fornitore"""
        name = self.new_supplier_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, 'Attenzione', 'Inserisci il nome del fornitore.')
            return
        
        # Controlla se esiste già
        existing = self.suppliers_repo.get_by_name(name)
        if existing:
            QMessageBox.warning(self, 'Attenzione', f'Il fornitore "{name}" esiste già.')
            return
        
        try:
            supplier_id = self.suppliers_repo.create(name)
            QMessageBox.information(self, 'Successo', f'Fornitore "{name}" aggiunto con successo!')
            
            self.new_supplier_edit.clear()
            self.load_suppliers()
            self.supplier_added.emit()
            
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore durante l\'aggiunta del fornitore:\n{str(e)}')
    
    def calculate_expense_total(self):
        """Calcola il totale della spesa"""
        try:
            cash = float(self.cash_payment_edit.text() or 0)
            bank = float(self.bank_payment_edit.text() or 0)
            total = cash + bank
            
            self.lbl_expense_total.setText(f'€ {total:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
        except ValueError:
            self.lbl_expense_total.setText('€ 0,00')
    
    def save_expense(self):
        """Salva una nuova spesa"""
        # Validazioni
        if self.expense_supplier_combo.currentData() is None:
            QMessageBox.warning(self, 'Attenzione', 'Seleziona un fornitore.')
            return
        
        description = self.description_edit.text().strip()
        if not description:
            QMessageBox.warning(self, 'Attenzione', 'Inserisci una descrizione.')
            return
        
        try:
            cash = float(self.cash_payment_edit.text() or 0)
            bank = float(self.bank_payment_edit.text() or 0)
            
            if cash == 0 and bank == 0:
                QMessageBox.warning(self, 'Attenzione', 'Inserisci almeno un importo (contante o bancario).')
                return
            
            # Crea l'acquisto
            purchase = Purchase(
                date=self.expense_date_edit.date().toString('yyyy-MM-dd'),
                supplier_id=self.expense_supplier_combo.currentData(),
                description=description,
                cash_payment=cash,
                bank_payment=bank,
                notes=self.expense_notes_edit.toPlainText()
            )
            
            purchase_id = self.purchases_repo.create(purchase.to_dict())
            QMessageBox.information(self, 'Successo', 'Spesa salvata con successo!')
            
            self.clear_expense_form()
            self.load_purchases()
            self.purchase_saved.emit()
            
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore durante il salvataggio:\n{str(e)}')
    
    def clear_expense_form(self):
        """Pulisce il form delle spese"""
        self.expense_date_edit.setDate(QDate.currentDate())
        if self.expense_supplier_combo.count() > 0:
            self.expense_supplier_combo.setCurrentIndex(0)
        self.description_edit.clear()
        self.cash_payment_edit.setText('0.00')
        self.bank_payment_edit.setText('0.00')
        self.expense_notes_edit.clear()
        self.calculate_expense_total()
    
    def load_purchases(self):
        """Carica tutte le spese nella tabella"""
        purchases = self.purchases_repo.get_by_date_range('2020-01-01', '2030-12-31')
        self.populate_purchases_table(purchases)
        self.update_summary(purchases)
    
    def filter_purchases(self):
        """Filtra le spese per data"""
        date_str = self.filter_date_edit.date().toString('yyyy-MM-dd')
        purchases = self.purchases_repo.get_by_date(date_str)
        self.populate_purchases_table(purchases)
        self.update_summary(purchases)
    
    def show_all_purchases(self):
        """Mostra tutte le spese"""
        self.load_purchases()
    
    def show_today_purchases(self):
        """Mostra le spese di oggi"""
        self.filter_date_edit.setDate(QDate.currentDate())
        self.filter_purchases()
    
    def populate_purchases_table(self, purchases):
        """Popola la tabella con le spese"""
        self.purchases_table.setRowCount(len(purchases))
        
        for row, purchase in enumerate(purchases):
            # Data
            date_item = QTableWidgetItem(purchase['date'])
            self.purchases_table.setItem(row, 0, date_item)
            
            # Fornitore
            supplier_item = QTableWidgetItem(purchase.get('supplier_name', ''))
            self.purchases_table.setItem(row, 1, supplier_item)
            
            # Descrizione
            desc_item = QTableWidgetItem(purchase.get('description', ''))
            self.purchases_table.setItem(row, 2, desc_item)
            
            # Contante
            cash_item = QTableWidgetItem(f"€ {purchase.get('cash_payment', 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            cash_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.purchases_table.setItem(row, 3, cash_item)
            
            # Bancario
            bank_item = QTableWidgetItem(f"€ {purchase.get('bank_payment', 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            bank_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.purchases_table.setItem(row, 4, bank_item)
            
            # Totale
            total = purchase.get('cash_payment', 0) + purchase.get('bank_payment', 0)
            total_item = QTableWidgetItem(f"€ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setBackground(Qt.lightGray)
            self.purchases_table.setItem(row, 5, total_item)
            
            # Memorizza l'ID per modifiche/eliminazioni
            date_item.setData(Qt.UserRole, purchase['id'])
    
    def update_summary(self, purchases):
        """Aggiorna i riepiloghi"""
        total_cash = sum(p.get('cash_payment', 0) for p in purchases)
        total_bank = sum(p.get('bank_payment', 0) for p in purchases)
        grand_total = total_cash + total_bank
        
        self.lbl_total_cash.setText(f"€ {total_cash:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.lbl_total_bank.setText(f"€ {total_bank:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.lbl_grand_total.setText(f"€ {grand_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    def edit_purchase(self):
        """Modifica la spesa selezionata"""
        current_row = self.purchases_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Attenzione', 'Seleziona una spesa da modificare.')
            return
        
        # Ottieni l'ID della spesa
        purchase_id = self.purchases_table.item(current_row, 0).data(Qt.UserRole)
        purchase_data = self.purchases_repo.get_by_id(purchase_id)
        
        if not purchase_data:
            QMessageBox.warning(self, 'Errore', 'Spesa non trovata.')
            return
        
        # TODO: Implementare dialogo di modifica
        QMessageBox.information(self, 'Info', 'Funzione di modifica in sviluppo.')
    
    def delete_purchase(self):
        """Elimina la spesa selezionata"""
        current_row = self.purchases_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Attenzione', 'Seleziona una spesa da eliminare.')
            return
        
        # Ottieni l'ID della spesa
        purchase_id = self.purchases_table.item(current_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            'Conferma Eliminazione',
            'Sei sicuro di voler eliminare questa spesa?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.purchases_repo.delete(purchase_id)
                QMessageBox.information(self, 'Successo', 'Spesa eliminata con successo!')
                self.load_purchases()
                self.purchase_saved.emit()
            except Exception as e:
                QMessageBox.critical(self, 'Errore', f'Errore durante l\'eliminazione:\n{str(e)}')
    
    def refresh_purchases(self):
        """Aggiorna la lista delle spese (chiamato dall'esterno)"""
        self.load_purchases()
