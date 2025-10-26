"""
Schema database SQLite per il gestionale negozio.
Crea le tabelle e gli indici necessari.
"""

import sqlite3
import os
from datetime import datetime


class Database:
    """Gestione connessione e schema database SQLite"""
    
    def __init__(self, db_path='gestionale.db'):
        """
        Inizializza la connessione al database.
        
        Args:
            db_path: Percorso del file database SQLite
        """
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Crea la connessione al database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Permette accesso per nome colonna
        
    def create_tables(self):
        """Crea tutte le tabelle e gli indici se non esistono"""
        cursor = self.connection.cursor()
        
        # Tabella vendite giornaliere
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                start_capital REAL DEFAULT 0,
                cash_income REAL DEFAULT 0,
                coin_income REAL DEFAULT 0,
                card_gross REAL DEFAULT 0,
                card_percent_fee REAL DEFAULT 1.95,
                card_fixed_fee REAL DEFAULT 0.15,
                satispay_gross REAL DEFAULT 0,
                satispay_percent_fee REAL DEFAULT 1.0,
                satispay_fixed_fee REAL DEFAULT 0.0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indice sulla data per le vendite
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_date 
            ON sales(date DESC)
        """)
        
        # Tabella fornitori
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                active INTEGER DEFAULT 1,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indice sul nome fornitore
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_suppliers_name 
            ON suppliers(name)
        """)
        
        # Tabella acquisti/spese
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                supplier_id INTEGER NOT NULL,
                description TEXT,
                cash_payment REAL DEFAULT 0,
                bank_payment REAL DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)
        
        # Indici per acquisti
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_purchases_date 
            ON purchases(date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_purchases_supplier 
            ON purchases(supplier_id)
        """)
        
        # Tabella fatture
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                supplier_id INTEGER,
                invoice_number TEXT,
                total_amount REAL DEFAULT 0,
                file_path TEXT,
                ocr_text TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)
        
        # Indici per fatture
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_date 
            ON invoices(date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_supplier 
            ON invoices(supplier_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_number 
            ON invoices(invoice_number)
        """)
        
        self.connection.commit()
        
        # Inserisci fornitori di default se la tabella è vuota
        self._insert_default_suppliers()
    
    def _insert_default_suppliers(self):
        """Inserisce i fornitori di default se non esistono"""
        cursor = self.connection.cursor()
        
        # Controlla se ci sono già fornitori
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        count = cursor.fetchone()[0]
        
        if count == 0:
            default_suppliers = ['AIA', 'GranTerre', 'MIA']
            for supplier in default_suppliers:
                cursor.execute(
                    "INSERT INTO suppliers (name, active) VALUES (?, 1)",
                    (supplier,)
                )
            self.connection.commit()
    
    def close(self):
        """Chiude la connessione al database"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
