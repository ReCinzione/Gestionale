"""
Model per i fornitori.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Supplier:
    """Rappresenta un fornitore"""
    
    name: str
    active: int = 1
    notes: str = ''
    id: Optional[int] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte il model in dizionario per il database"""
        data = {
            'name': self.name,
            'active': self.active,
            'notes': self.notes
        }
        
        if self.id is not None:
            data['id'] = self.id
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Supplier':
        """Crea un'istanza Supplier da un dizionario"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            active=data.get('active', 1),
            notes=data.get('notes', ''),
            created_at=data.get('created_at')
        )
