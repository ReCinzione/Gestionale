#!/usr/bin/env python
"""
Script di test per verificare che l'applicazione funzioni correttamente.
"""

import sys
import os

# Aggiungi il percorso corrente al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa tutti gli import necessari"""
    print("🔍 Testando import...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 importato correttamente")
    except ImportError as e:
        print(f"❌ Errore PyQt5: {e}")
        return False
    
    try:
        from database.schema import Database
        print("✅ Database schema importato")
    except ImportError as e:
        print(f"❌ Errore database: {e}")
        return False
    
    try:
        from models.sale import Sale
        from models.supplier import Supplier
        from models.purchase import Purchase
        print("✅ Modelli importati")
    except ImportError as e:
        print(f"❌ Errore modelli: {e}")
        return False
    
    try:
        from services.calculator import SalesCalculator
        print("✅ Servizi importati")
    except ImportError as e:
        print(f"❌ Errore servizi: {e}")
        return False
    
    return True

def test_database():
    """Testa la creazione del database"""
    print("\n🗄️ Testando database...")
    
    try:
        from database.schema import Database
        from database.repository import SalesRepository, SuppliersRepository
        
        # Crea database di test
        db = Database('test_gestionale.db')
        
        # Testa repository
        suppliers_repo = SuppliersRepository(db.connection)
        sales_repo = SalesRepository(db.connection)
        
        # Verifica fornitori di default
        suppliers = suppliers_repo.get_all_active()
        print(f"✅ Database creato con {len(suppliers)} fornitori di default")
        
        # Pulisci
        db.close()
        if os.path.exists('test_gestionale.db'):
            os.remove('test_gestionale.db')
        
        return True
        
    except Exception as e:
        print(f"❌ Errore database: {e}")
        return False

def test_calculations():
    """Testa i calcoli delle vendite"""
    print("\n🧮 Testando calcoli...")
    
    try:
        from models.sale import Sale
        from services.calculator import SalesCalculator
        
        # Crea una vendita di test
        sale = Sale(
            date='2024-01-01',
            cash_income=100.0,
            coin_income=50.0,
            card_gross=200.0,
            card_percent_fee=1.95,
            card_fixed_fee=0.15,
            satispay_gross=100.0,
            satispay_percent_fee=1.0,
            satispay_fixed_fee=0.0
        )
        
        # Testa calcoli
        calc = SalesCalculator()
        cash_total = calc.calculate_cash_total(sale)
        bank_total = calc.calculate_bank_total(sale)
        takings = calc.calculate_takings(sale)
        
        print(f"✅ Incasso contante: {calc.format_currency(cash_total)}")
        print(f"✅ Incasso bancario: {calc.format_currency(bank_total)}")
        print(f"✅ Corrispettivo: {calc.format_currency(takings)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore calcoli: {e}")
        return False

def main():
    """Funzione principale di test"""
    print("🚀 Test Gestionale Negozio")
    print("=" * 40)
    
    # Esegui tutti i test
    tests = [
        test_imports,
        test_database,
        test_calculations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Risultati: {passed}/{total} test superati")
    
    if passed == total:
        print("🎉 Tutti i test sono passati! L'applicazione è pronta.")
        print("\n💡 Per avviare l'applicazione esegui:")
        print("   python main.py")
    else:
        print("⚠️ Alcuni test sono falliti. Controlla gli errori sopra.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
