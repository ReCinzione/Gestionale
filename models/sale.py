"""
Model per le vendite giornaliere.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Sale:
    """Rappresenta una vendita giornaliera"""
    
    date: str
    start_capital: float = 0.0
    cash_income: float = 0.0
    coin_income: float = 0.0
    card_gross: float = 0.0
    card_percent_fee: float = 1.95
    card_fixed_fee: float = 0.15
    satispay_gross: float = 0.0
    satispay_percent_fee: float = 1.0
    satispay_fixed_fee: float = 0.0
    notes: str = ''
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte il model in dizionario per il database"""
        data = {
            'date': self.date,
            'start_capital': self.start_capital,
            'cash_income': self.cash_income,
            'coin_income': self.coin_income,
            'card_gross': self.card_gross,
            'card_percent_fee': self.card_percent_fee,
            'card_fixed_fee': self.card_fixed_fee,
            'satispay_gross': self.satispay_gross,
            'satispay_percent_fee': self.satispay_percent_fee,
            'satispay_fixed_fee': self.satispay_fixed_fee,
            'notes': self.notes
        }
        
        if self.id is not None:
            data['id'] = self.id
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Sale':
        """Crea un'istanza Sale da un dizionario"""
        return cls(
            id=data.get('id'),
            date=data.get('date'),
            start_capital=data.get('start_capital', 0.0),
            cash_income=data.get('cash_income', 0.0),
            coin_income=data.get('coin_income', 0.0),
            card_gross=data.get('card_gross', 0.0),
            card_percent_fee=data.get('card_percent_fee', 1.95),
            card_fixed_fee=data.get('card_fixed_fee', 0.15),
            satispay_gross=data.get('satispay_gross', 0.0),
            satispay_percent_fee=data.get('satispay_percent_fee', 1.0),
            satispay_fixed_fee=data.get('satispay_fixed_fee', 0.0),
            notes=data.get('notes', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
