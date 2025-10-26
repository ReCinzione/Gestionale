#!/usr/bin/env python3
"""
Gestionale Negozio - Applicazione Desktop
Entry point principale dell'applicazione.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Aggiungi il percorso corrente al PYTHONPATH per gli import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"Errore import: {e}")
    print("Assicurati di aver installato tutte le dipendenze con:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Funzione principale"""
    # Abilita DPI scaling per schermi ad alta risoluzione (PRIMA di creare QApplication)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Crea l'applicazione Qt
    app = QApplication(sys.argv)
    
    # Configura l'applicazione
    app.setApplicationName('Gestionale Negozio')
    app.setApplicationVersion('1.0')
    app.setOrganizationName('Gestionale')
    
    try:
        # Crea e mostra la finestra principale
        window = MainWindow()
        window.show()
        
        # Messaggio di benvenuto (solo al primo avvio)
        if not os.path.exists('gestionale.db'):
            QMessageBox.information(
                window,
                'Benvenuto!',
                '<h3>Benvenuto nel Gestionale Negozio!</h3>'
                '<p>Questa è la prima esecuzione dell\'applicazione.</p>'
                '<p>Il database è stato creato automaticamente con i fornitori di default:</p>'
                '<ul><li>AIA</li><li>GranTerre</li><li>MIA</li></ul>'
                '<p><b>Suggerimenti per iniziare:</b></p>'
                '<ul>'
                '<li>📊 Vai al tab "Vendite Giornaliere" per inserire i dati di oggi</li>'
                '<li>🏭 Usa il tab "Fornitori e Spese" per aggiungere nuovi fornitori</li>'
                '<li>📈 Controlla i "Report e Filtri" per analizzare i dati</li>'
                '</ul>'
            )
        
        # Avvia il loop degli eventi
        sys.exit(app.exec_())
        
    except Exception as e:
        # Gestione errori critici
        error_msg = f"Errore critico durante l'avvio:\n{str(e)}"
        print(error_msg)
        
        # Prova a mostrare un messaggio di errore grafico
        try:
            QMessageBox.critical(None, 'Errore Critico', error_msg)
        except:
            pass
        
        sys.exit(1)


if __name__ == '__main__':
    main()
