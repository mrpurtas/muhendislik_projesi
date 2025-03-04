from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QPushButton, QHeaderView)
from PyQt6.QtCore import Qt
from src.core.calculations.reinforcement import calculate_reinforcement

class ReinforcementDialog(QDialog):
    def __init__(self, moment, concrete_class, width, height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Donatı Hesabı Sonuçları")
        self.setGeometry(200, 200, 600, 400)
        
        # Parametreleri kaydet
        self.moment = moment
        self.concrete_class = concrete_class
        self.width = width / 100  # cm -> m
        self.height = height / 100  # cm -> m
        
        # Hesaplama yap
        self.calculate_reinforcement()
        
        # UI oluştur
        self.init_ui()
    
    def calculate_reinforcement(self):
        """Donatı hesabını yap"""
        # Varsayılan değerlerle results'ı başlat
        self.results = {
            "min_area": 0,
            "required_area": 0,
            "options": []
        }
        
        try:
            print(f"Donatı hesabı başlatılıyor: Moment={self.moment}, Beton={self.concrete_class}")
            self.results = calculate_reinforcement(
                moment=self.moment,
                concrete_class=self.concrete_class,
                width=self.width,
                height=self.height
            )
            print(f"Donatı hesabı tamamlandı: Gerekli Alan={self.results['required_area']} mm²")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.results["error"] = str(e)
    
    def init_ui(self):
        """UI bileşenlerini oluştur"""
        layout = QVBoxLayout()
        
        # Parametreler
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel(f"Moment: {self.moment:.2f} kNm"))
        params_layout.addWidget(QLabel(f"Beton Sınıfı: {self.concrete_class}"))
        params_layout.addWidget(QLabel(f"Kesit: {self.width*100:.0f}×{self.height*100:.0f} cm"))
        layout.addLayout(params_layout)
        
        # Hata varsa göster
        if "error" in self.results:
            error_label = QLabel(f"Hata: {self.results['error']}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)
        else:
            # Sonuçlar
            results_layout = QHBoxLayout()
            results_layout.addWidget(QLabel(f"Minimum Donatı Alanı: {self.results['min_area']:.2f} mm²"))
            results_layout.addWidget(QLabel(f"Gerekli Donatı Alanı: {self.results['required_area']:.2f} mm²"))
            layout.addLayout(results_layout)
            
            # Donatı seçenekleri tablosu
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Çap (mm)", "Adet", "Toplam Alan (mm²)", "Aralık (mm)"])
            
            # Tablo verilerini doldur
            options = self.results["options"]
            table.setRowCount(len(options))
            
            for i, option in enumerate(options):
                table.setItem(i, 0, QTableWidgetItem(str(option["diameter"])))
                table.setItem(i, 1, QTableWidgetItem(str(option["count"])))
                table.setItem(i, 2, QTableWidgetItem(f"{option['area']:.2f}"))
                table.setItem(i, 3, QTableWidgetItem(f"{option['spacing']:.1f}"))
            
            # Tablo ayarları
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            layout.addWidget(table)
        
        # Kapat butonu
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout) 