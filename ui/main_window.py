"""
Finestra principale dell'applicazione.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QStatusBar, QMessageBox, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from database.schema import Database
from database.repository import (
    SalesRepository, SuppliersRepository,
    PurchasesRepository, InvoicesRepository
)
from ui.sales_tab import SalesTab
from ui.suppliers_tab import SuppliersTab
from ui.reports_tab import ReportsTab
from ui.invoices_tab import InvoicesTab


class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione gestionale"""
    
    def __init__(self):
        super().__init__()
        
        # Inizializza database
        self.db = Database()
        
        # Inizializza repositories
        self.sales_repo = SalesRepository(self.db.connection)
        self.suppliers_repo = SuppliersRepository(self.db.connection)
        self.purchases_repo = PurchasesRepository(self.db.connection)
        self.invoices_repo = InvoicesRepository(self.db.connection)
        
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle('Gestionale Negozio')
        self.setGeometry(100, 100, 1400, 900)
        
        # Applica stile moderno all'applicazione
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            
            QTabWidget::pane {
                border: 2px solid #e0e0e0;
                background-color: white;
                border-radius: 8px;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
            }
            
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #555555;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                min-width: 150px;
            }
            
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
                font-weight: 600;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #d0d0d0;
            }
            
            QStatusBar {
                background-color: #2196F3;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            
            QMenuBar {
                background-color: #ffffff;
                color: #333333;
                border-bottom: 1px solid #e0e0e0;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        # Crea il widget centrale con tab
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Crea i tab
        self.sales_tab = SalesTab(
            self.sales_repo,
            self.purchases_repo,
            self.suppliers_repo
        )
        self.suppliers_tab = SuppliersTab(
            self.suppliers_repo,
            self.purchases_repo
        )
        self.reports_tab = ReportsTab(
            self.sales_repo,
            self.purchases_repo,
            self.suppliers_repo
        )
        self.invoices_tab = InvoicesTab(
            self.invoices_repo,
            self.suppliers_repo
        )
        
        # Aggiungi i tab
        self.tabs.addTab(self.sales_tab, '📊 Vendite Giornaliere')
        self.tabs.addTab(self.suppliers_tab, '🏭 Fornitori e Spese')
        self.tabs.addTab(self.reports_tab, '📈 Report e Filtri')
        self.tabs.addTab(self.invoices_tab, '📄 Fatture')
        
        # Crea la barra di stato
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Pronto')
        
        # Crea menu
        self.create_menu()
        
        # Connetti segnali
        self.connect_signals()
    
    def create_menu(self):
        """Crea la barra dei menu"""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('&File')
        
        # Azione Import CSV
        import_action = QAction('📥 Importa CSV...', self)
        import_action.setShortcut('Ctrl+I')
        import_action.triggered.connect(self.import_csv)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Azione Esci
        exit_action = QAction('🚪 Esci', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Strumenti
        tools_menu = menubar.addMenu('&Strumenti')
        
        # Azione Backup
        backup_action = QAction('💾 Backup Database...', self)
        backup_action.triggered.connect(self.backup_database)
        tools_menu.addAction(backup_action)
        
        # Menu Aiuto
        help_menu = menubar.addMenu('&Aiuto')
        
        about_action = QAction('ℹ️ Info', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """Connette i segnali tra i vari componenti"""
        # Quando si aggiunge un fornitore, aggiorna la lista nel tab vendite
        self.suppliers_tab.supplier_added.connect(self.sales_tab.refresh_suppliers)
        
        # Quando si salvano vendite, aggiorna i report
        self.sales_tab.sale_saved.connect(self.reports_tab.refresh_data)
        
        # Quando si salvano acquisti, aggiorna i report
        self.suppliers_tab.purchase_saved.connect(self.reports_tab.refresh_data)
    
    def import_csv(self):
        """Apre il dialogo di importazione CSV"""
        from services.csv_importer import CSVImportDialog
        
        dialog = CSVImportDialog(
            self,
            self.sales_repo,
            self.suppliers_repo,
            self.purchases_repo
        )
        
        if dialog.exec_():
            self.statusBar.showMessage('Importazione completata con successo', 3000)
            # Aggiorna tutti i tab
            self.sales_tab.load_today_sale()
            self.suppliers_tab.refresh_purchases()
            self.reports_tab.refresh_data()
    
    def backup_database(self):
        """Crea un backup del database"""
        from PyQt5.QtWidgets import QFileDialog
        import shutil
        from datetime import datetime
        
        # Suggerisci nome file con data
        default_name = f"gestionale_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Salva Backup Database',
            default_name,
            'Database SQLite (*.db)'
        )
        
        if file_path:
            try:
                shutil.copy2(self.db.db_path, file_path)
                QMessageBox.information(
                    self,
                    'Backup Completato',
                    f'Backup salvato con successo in:\n{file_path}'
                )
                self.statusBar.showMessage('Backup completato', 3000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Errore Backup',
                    f'Errore durante il backup:\n{str(e)}'
                )
    
    def show_about(self):
        """Mostra la finestra informazioni"""
        QMessageBox.about(
            self,
            'Info - Gestionale Negozio',
            '<h2>Gestionale Negozio</h2>'
            '<p>Versione 1.0</p>'
            '<p>Applicazione per la gestione di vendite, fornitori e fatture.</p>'
            '<p><b>Funzionalità:</b></p>'
            '<ul>'
            '<li>Gestione vendite giornaliere</li>'
            '<li>Gestione fornitori e spese</li>'
            '<li>Report e filtri avanzati</li>'
            '<li>Gestione fatture con OCR</li>'
            '<li>Importazione dati da CSV</li>'
            '</ul>'
            '<p>Sviluppato con Python e PyQt5</p>'
        )
    
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        reply = QMessageBox.question(
            self,
            'Conferma Uscita',
            'Sei sicuro di voler uscire?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Chiudi connessione database
            self.db.close()
            event.accept()
        else:
            event.ignore()
