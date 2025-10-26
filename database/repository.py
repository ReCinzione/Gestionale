"""
Repository pattern per accesso ai dati.
Fornisce metodi CRUD per tutte le entità del database.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import sqlite3


class BaseRepository:
    """Classe base per i repository"""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def _dict_from_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Converte una Row in dizionario"""
        if row is None:
            return None
        return {key: row[key] for key in row.keys()}


class SalesRepository(BaseRepository):
    """Repository per la gestione delle vendite"""
    
    def create(self, sale_data: Dict[str, Any]) -> int:
        """
        Crea una nuova vendita.
        
        Args:
            sale_data: Dizionario con i dati della vendita
            
        Returns:
            ID della vendita creata
        """
        cursor = self.connection.cursor()
        
        fields = ', '.join(sale_data.keys())
        placeholders = ', '.join(['?' for _ in sale_data])
        
        query = f"INSERT INTO sales ({fields}) VALUES ({placeholders})"
        cursor.execute(query, list(sale_data.values()))
        self.connection.commit()
        
        return cursor.lastrowid
    
    def get_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """
        Recupera una vendita per data.
        
        Args:
            date: Data in formato YYYY-MM-DD
            
        Returns:
            Dizionario con i dati della vendita o None
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sales WHERE date = ?", (date,))
        row = cursor.fetchone()
        return self._dict_from_row(row)
    
    def get_by_id(self, sale_id: int) -> Optional[Dict[str, Any]]:
        """Recupera una vendita per ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sales WHERE id = ?", (sale_id,))
        row = cursor.fetchone()
        return self._dict_from_row(row)
    
    def update(self, date: str, sale_data: Dict[str, Any]) -> bool:
        """
        Aggiorna una vendita esistente.
        
        Args:
            date: Data della vendita da aggiornare
            sale_data: Nuovi dati
            
        Returns:
            True se aggiornata, False altrimenti
        """
        cursor = self.connection.cursor()
        
        # Aggiungi timestamp di aggiornamento
        sale_data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{key} = ?" for key in sale_data.keys()])
        query = f"UPDATE sales SET {set_clause} WHERE date = ?"
        
        values = list(sale_data.values()) + [date]
        cursor.execute(query, values)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def delete(self, date: str) -> bool:
        """Elimina una vendita per data"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM sales WHERE date = ?", (date,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Recupera tutte le vendite con paginazione"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM sales ORDER BY date DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Recupera vendite in un intervallo di date.
        
        Args:
            start_date: Data inizio (YYYY-MM-DD)
            end_date: Data fine (YYYY-MM-DD)
            
        Returns:
            Lista di vendite
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM sales WHERE date BETWEEN ? AND ? ORDER BY date DESC",
            (start_date, end_date)
        )
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Cerca vendite per data o note"""
        cursor = self.connection.cursor()
        search_pattern = f"%{query}%"
        cursor.execute(
            "SELECT * FROM sales WHERE date LIKE ? OR notes LIKE ? ORDER BY date DESC",
            (search_pattern, search_pattern)
        )
        return [self._dict_from_row(row) for row in cursor.fetchall()]


class SuppliersRepository(BaseRepository):
    """Repository per la gestione dei fornitori"""
    
    def create(self, name: str, notes: str = '') -> int:
        """Crea un nuovo fornitore"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO suppliers (name, notes) VALUES (?, ?)",
            (name, notes)
        )
        self.connection.commit()
        return cursor.lastrowid
    
    def get_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """Recupera un fornitore per ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        return self._dict_from_row(row)
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Recupera un fornitore per nome"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE name = ?", (name,))
        row = cursor.fetchone()
        return self._dict_from_row(row)
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        """Recupera tutti i fornitori attivi"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM suppliers WHERE active = 1 ORDER BY name"
        )
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Recupera tutti i fornitori"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM suppliers ORDER BY name")
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def update(self, supplier_id: int, name: str, active: int = 1, notes: str = '') -> bool:
        """Aggiorna un fornitore"""
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE suppliers SET name = ?, active = ?, notes = ? WHERE id = ?",
            (name, active, notes, supplier_id)
        )
        self.connection.commit()
        return cursor.rowcount > 0
    
    def delete(self, supplier_id: int) -> bool:
        """Elimina un fornitore (soft delete - lo disattiva)"""
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE suppliers SET active = 0 WHERE id = ?",
            (supplier_id,)
        )
        self.connection.commit()
        return cursor.rowcount > 0
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Cerca fornitori per nome"""
        cursor = self.connection.cursor()
        search_pattern = f"%{query}%"
        cursor.execute(
            "SELECT * FROM suppliers WHERE name LIKE ? ORDER BY name",
            (search_pattern,)
        )
        return [self._dict_from_row(row) for row in cursor.fetchall()]


