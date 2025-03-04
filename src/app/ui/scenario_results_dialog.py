from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QTableWidget, 
                           QTableWidgetItem, QTabWidget, QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class ScenarioResultsDialog(QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Senaryo Sonuçları")
        self.setGeometry(100, 100, 800, 600)
        self.results = results
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Sekme widget'ı
        tab_widget = QTabWidget()
        
        # Tablo sekmesi
        table_tab = QWidget()
        table_layout = QVBoxLayout()
        self.results_table = self.create_results_table()
        table_layout.addWidget(self.results_table)
        table_tab.setLayout(table_layout)
        tab_widget.addTab(table_tab, "Tablo")
        
        # Grafik sekmesi
        graph_tab = QWidget()
        graph_layout = QVBoxLayout()
        self.plot_figure = self.create_plots()
        graph_layout.addWidget(self.plot_figure)
        graph_tab.setLayout(graph_layout)
        tab_widget.addTab(graph_tab, "Grafikler")
        
        layout.addWidget(tab_widget)
        
        # Butonlar
        button_layout = QHBoxLayout()
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_results_table(self):
        """Sonuçları tablo olarak göster"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Senaryo", "Kiriş Uzunluğu (m)", "Yük (kN)", 
            "Kesit Genişliği (cm)", "Kesit Yüksekliği (cm)",
            "Maks. Moment (kNm)", "Maks. Kesme (kN)", 
            "Maks. Sehim (mm)"
        ])
        
        table.setRowCount(len(self.results))
        
        for i, result in enumerate(self.results):
            table.setItem(i, 0, QTableWidgetItem(f"Senaryo {i+1}"))
            table.setItem(i, 1, QTableWidgetItem(f"{result['length']:.2f}"))
            table.setItem(i, 2, QTableWidgetItem(f"{result['load']:.1f}"))
            table.setItem(i, 3, QTableWidgetItem(f"{result['width']:.1f}"))
            table.setItem(i, 4, QTableWidgetItem(f"{result['height']:.1f}"))
            table.setItem(i, 5, QTableWidgetItem(f"{result['moment']:.2f}"))
            table.setItem(i, 6, QTableWidgetItem(f"{result['shear']:.2f}"))
            table.setItem(i, 7, QTableWidgetItem(f"{result['max_deflection']*1000:.2f}"))
        
        table.resizeColumnsToContents()
        return table
    
    def create_plots(self):
        """Sonuçları grafiklerle göster"""
        fig = Figure(figsize=(8, 6))
        
        # Grafik düzeni: 2x2
        ax1 = fig.add_subplot(221)  # Moment
        ax2 = fig.add_subplot(222)  # Kesme
        ax3 = fig.add_subplot(223)  # Sehim
        ax4 = fig.add_subplot(224)  # Donatı
        
        # Veri hazırlığı
        lengths = [r['length'] for r in self.results]
        moments = [r['moment'] for r in self.results]
        shears = [r['shear'] for r in self.results]
        deflections = [r['max_deflection']*1000 for r in self.results]  # mm cinsinden
        areas = [r['reinforcement']['required_area'] for r in self.results if 'reinforcement' in r]
        
        # Grafikleri çiz
        ax1.plot(lengths, moments, 'b-')
        ax1.set_title('Maksimum Moment')
        ax1.set_xlabel('Kiriş Uzunluğu (m)')
        ax1.set_ylabel('Moment (kNm)')
        ax1.grid(True)
        
        ax2.plot(lengths, shears, 'r-')
        ax2.set_title('Maksimum Kesme')
        ax2.set_xlabel('Kiriş Uzunluğu (m)')
        ax2.set_ylabel('Kesme Kuvveti (kN)')
        ax2.grid(True)
        
        ax3.plot(lengths, deflections, 'g-')
        ax3.set_title('Maksimum Sehim')
        ax3.set_xlabel('Kiriş Uzunluğu (m)')
        ax3.set_ylabel('Sehim (mm)')
        ax3.grid(True)
        
        if areas:  # Donatı hesabı yapıldıysa
            ax4.plot(lengths, areas, 'm-')
            ax4.set_title('Gerekli Donatı Alanı')
            ax4.set_xlabel('Kiriş Uzunluğu (m)')
            ax4.set_ylabel('Donatı Alanı (mm²)')
            ax4.grid(True)
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        return canvas 