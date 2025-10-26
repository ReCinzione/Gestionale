"""
Tab per report e filtri avanzati.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit, QComboBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QAbstractItemView, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta


class ReportsTab(QWidget):
    """Tab per report e analisi dati"""
    
    def __init__(self, sales_repo, purchases_repo, suppliers_repo):
        super().__init__()
        
        self.sales_repo = sales_repo
        self.purchases_repo = purchases_repo
        self.suppliers_repo = suppliers_repo
        
        self.init_ui()
        self.refresh_data()
    
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
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Filtri periodo
        filters_group = QGroupBox('🔍 FILTRI PERIODO')
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)
        
        # Data inizio
        filters_layout.addWidget(QLabel('Dal:'))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setDisplayFormat('dd/MM/yyyy')
        self.start_date_edit.setMinimumHeight(35)
        filters_layout.addWidget(self.start_date_edit)
        
        # Data fine
        filters_layout.addWidget(QLabel('Al:'))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDisplayFormat('dd/MM/yyyy')
        self.end_date_edit.setMinimumHeight(35)
        filters_layout.addWidget(self.end_date_edit)
        
        # Pulsanti periodo predefinito
        self.btn_today = QPushButton('Oggi')
        self.btn_today.clicked.connect(self.filter_today)
        self.btn_today.setMinimumSize(80, 35)
        filters_layout.addWidget(self.btn_today)
        
        self.btn_week = QPushButton('Settimana')
        self.btn_week.clicked.connect(self.filter_week)
        self.btn_week.setMinimumSize(80, 35)
        filters_layout.addWidget(self.btn_week)
        
        self.btn_month = QPushButton('Mese')
        self.btn_month.clicked.connect(self.filter_month)
        self.btn_month.setMinimumSize(80, 35)
        filters_layout.addWidget(self.btn_month)
        
        self.btn_apply = QPushButton('🔍 Applica Filtro')
        self.btn_apply.setProperty('class', 'primary')
        self.btn_apply.setMinimumSize(120, 35)
        self.btn_apply.clicked.connect(self.apply_filter)
        filters_layout.addWidget(self.btn_apply)
        
        filters_layout.addStretch()
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Tab per diversi tipi di report
        self.reports_tabs = QTabWidget()
        
        # Tab Riepilogo Generale
        self.summary_tab = self.create_summary_tab()
        self.reports_tabs.addTab(self.summary_tab, '📊 Riepilogo Generale')
        
        # Tab Vendite Dettagliate
        self.sales_tab = self.create_sales_tab()
        self.reports_tabs.addTab(self.sales_tab, '💰 Vendite Dettagliate')
        
        # Tab Spese per Fornitore
        self.expenses_tab = self.create_expenses_tab()
        self.reports_tabs.addTab(self.expenses_tab, '🏭 Spese per Fornitore')
        
        layout.addWidget(self.reports_tabs)
        
        self.setLayout(layout)
    
    def create_summary_tab(self):
        """Crea il tab riepilogo generale"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Riepilogo numerico
        summary_group = QGroupBox('📈 RIEPILOGO PERIODO')
        summary_group.setStyleSheet('QGroupBox { font-weight: bold; background-color: #F0FFF0; }')
        summary_layout = QFormLayout()
        
        # Font per i totali
        total_font = QFont()
        total_font.setBold(True)
        total_font.setPointSize(11)
        
        # Vendite
        self.lbl_total_sales = QLabel('€ 0,00')
        self.lbl_total_sales.setFont(total_font)
        self.lbl_total_sales.setStyleSheet('background-color: #90EE90; padding: 8px;')
        summary_layout.addRow('💰 Totale Incassi:', self.lbl_total_sales)
        
        self.lbl_total_cash_sales = QLabel('€ 0,00')
        self.lbl_total_cash_sales.setStyleSheet('background-color: #E0FFE0; padding: 5px;')
        summary_layout.addRow('  - Incassi Contanti:', self.lbl_total_cash_sales)
        
        self.lbl_total_bank_sales = QLabel('€ 0,00')
        self.lbl_total_bank_sales.setStyleSheet('background-color: #E0FFE0; padding: 5px;')
        summary_layout.addRow('  - Incassi Bancari:', self.lbl_total_bank_sales)
        
        # Spese
        self.lbl_total_expenses = QLabel('€ 0,00')
        self.lbl_total_expenses.setFont(total_font)
        self.lbl_total_expenses.setStyleSheet('background-color: #FFB6C1; padding: 8px;')
        summary_layout.addRow('💸 Totale Spese:', self.lbl_total_expenses)
        
        self.lbl_total_cash_expenses = QLabel('€ 0,00')
        self.lbl_total_cash_expenses.setStyleSheet('background-color: #FFE0E0; padding: 5px;')
        summary_layout.addRow('  - Spese Contanti:', self.lbl_total_cash_expenses)
        
        self.lbl_total_bank_expenses = QLabel('€ 0,00')
        self.lbl_total_bank_expenses.setStyleSheet('background-color: #FFE0E0; padding: 5px;')
        summary_layout.addRow('  - Spese Bancarie:', self.lbl_total_bank_expenses)
        
        # Profitto
        self.lbl_net_profit = QLabel('€ 0,00')
        self.lbl_net_profit.setFont(total_font)
        self.lbl_net_profit.setStyleSheet('background-color: #FFFF99; padding: 10px; font-size: 14pt;')
        summary_layout.addRow('📈 PROFITTO NETTO:', self.lbl_net_profit)
        
        # Statistiche
        summary_layout.addRow('', QLabel(''))  # Spazio
        
        self.lbl_days_count = QLabel('0')
        summary_layout.addRow('📅 Giorni con Vendite:', self.lbl_days_count)
        
        self.lbl_avg_daily = QLabel('€ 0,00')
        summary_layout.addRow('📊 Media Giornaliera:', self.lbl_avg_daily)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_sales_tab(self):
        """Crea il tab vendite dettagliate"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tabella vendite
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(8)
        self.sales_table.setHorizontalHeaderLabels([
            'Data', 'Incasso Contante', 'Incasso Bancario', 'Commissioni',
            'Corrispettivo', 'Spese Giorno', 'Ricavo Netto', 'Note'
        ])
        
        # Configura tabella
        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Contante
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Bancario
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Commissioni
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Corrispettivo
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Spese
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Ricavo
        header.setSectionResizeMode(7, QHeaderView.Stretch)           # Note
        
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setSortingEnabled(True)
        
        layout.addWidget(QLabel('<b>📋 DETTAGLIO VENDITE</b>'))
        layout.addWidget(self.sales_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_expenses_tab(self):
        """Crea il tab spese per fornitore"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tabella spese per fornitore
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setHorizontalHeaderLabels([
            'Fornitore', 'Pagamenti Contanti', 'Pagamenti Bancari', 'Totale'
        ])
        
        # Configura tabella
        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Fornitore
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Contanti
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Bancari
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Totale
        
        self.expenses_table.setAlternatingRowColors(True)
        self.expenses_table.setSortingEnabled(True)
        
        layout.addWidget(QLabel('<b>📋 SPESE PER FORNITORE</b>'))
        layout.addWidget(self.expenses_table)
        
        widget.setLayout(layout)
        return widget
    
    def filter_today(self):
        """Filtra per oggi"""
        today = QDate.currentDate()
        self.start_date_edit.setDate(today)
        self.end_date_edit.setDate(today)
        self.apply_filter()
    
    def filter_week(self):
        """Filtra per questa settimana"""
        today = QDate.currentDate()
        start_week = today.addDays(-today.dayOfWeek() + 1)  # Lunedì
        self.start_date_edit.setDate(start_week)
        self.end_date_edit.setDate(today)
        self.apply_filter()
    
    def filter_month(self):
        """Filtra per questo mese"""
        today = QDate.currentDate()
        start_month = QDate(today.year(), today.month(), 1)
        self.start_date_edit.setDate(start_month)
        self.end_date_edit.setDate(today)
        self.apply_filter()
    
    def apply_filter(self):
        """Applica il filtro selezionato"""
        start_date = self.start_date_edit.date().toString('yyyy-MM-dd')
        end_date = self.end_date_edit.date().toString('yyyy-MM-dd')
        
        # Carica dati filtrati
        self.load_filtered_data(start_date, end_date)
    
    def load_filtered_data(self, start_date, end_date):
        """Carica i dati per il periodo specificato"""
        # Carica vendite
        sales = self.sales_repo.get_by_date_range(start_date, end_date)
        
        # Carica spese
        purchases = self.purchases_repo.get_by_date_range(start_date, end_date)
        
        # Aggiorna riepilogo
        self.update_summary(sales, purchases)
        
        # Aggiorna tabelle
        self.update_sales_table(sales, purchases)
        self.update_expenses_table(purchases)
    
    def update_summary(self, sales, purchases):
        """Aggiorna il riepilogo generale"""
        from services.calculator import SalesCalculator
        
        # Calcola totali vendite
        total_sales = 0
        total_cash_sales = 0
        total_bank_sales = 0
        
        for sale_data in sales:
            from models.sale import Sale
            sale = Sale.from_dict(sale_data)
            
            cash_total = SalesCalculator.calculate_cash_total(sale)
            bank_total = SalesCalculator.calculate_bank_total(sale)
            takings = cash_total + bank_total
            
            total_sales += takings
            total_cash_sales += cash_total
            total_bank_sales += bank_total
        
        # Calcola totali spese
        total_expenses = 0
        total_cash_expenses = 0
        total_bank_expenses = 0
        
        for purchase in purchases:
            cash = purchase.get('cash_payment', 0)
            bank = purchase.get('bank_payment', 0)
            
            total_expenses += cash + bank
            total_cash_expenses += cash
            total_bank_expenses += bank
        
        # Calcola profitto netto
        net_profit = total_sales - total_expenses
        
        # Statistiche
        days_count = len(sales)
        avg_daily = total_sales / days_count if days_count > 0 else 0
        
        # Aggiorna label
        self.lbl_total_sales.setText(self.format_currency(total_sales))
        self.lbl_total_cash_sales.setText(self.format_currency(total_cash_sales))
        self.lbl_total_bank_sales.setText(self.format_currency(total_bank_sales))
        
        self.lbl_total_expenses.setText(self.format_currency(total_expenses))
        self.lbl_total_cash_expenses.setText(self.format_currency(total_cash_expenses))
        self.lbl_total_bank_expenses.setText(self.format_currency(total_bank_expenses))
        
        self.lbl_net_profit.setText(self.format_currency(net_profit))
        
        self.lbl_days_count.setText(str(days_count))
        self.lbl_avg_daily.setText(self.format_currency(avg_daily))
        
        # Colora il profitto
        if net_profit >= 0:
            self.lbl_net_profit.setStyleSheet('background-color: #90EE90; padding: 10px; font-size: 14pt; font-weight: bold;')
        else:
            self.lbl_net_profit.setStyleSheet('background-color: #FFB6C1; padding: 10px; font-size: 14pt; font-weight: bold;')
    
    def update_sales_table(self, sales, purchases):
        """Aggiorna la tabella delle vendite"""
        from services.calculator import SalesCalculator
        from models.sale import Sale
        
        self.sales_table.setRowCount(len(sales))
        
        for row, sale_data in enumerate(sales):
            sale = Sale.from_dict(sale_data)
            
            # Calcola valori
            cash_total = SalesCalculator.calculate_cash_total(sale)
            bank_total = SalesCalculator.calculate_bank_total(sale)
            
            card_fees = SalesCalculator.calculate_card_fees(
                sale.card_gross, sale.card_percent_fee, sale.card_fixed_fee
            )
            satispay_fees = SalesCalculator.calculate_card_fees(
                sale.satispay_gross, sale.satispay_percent_fee, sale.satispay_fixed_fee
            )
            total_fees = card_fees + satispay_fees
            
            takings = cash_total + bank_total
            
            # Spese del giorno
            day_purchases = [p for p in purchases if p['date'] == sale.date]
            day_expenses = sum(p.get('cash_payment', 0) + p.get('bank_payment', 0) for p in day_purchases)
            
            net_profit = takings - day_expenses
            
            # Popola riga
            self.sales_table.setItem(row, 0, QTableWidgetItem(sale.date))
            self.sales_table.setItem(row, 1, QTableWidgetItem(self.format_currency(cash_total)))
            self.sales_table.setItem(row, 2, QTableWidgetItem(self.format_currency(bank_total)))
            self.sales_table.setItem(row, 3, QTableWidgetItem(self.format_currency(total_fees)))
            self.sales_table.setItem(row, 4, QTableWidgetItem(self.format_currency(takings)))
            self.sales_table.setItem(row, 5, QTableWidgetItem(self.format_currency(day_expenses)))
            self.sales_table.setItem(row, 6, QTableWidgetItem(self.format_currency(net_profit)))
            self.sales_table.setItem(row, 7, QTableWidgetItem(sale.notes))
            
            # Allinea numeri a destra
            for col in range(1, 7):
                self.sales_table.item(row, col).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    
    def update_expenses_table(self, purchases):
        """Aggiorna la tabella spese per fornitore"""
        # Raggruppa per fornitore
        supplier_totals = {}
        
        for purchase in purchases:
            supplier_name = purchase.get('supplier_name', 'Sconosciuto')
            cash = purchase.get('cash_payment', 0)
            bank = purchase.get('bank_payment', 0)
            
            if supplier_name not in supplier_totals:
                supplier_totals[supplier_name] = {'cash': 0, 'bank': 0}
            
            supplier_totals[supplier_name]['cash'] += cash
            supplier_totals[supplier_name]['bank'] += bank
        
        # Popola tabella
        self.expenses_table.setRowCount(len(supplier_totals))
        
        for row, (supplier, totals) in enumerate(supplier_totals.items()):
            total = totals['cash'] + totals['bank']
            
            self.expenses_table.setItem(row, 0, QTableWidgetItem(supplier))
            self.expenses_table.setItem(row, 1, QTableWidgetItem(self.format_currency(totals['cash'])))
            self.expenses_table.setItem(row, 2, QTableWidgetItem(self.format_currency(totals['bank'])))
            self.expenses_table.setItem(row, 3, QTableWidgetItem(self.format_currency(total)))
            
            # Allinea numeri a destra
            for col in range(1, 4):
                self.expenses_table.item(row, col).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    
    def format_currency(self, value):
        """Formatta un valore come valuta"""
        return f"€ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def refresh_data(self):
        """Aggiorna tutti i dati (chiamato dall'esterno)"""
        self.apply_filter()