class PurchasesRepository(BaseRepository):
    """Repository per la gestione degli acquisti"""
    
    def create(self, purchase_data: Dict[str, Any]) -> int:
        """Crea un nuovo acquisto"""
        cursor = self.connection.cursor()
        
        fields = ', '.join(purchase_data.keys())
        placeholders = ', '.join(['?' for _ in purchase_data])
        
        query = f"INSERT INTO purchases ({fields}) VALUES ({placeholders})"
        cursor.execute(query, list(purchase_data.values()))
        self.connection.commit()
        
        return cursor.lastrowid
    
    def get_by_id(self, purchase_id: int) -> Optional[Dict[str, Any]]:
        """Recupera un acquisto per ID"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT p.*, s.name as supplier_name 
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id = ?
        """, (purchase_id,))
        row = cursor.fetchone()
        return self._dict_from_row(row)
    
    def get_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Recupera tutti gli acquisti di una data"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT p.*, s.name as supplier_name 
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.date = ?
            ORDER BY p.created_at DESC
        """, (date,))
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Recupera acquisti in un intervallo di date"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT p.*, s.name as supplier_name 
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.date BETWEEN ? AND ?
            ORDER BY p.date DESC, p.created_at DESC
        """, (start_date, end_date))
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def get_by_supplier(self, supplier_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera acquisti per fornitore"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT p.*, s.name as supplier_name 
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.supplier_id = ?
            ORDER BY p.date DESC
            LIMIT ?
        """, (supplier_id, limit))
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def update(self, purchase_id: int, purchase_data: Dict[str, Any]) -> bool:
        """Aggiorna un acquisto"""
        cursor = self.connection.cursor()
        
        purchase_data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{key} = ?" for key in purchase_data.keys()])
        query = f"UPDATE purchases SET {set_clause} WHERE id = ?"
        
        values = list(purchase_data.values()) + [purchase_id]
        cursor.execute(query, values)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def delete(self, purchase_id: int) -> bool:
        """Elimina un acquisto"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_totals_by_date_range(self, start_date: str, end_date: str) -> Dict[str, float]:
        """Calcola totali acquisti per intervallo di date"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                COALESCE(SUM(cash_payment), 0) as total_cash,
                COALESCE(SUM(bank_payment), 0) as total_bank,
                COALESCE(SUM(cash_payment + bank_payment), 0) as total
            FROM purchases
            WHERE date BETWEEN ? AND ?
        """, (start_date, end_date))
        row = cursor.fetchone()
        return self._dict_from_row(row)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Cerca acquisti per descrizione o fornitore"""
        cursor = self.connection.cursor()
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT p.*, s.name as supplier_name 
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.description LIKE ? OR s.name LIKE ? OR p.notes LIKE ?
            ORDER BY p.date DESC
        """, (search_pattern, search_pattern, search_pattern))
        return [self._dict_from_row(row) for row in cursor.fetchall()]


class InvoicesRepository(BaseRepository):
    """Repository per la gestione delle fatture"""
    
    def create(self, invoice_data: Dict[str, Any]) -> int:
        """Crea una nuova fattura"""
        cursor = self.connection.cursor()
        
        fields = ', '.join(invoice_data.keys())
        placeholders = ', '.join(['?' for _ in invoice_data])
        
        query = f"INSERT INTO invoices ({fields}) VALUES ({placeholders})"
        cursor.execute(query, list(invoice_data.values()))
        self.connection.commit()
        
        return cursor.lastrowid
    
    def get_by_id(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Recupera una fattura per ID"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT i.*, s.name as supplier_name 
            FROM invoices i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.id = ?
        """, (invoice_id,))
        row = cursor.fetchone()
        return self._dict_from_row(row)
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Recupera tutte le fatture con paginazione"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT i.*, s.name as supplier_name 
            FROM invoices i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY i.date DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Recupera fatture in un intervallo di date"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT i.*, s.name as supplier_name 
            FROM invoices i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.date BETWEEN ? AND ?
            ORDER BY i.date DESC
        """, (start_date, end_date))
        return [self._dict_from_row(row) for row in cursor.fetchall()]
    
    def update(self, invoice_id: int, invoice_data: Dict[str, Any]) -> bool:
        """Aggiorna una fattura"""
        cursor = self.connection.cursor()
        
        invoice_data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{key} = ?" for key in invoice_data.keys()])
        query = f"UPDATE invoices SET {set_clause} WHERE id = ?"
        
        values = list(invoice_data.values()) + [invoice_id]
        cursor.execute(query, values)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def delete(self, invoice_id: int) -> bool:
        """Elimina una fattura"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Cerca fatture per numero, fornitore o testo OCR"""
        cursor = self.connection.cursor()
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT i.*, s.name as supplier_name 
            FROM invoices i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.invoice_number LIKE ? OR s.name LIKE ? 
               OR i.ocr_text LIKE ? OR i.notes LIKE ?
            ORDER BY i.date DESC
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        return [self._dict_from_row(row) for row in cursor.fetchall()]
