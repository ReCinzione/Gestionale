"""
Model per le fatture.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Invoice:
    """Rappresenta una fattura"""
    
    date: str
    supplier_id: Optional[int] = None
    invoice_number: str = ''
    total_amount: float = 0.0
    file_path: str = ''
    ocr_text: str = ''
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
            'invoice_number': self.invoice_number,
            'total_amount': self.total_amount,
            'file_path': self.file_path,
            'ocr_text': self.ocr_text,
            'notes': self.notes
        }
        
        if self.id is not None:
            data['id'] = self.id
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        """Crea un'istanza Invoice da un dizionario"""
        return cls(
            id=data.get('id'),
            date=data.get('date'),
            supplier_id=data.get('supplier_id'),
            supplier_name=data.get('supplier_name'),
            invoice_number=data.get('invoice_number', ''),
            total_amount=data.get('total_amount', 0.0),
            file_path=data.get('file_path', ''),
            ocr_text=data.get('ocr_text', ''),
            notes=data.get('notes', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
