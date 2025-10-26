#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Tab - Pannello principale con statistiche e grafici
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import sqlite3


class StatCard(QFrame):
    """Widget card per visualizzare statistiche"""
    
    def __init__(self, title, value, subtitle="", icon="📊"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            StatCard {
                background-color: #424242;
                border: 1px solid #616161;
                border-radius: 12px;
                padding: 15px;
            }
            StatCard:hover {
                border: 2px solid #2196F3;
                background-color: #484848;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Header con icona e titolo
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #BBBBBB;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Valore principale
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #2196F3;
            margin: 5px 0;
        """)
        layout.addWidget(self.value_label)
        
        # Sottotitolo
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                font-size: 12px;
                color: #888888;
            """)
            layout.addWidget(subtitle_label)
        
        self.setLayout(layout)
        self.setMinimumSize(200, 120)
    
    def update_value(self, value):
        """Aggiorna il valore della card"""
        self.value_label.setText(str(value))


class ChartWidget(QWidget):
    """Widget per grafici matplotlib"""
    
    def __init__(self, title="Grafico"):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Titolo
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #FFFFFF;
            padding: 10px;
        """)
        layout.addWidget(title_label)
        
        # Figura matplotlib
        self.figure = Figure(figsize=(8, 4), facecolor='#424242')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #424242; border-radius: 8px;")
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_sales_trend(self, dates, values):
        """Grafico andamento vendite"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(dates, values, color='#2196F3', linewidth=2, marker='o', markersize=4)
        ax.fill_between(dates, values, alpha=0.3, color='#2196F3')
        
        ax.set_facecolor('#424242')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        ax.set_ylabel('Vendite (€)', color='white')
        ax.grid(True, alpha=0.3, color='white')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_expenses_pie(self, labels, values):
        """Grafico a torta delle spese"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0']
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                         colors=colors, startangle=90)
        
        for text in texts:
            text.set_color('white')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
        
        ax.set_facecolor('#424242')
        self.figure.tight_layout()
        self.canvas.draw()


class DashboardTab(QWidget):
    """Tab principale con dashboard e statistiche"""
    
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()
        
        # Timer per aggiornamento automatico
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Aggiorna ogni 30 secondi
        
        # Carica dati iniziali
        self.refresh_data()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # Header con titolo e pulsante refresh
        header_layout = QHBoxLayout()
        
        title_label = QLabel('📊 Dashboard Gestionale')
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #2196F3;
            padding: 10px 0;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton('🔄 Aggiorna')
        refresh_btn.setProperty('class', 'primary')
        refresh_btn.setMinimumSize(120, 35)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Scroll area per contenuto
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Cards statistiche
        self.create_stats_cards(content_layout)
        
        # Grafici
        self.create_charts(content_layout)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def create_stats_cards(self, layout):
        """Crea le card con statistiche"""
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        # Card vendite oggi
        self.sales_today_card = StatCard(
            "Vendite Oggi", "€ 0.00", "Rispetto a ieri", "💰"
        )
        cards_layout.addWidget(self.sales_today_card, 0, 0)
        
        # Card vendite mese
        self.sales_month_card = StatCard(
            "Vendite Mese", "€ 0.00", "Totale mensile", "📈"
        )
        cards_layout.addWidget(self.sales_month_card, 0, 1)
        
        # Card spese mese
        self.expenses_month_card = StatCard(
            "Spese Mese", "€ 0.00", "Totale mensile", "💸"
        )
        cards_layout.addWidget(self.expenses_month_card, 0, 2)
        
        # Card profitto
        self.profit_card = StatCard(
            "Profitto Mese", "€ 0.00", "Vendite - Spese", "🎯"
        )
        cards_layout.addWidget(self.profit_card, 0, 3)
        
        # Card fatture pending
        self.invoices_pending_card = StatCard(
            "Fatture da Processare", "0", "In attesa OCR", "📄"
        )
        cards_layout.addWidget(self.invoices_pending_card, 1, 0)
        
        # Card fornitori attivi
        self.suppliers_card = StatCard(
            "Fornitori Attivi", "0", "Questo mese", "🏪"
        )
        cards_layout.addWidget(self.suppliers_card, 1, 1)
        
        layout.addLayout(cards_layout)
    
    def create_charts(self, layout):
        """Crea i grafici"""
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Grafico vendite
        self.sales_chart = ChartWidget("📈 Andamento Vendite (Ultimi 7 giorni)")
        charts_layout.addWidget(self.sales_chart)
        
        # Grafico spese
        self.expenses_chart = ChartWidget("🥧 Distribuzione Spese (Questo Mese)")
        charts_layout.addWidget(self.expenses_chart)
        
        layout.addLayout(charts_layout)
    
    def refresh_data(self):
        """Aggiorna tutti i dati del dashboard"""
        try:
            cursor = self.db_connection.cursor()
            
            # Vendite oggi
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COALESCE(SUM(cash_income + coin_income + card_gross + satispay_gross), 0) 
                FROM sales 
                WHERE date = ?
            """, (today,))
            sales_today = cursor.fetchone()[0]
            self.sales_today_card.update_value(f"€ {sales_today:.2f}")
            
            # Vendite mese
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COALESCE(SUM(cash_income + coin_income + card_gross + satispay_gross), 0) 
                FROM sales 
                WHERE date >= ?
            """, (month_start,))
            sales_month = cursor.fetchone()[0]
            self.sales_month_card.update_value(f"€ {sales_month:.2f}")
            
            # Spese mese
            cursor.execute("""
                SELECT COALESCE(SUM(cash_payment + bank_payment), 0) 
                FROM purchases 
                WHERE date >= ?
            """, (month_start,))
            expenses_month = cursor.fetchone()[0]
            self.expenses_month_card.update_value(f"€ {expenses_month:.2f}")
            
            # Profitto
            profit = sales_month - expenses_month
            self.profit_card.update_value(f"€ {profit:.2f}")
            
            # Fatture pending
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM invoices 
                    WHERE ocr_status = 'pending' OR ocr_status IS NULL
                """)
                result = cursor.fetchone()
                pending_invoices = result[0] if result else 0
            except:
                pending_invoices = 0
            self.invoices_pending_card.update_value(str(pending_invoices))
            
            # Fornitori attivi
            cursor.execute("""
                SELECT COUNT(DISTINCT supplier_id) 
                FROM purchases 
                WHERE date >= ?
            """, (month_start,))
            active_suppliers = cursor.fetchone()[0]
            self.suppliers_card.update_value(str(active_suppliers))
            
            # Aggiorna grafici
            self.update_sales_chart(cursor)
            self.update_expenses_chart(cursor)
            
        except Exception as e:
            print(f"Errore aggiornamento dashboard: {e}")
    
    def update_sales_chart(self, cursor):
        """Aggiorna il grafico delle vendite"""
        try:
            # Ultimi 7 giorni
            dates = []
            values = []
            
            for i in range(6, -1, -1):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT COALESCE(SUM(cash_income + coin_income + card_gross + satispay_gross), 0) 
                    FROM sales 
                    WHERE date = ?
                """, (date_str,))
                
                daily_sales = cursor.fetchone()[0]
                dates.append(date)
                values.append(float(daily_sales))
            
            self.sales_chart.plot_sales_trend(dates, values)
            
        except Exception as e:
            print(f"Errore aggiornamento grafico vendite: {e}")
    
    def update_expenses_chart(self, cursor):
        """Aggiorna il grafico delle spese"""
        try:
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT s.name, COALESCE(SUM(p.cash_payment + p.bank_payment), 0)
                FROM suppliers s
                LEFT JOIN purchases p ON s.id = p.supplier_id 
                    AND p.date >= ?
                GROUP BY s.id, s.name
                HAVING SUM(p.cash_payment + p.bank_payment) > 0
                ORDER BY SUM(p.cash_payment + p.bank_payment) DESC
                LIMIT 5
            """, (month_start,))
            
            results = cursor.fetchall()
            
            if results:
                labels = [row[0] for row in results]
                values = [float(row[1]) for row in results]
                self.expenses_chart.plot_expenses_pie(labels, values)
            
        except Exception as e:
            print(f"Errore aggiornamento grafico spese: {e}")