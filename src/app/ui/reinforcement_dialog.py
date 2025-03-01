from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem)

class ReinforcementDialog(QDialog):
    def __init__(self, moment, concrete_class, width, height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Donatı Hesabı")
        self.setGeometry(200, 200, 500, 400)
        
        self.moment = moment
        self.concrete_class = concrete_class
        self.width = width
        self.height = height
        
        self.initUI()
        self.calculate()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Giriş parametreleri
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel(f"Moment: {self.moment:.2f} kNm"))
        input_layout.addWidget(QLabel(f"Beton Sınıfı: {self.concrete_class}"))
        input_layout.addWidget(QLabel(f"Kesit: {self.width}x{self.height} cm"))
        layout.addLayout(input_layout)
        
        # Sonuç tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Donatı Çapı (mm)", "Adet", "Toplam Alan (mm²)"])
        layout.addWidget(self.table)
        
        # Kapat butonu
        self.close_button = QPushButton("Kapat")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
    
    def calculate(self):
        from src.core.calculations.reinforcement import calculate_reinforcement
        
        results = calculate_reinforcement(self.moment, self.concrete_class, self.width, self.height)
        
        # Tabloyu doldur
        self.table.setRowCount(len(results["options"]))
        
        for i, option in enumerate(results["options"]):
            diameter, count = option
            area = 3.14159 * (diameter/2)**2 * count
            
            self.table.setItem(i, 0, QTableWidgetItem(f"{diameter}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{count}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{area:.2f}")) 