"""
Servizio per i calcoli delle vendite giornaliere.
Implementa la logica di business per i calcoli automatici.
"""

from typing import Dict, Any
from models.sale import Sale


class SalesCalculator:
    """Calcola i valori derivati per le vendite giornaliere"""
    
    @staticmethod
    def calculate_cash_total(sale: Sale) -> float:
        """
        Calcola l'incasso contante totale.
        
        Formula: Incasso Contante + Incasso Moneta
        """
        return sale.cash_income + sale.coin_income
    
    @staticmethod
    def calculate_card_fees(gross: float, percent_fee: float, fixed_fee: float) -> float:
        """
        Calcola le commissioni per transazioni con carta.
        
        Formula: (Lordo * Percentuale / 100) + Costo Fisso
        """
        return (gross * percent_fee / 100.0) + fixed_fee
    
    @staticmethod
    def calculate_card_net(sale: Sale) -> float:
        """
        Calcola l'incasso netto da transazioni Bancomat.
        
        Formula: Lordo - Commissioni
        """
        fees = SalesCalculator.calculate_card_fees(
            sale.card_gross,
            sale.card_percent_fee,
            sale.card_fixed_fee
        )
        return sale.card_gross - fees
    
    @staticmethod
    def calculate_satispay_net(sale: Sale) -> float:
        """
        Calcola l'incasso netto da transazioni Satispay.
        
        Formula: Lordo - Commissioni
        """
        fees = SalesCalculator.calculate_card_fees(
            sale.satispay_gross,
            sale.satispay_percent_fee,
            sale.satispay_fixed_fee
        )
        return sale.satispay_gross - fees
    
    @staticmethod
    def calculate_bank_total(sale: Sale) -> float:
        """
        Calcola l'incasso bancario totale.
        
        Formula: Netto Bancomat + Netto Satispay
        """
        card_net = SalesCalculator.calculate_card_net(sale)
        satispay_net = SalesCalculator.calculate_satispay_net(sale)
        return card_net + satispay_net
    
    @staticmethod
    def calculate_takings(sale: Sale) -> float:
        """
        Calcola il corrispettivo (incasso totale).
        
        Formula: Incasso Contante + Incasso Bancario
        """
        cash_total = SalesCalculator.calculate_cash_total(sale)
        bank_total = SalesCalculator.calculate_bank_total(sale)
        return cash_total + bank_total
    
    @staticmethod
    def calculate_daily_profit(sale: Sale, supplier_payments: float = 0.0) -> float:
        """
        Calcola il ricavo giornaliero.
        
        Formula: Corrispettivo - Pagamenti Fornitori
        
        Args:
            sale: Vendita giornaliera
            supplier_payments: Totale pagamenti fornitori del giorno
        """
        takings = SalesCalculator.calculate_takings(sale)
        return takings - supplier_payments
    
    @staticmethod
    def get_all_calculations(sale: Sale, supplier_payments: float = 0.0) -> Dict[str, float]:
        """
        Restituisce tutti i calcoli per una vendita.
        
        Returns:
            Dizionario con tutti i valori calcolati
        """
        cash_total = SalesCalculator.calculate_cash_total(sale)
        
        card_fees = SalesCalculator.calculate_card_fees(
            sale.card_gross,
            sale.card_percent_fee,
            sale.card_fixed_fee
        )
        card_net = sale.card_gross - card_fees
        
        satispay_fees = SalesCalculator.calculate_card_fees(
            sale.satispay_gross,
            sale.satispay_percent_fee,
            sale.satispay_fixed_fee
        )
        satispay_net = sale.satispay_gross - satispay_fees
        
        bank_total = card_net + satispay_net
        takings = cash_total + bank_total
        daily_profit = takings - supplier_payments
        
        return {
            'cash_total': cash_total,
            'card_fees': card_fees,
            'card_net': card_net,
            'satispay_fees': satispay_fees,
            'satispay_net': satispay_net,
            'bank_total': bank_total,
            'takings': takings,
            'supplier_payments': supplier_payments,
            'daily_profit': daily_profit
        }
    
    @staticmethod
    def format_currency(value: float) -> str:
        """
        Formatta un valore come valuta italiana.
        
        Args:
            value: Valore numerico
            
        Returns:
            Stringa formattata (es. "€ 1.234,56")
        """
        # Formatta con separatore migliaia e virgola decimale
        formatted = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"€ {formatted}"
