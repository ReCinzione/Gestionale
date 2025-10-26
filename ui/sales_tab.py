"""
Tab per la gestione delle vendite giornaliere.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QFont
from datetime import datetime
from models.sale import Sale
from services.calculator import SalesCalculator


class SalesTab(QWidget):
    """Tab per l'inserimento e visualizzazione delle vendite giornaliere"""
    
    sale_saved = pyqtSignal()  # Segnale emesso quando si salva una vendita
    
    def __init__(self, sales_repo, purchases_repo, suppliers_repo):
        super().__init__()
        
        self.sales_repo = sales_repo
        self.purchases_repo = purchases_repo
        self.suppliers_repo = suppliers_repo
        self.calculator = SalesCalculator()
        
        self.current_sale = None
        
        self.init_ui()
        self.load_today_sale()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        layout = QVBoxLayout()
        
        # Applica stile moderno al tab
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
            
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            
            QLineEdit:focus {
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
        """)
        
        # Sezione selezione data
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)
        
        date_label = QLabel('<b>Data:</b>')
        date_label.setStyleSheet('font-size: 16px; color: #333333; font-weight: 600;')
        date_layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('dd/MM/yyyy')
        self.date_edit.dateChanged.connect(self.on_date_changed)
        date_layout.addWidget(self.date_edit)
        
        self.btn_today = QPushButton('📅 Oggi')
        self.btn_today.clicked.connect(self.go_to_today)
        self.btn_today.setMinimumSize(100, 40)
        date_layout.addWidget(self.btn_today)
        
        self.btn_prev = QPushButton('◀ Precedente')
        self.btn_prev.clicked.connect(self.go_to_previous_day)
        self.btn_prev.setMinimumSize(120, 40)
        date_layout.addWidget(self.btn_prev)
        
        self.btn_next = QPushButton('Successivo ▶')
        self.btn_next.clicked.connect(self.go_to_next_day)
        self.btn_next.setMinimumSize(120, 40)
        date_layout.addWidget(self.btn_next)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Layout principale con due colonne
        main_layout = QHBoxLayout()
        
        # Colonna sinistra: Input dati
        left_column = QVBoxLayout()
        
        # Gruppo: Inserire i dati della giornata
        input_group = QGroupBox('INSERIRE I DATI DELLA GIORNATA')
        input_layout = QFormLayout()
        input_layout.setSpacing(12)
        
        # Validatore per numeri decimali
        double_validator = QDoubleValidator(0.0, 999999.99, 2)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        
        # Capitale di inizio giornata
        self.start_capital_edit = QLineEdit()
        self.start_capital_edit.setValidator(double_validator)
        self.start_capital_edit.setText('0.00')
        self.start_capital_edit.textChanged.connect(self.calculate_totals)
        self.start_capital_edit.setMinimumHeight(35)
        input_layout.addRow('Capitale di inizio giornata:', self.start_capital_edit)
        
        # Contare il contante
        self.cash_income_edit = QLineEdit()
        self.cash_income_edit.setValidator(double_validator)
        self.cash_income_edit.setText('0.00')
        self.cash_income_edit.textChanged.connect(self.calculate_totals)
        self.cash_income_edit.setStyleSheet('QLineEdit { background-color: #e8f5e8; border: 2px solid #4caf50; }')
        self.cash_income_edit.setMinimumHeight(35)
        input_layout.addRow('Contare il contante:', self.cash_income_edit)
        
        # Contare la moneta
        self.coin_income_edit = QLineEdit()
        self.coin_income_edit.setValidator(double_validator)
        self.coin_income_edit.setText('0.00')
        self.coin_income_edit.textChanged.connect(self.calculate_totals)
        self.coin_income_edit.setStyleSheet('QLineEdit { background-color: #e8f5e8; border: 2px solid #4caf50; }')
        self.coin_income_edit.setMinimumHeight(35)
        input_layout.addRow('Contare la moneta:', self.coin_income_edit)
        
        # Bancomat
        bancomat_layout = QHBoxLayout()
        bancomat_layout.setSpacing(8)
        
        self.card_gross_edit = QLineEdit()
        self.card_gross_edit.setValidator(double_validator)
        self.card_gross_edit.setText('0.00')
        self.card_gross_edit.textChanged.connect(self.calculate_totals)
        self.card_gross_edit.setStyleSheet('QLineEdit { background-color: #e8f5e8; border: 2px solid #4caf50; }')
        self.card_gross_edit.setMinimumHeight(35)
        bancomat_layout.addWidget(self.card_gross_edit)
        
        percent_label = QLabel('%')
        percent_label.setStyleSheet('font-weight: 600; color: #333333;')
        bancomat_layout.addWidget(percent_label)
        
        self.card_percent_edit = QLineEdit()
        self.card_percent_edit.setValidator(QDoubleValidator(0.0, 100.0, 2))
        self.card_percent_edit.setText('1.95')
        self.card_percent_edit.setMaximumWidth(80)
        self.card_percent_edit.setMinimumHeight(35)
        self.card_percent_edit.textChanged.connect(self.calculate_totals)
        bancomat_layout.addWidget(self.card_percent_edit)
        
        euro_label = QLabel('€')
        euro_label.setStyleSheet('font-weight: 600; color: #333333;')
        bancomat_layout.addWidget(euro_label)
        
        self.card_fixed_edit = QLineEdit()
        self.card_fixed_edit.setValidator(double_validator)
        self.card_fixed_edit.setText('0.15')
        self.card_fixed_edit.setMaximumWidth(80)
        self.card_fixed_edit.setMinimumHeight(35)
        self.card_fixed_edit.textChanged.connect(self.calculate_totals)
        bancomat_layout.addWidget(self.card_fixed_edit)
        
        input_layout.addRow('Lordo transazioni Bancomat:', bancomat_layout)
        
        # Satispay
        satispay_layout = QHBoxLayout()
        satispay_layout.setSpacing(8)
        
        self.satispay_gross_edit = QLineEdit()
        self.satispay_gross_edit.setValidator(double_validator)
        self.satispay_gross_edit.setText('0.00')
        self.satispay_gross_edit.textChanged.connect(self.calculate_totals)
        self.satispay_gross_edit.setStyleSheet('QLineEdit { background-color: #e8f5e8; border: 2px solid #4caf50; }')
        self.satispay_gross_edit.setMinimumHeight(35)
        satispay_layout.addWidget(self.satispay_gross_edit)
        
        percent_label2 = QLabel('%')
        percent_label2.setStyleSheet('font-weight: 600; color: #333333;')
        satispay_layout.addWidget(percent_label2)
        
        self.satispay_percent_edit = QLineEdit()
        self.satispay_percent_edit.setValidator(QDoubleValidator(0.0, 100.0, 2))
        self.satispay_percent_edit.setText('1.00')
        self.satispay_percent_edit.setMaximumWidth(80)
        self.satispay_percent_edit.setMinimumHeight(35)
        self.satispay_percent_edit.textChanged.connect(self.calculate_totals)
        satispay_layout.addWidget(self.satispay_percent_edit)
        
        euro_label2 = QLabel('€')
        euro_label2.setStyleSheet('font-weight: 600; color: #333333;')
        satispay_layout.addWidget(euro_label2)
        
        self.satispay_fixed_edit = QLineEdit()
        self.satispay_fixed_edit.setValidator(double_validator)
        self.satispay_fixed_edit.setText('0.00')
        self.satispay_fixed_edit.setMaximumWidth(80)
        self.satispay_fixed_edit.setMinimumHeight(35)
        self.satispay_fixed_edit.textChanged.connect(self.calculate_totals)
        satispay_layout.addWidget(self.satispay_fixed_edit)
        
        input_layout.addRow('Lordo transazioni Satispay:', satispay_layout)
        
        input_group.setLayout(input_layout)
        left_column.addWidget(input_group)
        
        # Note
        notes_group = QGroupBox('Note')
        notes_layout = QVBoxLayout()
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_edit)
        notes_group.setLayout(notes_layout)
        left_column.addWidget(notes_group)
        
        # Pulsanti azione
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.btn_save = QPushButton('💾 Salva')
        self.btn_save.setStyleSheet('QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #45a049; }')
        self.btn_save.clicked.connect(self.save_sale)
        self.btn_save.setMinimumSize(120, 45)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_clear = QPushButton('🗑️ Pulisci')
        self.btn_clear.setStyleSheet('QPushButton { background-color: #ff9800; } QPushButton:hover { background-color: #f57c00; }')
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_clear.setMinimumSize(120, 45)
        buttons_layout.addWidget(self.btn_clear)
        
        self.btn_delete = QPushButton('❌ Elimina')
        self.btn_delete.setStyleSheet('QPushButton { background-color: #f44336; } QPushButton:hover { background-color: #d32f2f; }')
        self.btn_delete.clicked.connect(self.delete_sale)
        self.btn_delete.setMinimumSize(120, 45)
        buttons_layout.addWidget(self.btn_delete)
        
        left_column.addLayout(buttons_layout)
        left_column.addStretch()
        
        main_layout.addLayout(left_column, 1)
        
        # Colonna destra: Bilancio giornaliero
        right_column = QVBoxLayout()
        
        balance_group = QGroupBox('BILANCIO GIORNALIERO')
        balance_layout = QFormLayout()
        balance_layout.setSpacing(8)
        
        # Font per i totali
        total_font = QFont()
        total_font.setBold(True)
        total_font.setPointSize(11)
        
        # Incasso Contante
        self.lbl_cash_total = QLabel('€ 0,00')
        self.lbl_cash_total.setFont(total_font)
        self.lbl_cash_total.setStyleSheet('QLabel { background-color: #e1f5fe; padding: 8px; border-radius: 4px; color: #0277bd; border: 1px solid #81d4fa; }')
        self.lbl_cash_total.setMinimumHeight(30)
        balance_layout.addRow('Incasso Contante:', self.lbl_cash_total)
        
        # Incasso Bancario
        self.lbl_bank_total = QLabel('€ 0,00')
        self.lbl_bank_total.setFont(total_font)
        self.lbl_bank_total.setStyleSheet('QLabel { background-color: #e1f5fe; padding: 8px; border-radius: 4px; color: #0277bd; border: 1px solid #81d4fa; }')
        self.lbl_bank_total.setMinimumHeight(30)
        balance_layout.addRow('Incasso Bancario:', self.lbl_bank_total)
        
        # Dettagli commissioni
        self.lbl_card_fees = QLabel('€ 0,00')
        balance_layout.addRow('  - Commissioni Bancomat:', self.lbl_card_fees)
        
        self.lbl_satispay_fees = QLabel('€ 0,00')
        balance_layout.addRow('  - Commissioni Satispay:', self.lbl_satispay_fees)
        
        balance_layout.addRow('', QLabel(''))  # Spazio
        
        # Fornitori pagamento contanti
        self.lbl_supplier_cash = QLabel('€ 0,00')
        self.lbl_supplier_cash.setStyleSheet('QLabel { background-color: #fff3e0; padding: 8px; border-radius: 4px; color: #e65100; border: 1px solid #ffcc02; }')
        self.lbl_supplier_cash.setMinimumHeight(30)
        balance_layout.addRow('Fornitori pagamento contanti:', self.lbl_supplier_cash)
        
        # Fornitori pagamento bancario
        self.lbl_supplier_bank = QLabel('€ 0,00')
        self.lbl_supplier_bank.setStyleSheet('QLabel { background-color: #fff3e0; padding: 8px; border-radius: 4px; color: #e65100; border: 1px solid #ffcc02; }')
        self.lbl_supplier_bank.setMinimumHeight(30)
        balance_layout.addRow('Fornitori pagamento bancario:', self.lbl_supplier_bank)
        
        balance_layout.addRow('', QLabel(''))  # Spazio
        
        # Font più grande per i totali principali
        main_total_font = QFont()
        main_total_font.setBold(True)
        main_total_font.setPointSize(12)
        
        # Corrispettivo
        self.lbl_takings = QLabel('€ 0,00')
        self.lbl_takings.setFont(main_total_font)
        self.lbl_takings.setStyleSheet('QLabel { background-color: #f3e5f5; padding: 10px; border-radius: 6px; color: #4a148c; border: 2px solid #9c27b0; font-weight: 700; }')
        self.lbl_takings.setMinimumHeight(35)
        balance_layout.addRow('Corrispettivo:', self.lbl_takings)
        
        # Incasso Totale
        self.lbl_total_income = QLabel('€ 0,00')
        self.lbl_total_income.setFont(main_total_font)
        self.lbl_total_income.setStyleSheet('QLabel { background-color: #f3e5f5; padding: 10px; border-radius: 6px; color: #4a148c; border: 2px solid #9c27b0; font-weight: 700; }')
        self.lbl_total_income.setMinimumHeight(35)
        balance_layout.addRow('Incasso Totale:', self.lbl_total_income)
        
        # Ricavo Giornaliero
        self.lbl_daily_profit = QLabel('€ 0,00')
        self.lbl_daily_profit.setFont(main_total_font)
        self.lbl_daily_profit.setStyleSheet('QLabel { background-color: #e8f5e8; padding: 10px; border-radius: 6px; color: #1b5e20; border: 2px solid #4caf50; font-weight: 700; }')
        self.lbl_daily_profit.setMinimumHeight(35)
        balance_layout.addRow('Ricavo Giornaliero:', self.lbl_daily_profit)
        
        balance_group.setLayout(balance_layout)
        right_column.addWidget(balance_group)
        right_column.addStretch()
        
        main_layout.addLayout(right_column, 1)
        
        layout.addLayout(main_layout)
        
        self.setLayout(layout)
    
    def on_date_changed(self):
        """Gestisce il cambio di data"""
        date_str = self.date_edit.date().toString('yyyy-MM-dd')
        self.load_sale_by_date(date_str)
    
    def go_to_today(self):
        """Va alla data odierna"""
        self.date_edit.setDate(QDate.currentDate())
    
    def go_to_previous_day(self):
        """Va al giorno precedente"""
        current = self.date_edit.date()
        self.date_edit.setDate(current.addDays(-1))
    
    def go_to_next_day(self):
        """Va al giorno successivo"""
        current = self.date_edit.date()
        self.date_edit.setDate(current.addDays(1))
    
    def load_today_sale(self):
        """Carica la vendita di oggi"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.load_sale_by_date(today)
    
    def load_sale_by_date(self, date_str):
        """Carica una vendita per data"""
        sale_data = self.sales_repo.get_by_date(date_str)
        
        if sale_data:
            self.current_sale = Sale.from_dict(sale_data)
            self.populate_form(self.current_sale)
        else:
            self.current_sale = None
            self.clear_form()
        
        self.calculate_totals()
    
    def populate_form(self, sale: Sale):
        """Popola il form con i dati di una vendita"""
        self.start_capital_edit.setText(f"{sale.start_capital:.2f}")
        self.cash_income_edit.setText(f"{sale.cash_income:.2f}")
        self.coin_income_edit.setText(f"{sale.coin_income:.2f}")
        self.card_gross_edit.setText(f"{sale.card_gross:.2f}")
        self.card_percent_edit.setText(f"{sale.card_percent_fee:.2f}")
        self.card_fixed_edit.setText(f"{sale.card_fixed_fee:.2f}")
        self.satispay_gross_edit.setText(f"{sale.satispay_gross:.2f}")
        self.satispay_percent_edit.setText(f"{sale.satispay_percent_fee:.2f}")
        self.satispay_fixed_edit.setText(f"{sale.satispay_fixed_fee:.2f}")
        self.notes_edit.setPlainText(sale.notes)
    
    def clear_form(self):
        """Pulisce il form"""
        self.start_capital_edit.setText('0.00')
        self.cash_income_edit.setText('0.00')
        self.coin_income_edit.setText('0.00')
        self.card_gross_edit.setText('0.00')
        self.card_percent_edit.setText('1.95')
        self.card_fixed_edit.setText('0.15')
        self.satispay_gross_edit.setText('0.00')
        self.satispay_percent_edit.setText('1.00')
        self.satispay_fixed_edit.setText('0.00')
        self.notes_edit.clear()
        self.calculate_totals()
    
    def get_sale_from_form(self) -> Sale:
        """Crea un oggetto Sale dai dati del form"""
        date_str = self.date_edit.date().toString('yyyy-MM-dd')
        
        return Sale(
            date=date_str,
            start_capital=float(self.start_capital_edit.text() or 0),
            cash_income=float(self.cash_income_edit.text() or 0),
            coin_income=float(self.coin_income_edit.text() or 0),
            card_gross=float(self.card_gross_edit.text() or 0),
            card_percent_fee=float(self.card_percent_edit.text() or 0),
            card_fixed_fee=float(self.card_fixed_edit.text() or 0),
            satispay_gross=float(self.satispay_gross_edit.text() or 0),
            satispay_percent_fee=float(self.satispay_percent_edit.text() or 0),
            satispay_fixed_fee=float(self.satispay_fixed_edit.text() or 0),
            notes=self.notes_edit.toPlainText()
        )
    
    def calculate_totals(self):
        """Calcola e aggiorna tutti i totali"""
        try:
            sale = self.get_sale_from_form()
            
            # Ottieni pagamenti fornitori per la data selezionata
            date_str = self.date_edit.date().toString('yyyy-MM-dd')
            purchases = self.purchases_repo.get_by_date(date_str)
            
            supplier_cash = sum(p.get('cash_payment', 0) for p in purchases)
            supplier_bank = sum(p.get('bank_payment', 0) for p in purchases)
            supplier_total = supplier_cash + supplier_bank
            
            # Calcola tutti i valori
            calcs = self.calculator.get_all_calculations(sale, supplier_total)
            
            # Aggiorna le label
            self.lbl_cash_total.setText(self.calculator.format_currency(calcs['cash_total']))
            self.lbl_bank_total.setText(self.calculator.format_currency(calcs['bank_total']))
            self.lbl_card_fees.setText(self.calculator.format_currency(calcs['card_fees']))
            self.lbl_satispay_fees.setText(self.calculator.format_currency(calcs['satispay_fees']))
            self.lbl_supplier_cash.setText(self.calculator.format_currency(supplier_cash))
            self.lbl_supplier_bank.setText(self.calculator.format_currency(supplier_bank))
            self.lbl_takings.setText(self.calculator.format_currency(calcs['takings']))
            self.lbl_total_income.setText(self.calculator.format_currency(calcs['takings']))
            self.lbl_daily_profit.setText(self.calculator.format_currency(calcs['daily_profit']))
            
        except ValueError:
            # Se ci sono errori di conversione, ignora
            pass
    
    def save_sale(self):
        """Salva la vendita nel database"""
        try:
            sale = self.get_sale_from_form()
            
            # Controlla se esiste già una vendita per questa data
            existing = self.sales_repo.get_by_date(sale.date)
            
            if existing:
                # Aggiorna
                self.sales_repo.update(sale.date, sale.to_dict())
                QMessageBox.information(self, 'Successo', 'Vendita aggiornata con successo!')
            else:
                # Crea nuova
                self.sales_repo.create(sale.to_dict())
                QMessageBox.information(self, 'Successo', 'Vendita salvata con successo!')
            
            self.current_sale = sale
            self.sale_saved.emit()
            
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore durante il salvataggio:\n{str(e)}')
    
    def delete_sale(self):
        """Elimina la vendita corrente"""
        if not self.current_sale:
            QMessageBox.warning(self, 'Attenzione', 'Nessuna vendita da eliminare per questa data.')
            return
        
        reply = QMessageBox.question(
            self,
            'Conferma Eliminazione',
            f'Sei sicuro di voler eliminare la vendita del {self.current_sale.date}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.sales_repo.delete(self.current_sale.date)
                QMessageBox.information(self, 'Successo', 'Vendita eliminata con successo!')
                self.current_sale = None
                self.clear_form()
                self.sale_saved.emit()
            except Exception as e:
                QMessageBox.critical(self, 'Errore', f'Errore durante l\'eliminazione:\n{str(e)}')
    
    def refresh_suppliers(self):
        """Aggiorna la lista fornitori (chiamato quando si aggiunge un fornitore)"""
        # Ricalcola i totali per aggiornare i pagamenti fornitori
        self.calculate_totals()
