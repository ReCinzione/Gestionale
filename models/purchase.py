"""
Model per gli acquisti/spese.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Purchase:
    """Rappresenta un acquisto o spesa"""
    
    date: str
    supplier_id: int
    description: str = ''
    cash_payment: float = 0.0
    bank_payment: float = 0.0
    notes: str = ''
    id: Optional[int] = None
    supplier_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte il model in dizionario per il database"""
        data = {
            'date': self.date,
            'supplier_id': self.supplier_id,
            'description': self.description,
            'cash_payment': self.cash_payment,
            'bank_payment': self.bank_payment,
            'notes': self.notes
        }
        
        if self.id is not None:
            data['id'] = self.id
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Purchase':
        """Crea un'istanza Purchase da un dizionario"""
        return cls(
            id=data.get('id'),
            date=data.get('date'),
            supplier_id=data.get('supplier_id'),
            supplier_name=data.get('supplier_name'),
            description=data.get('description', ''),
            cash_payment=data.get('cash_payment', 0.0),
            bank_payment=data.get('bank_payment', 0.0),
            notes=data.get('notes', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @property
    def total(self) -> float:
        """Calcola il totale dell'acquisto"""
        return self.cash_payment + self.bank_payment
