from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QTableWidget, 
                           QTableWidgetItem, QSpinBox, QDoubleSpinBox)

class ScenarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Senaryo Yönetimi")
        self.setGeometry(200, 200, 600, 400)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Tablo oluştur
        self.scenario_table = QTableWidget()
        self.scenario_table.setColumnCount(4)
        self.scenario_table.setHorizontalHeaderLabels(["Parametre", "Minimum", "Maksimum", "Adım Sayısı"])
        
        # Varsayılan parametreleri ekle
        parameters = [
            ("Kiriş Uzunluğu (m)", 1.0, 10.0, 5),
            ("Yük (kN)", 10.0, 100.0, 5),
            ("Kesit Genişliği (cm)", 20.0, 50.0, 4),
            ("Kesit Yüksekliği (cm)", 30.0, 80.0, 4)
        ]
        
        self.scenario_table.setRowCount(len(parameters))
        
        for i, (param, min_val, max_val, steps) in enumerate(parameters):
            # Parametre adı
            self.scenario_table.setItem(i, 0, QTableWidgetItem(param))
            
            # Minimum değer
            min_spin = QDoubleSpinBox()
            min_spin.setRange(0.1, 1000.0)
            min_spin.setValue(min_val)
            self.scenario_table.setCellWidget(i, 1, min_spin)
            
            # Maksimum değer
            max_spin = QDoubleSpinBox()
            max_spin.setRange(0.1, 1000.0)
            max_spin.setValue(max_val)
            self.scenario_table.setCellWidget(i, 2, max_spin)
            
            # Adım sayısı
            step_spin = QSpinBox()
            step_spin.setRange(2, 20)
            step_spin.setValue(steps)
            self.scenario_table.setCellWidget(i, 3, step_spin)
        
        layout.addWidget(self.scenario_table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("Hesapla")
        self.calculate_button.clicked.connect(self.run_scenarios)
        button_layout.addWidget(self.calculate_button)
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def run_scenarios(self):
        scenarios = []
        for row in range(self.scenario_table.rowCount()):
            param = self.scenario_table.item(row, 0).text()
            min_val = self.scenario_table.cellWidget(row, 1).value()
            max_val = self.scenario_table.cellWidget(row, 2).value()
            steps = self.scenario_table.cellWidget(row, 3).value()
            
            scenarios.append({
                "param": param,
                "min": min_val,
                "max": max_val,
                "steps": steps
            })
        
        self.accept() 