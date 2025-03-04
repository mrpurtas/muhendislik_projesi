from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QComboBox)
from PyQt6.QtCore import Qt

class ScenarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Senaryo Yönetimi")
        self.setGeometry(200, 200, 800, 400)
        self.scenarios = []
        
        # Beton sınıfları
        self.concrete_classes = ["C20", "C25", "C30", "C35", "C40", "C45", "C50"]
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Kiriş Uzunluğu (m)", 
            "Yük (kN)", 
            "Kesit Genişliği (cm)", 
            "Kesit Yüksekliği (cm)",
            "Beton Sınıfı"
        ])
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Senaryo Ekle")
        add_button.clicked.connect(self.add_scenario)
        button_layout.addWidget(add_button)
        
        remove_button = QPushButton("Seçili Senaryoyu Sil")
        remove_button.clicked.connect(self.remove_scenario)
        button_layout.addWidget(remove_button)
        
        clear_button = QPushButton("Tümünü Temizle")
        clear_button.clicked.connect(self.clear_scenarios)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # Onay butonları
        dialog_buttons = QHBoxLayout()
        
        ok_button = QPushButton("Hesapla")
        ok_button.clicked.connect(self.accept)
        dialog_buttons.addWidget(ok_button)
        
        cancel_button = QPushButton("İptal")
        cancel_button.clicked.connect(self.reject)
        dialog_buttons.addWidget(cancel_button)
        
        layout.addLayout(dialog_buttons)
        
        self.setLayout(layout)
        
        # Örnek senaryolar ekle
        self.add_example_scenarios()
    
    def add_scenario(self):
        """Yeni bir senaryo satırı ekle"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Uzunluk için QDoubleSpinBox
        length_spin = QDoubleSpinBox()
        length_spin.setRange(1.0, 20.0)
        length_spin.setValue(5.0)
        length_spin.setSingleStep(0.5)
        length_spin.setSuffix(" m")
        self.table.setCellWidget(row, 0, length_spin)
        
        # Yük için QDoubleSpinBox
        load_spin = QDoubleSpinBox()
        load_spin.setRange(1.0, 1000.0)
        load_spin.setValue(10.0)
        load_spin.setSingleStep(5.0)
        load_spin.setSuffix(" kN")
        self.table.setCellWidget(row, 1, load_spin)
        
        # Genişlik için QDoubleSpinBox
        width_spin = QDoubleSpinBox()
        width_spin.setRange(20.0, 100.0)
        width_spin.setValue(30.0)
        width_spin.setSingleStep(5.0)
        width_spin.setSuffix(" cm")
        self.table.setCellWidget(row, 2, width_spin)
        
        # Yükseklik için QDoubleSpinBox
        height_spin = QDoubleSpinBox()
        height_spin.setRange(30.0, 150.0)
        height_spin.setValue(50.0)
        height_spin.setSingleStep(5.0)
        height_spin.setSuffix(" cm")
        self.table.setCellWidget(row, 3, height_spin)
        
        # Beton sınıfı için QComboBox
        concrete_combo = QComboBox()
        concrete_combo.addItems(self.concrete_classes)
        concrete_combo.setCurrentText("C25")
        self.table.setCellWidget(row, 4, concrete_combo)
    
    def remove_scenario(self):
        """Seçili senaryoyu sil"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
    
    def clear_scenarios(self):
        """Tüm senaryoları temizle"""
        self.table.setRowCount(0)
    
    def add_example_scenarios(self):
        """Örnek senaryolar ekle"""
        examples = [
            (5.0, 10.0, 30.0, 50.0, "C25"),
            (6.0, 15.0, 35.0, 55.0, "C30"),
            (7.0, 20.0, 40.0, 60.0, "C35")
        ]
        
        for length, load, width, height, concrete in examples:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Uzunluk
            length_spin = QDoubleSpinBox()
            length_spin.setRange(1.0, 20.0)
            length_spin.setValue(length)
            length_spin.setSuffix(" m")
            self.table.setCellWidget(row, 0, length_spin)
            
            # Yük
            load_spin = QDoubleSpinBox()
            load_spin.setRange(1.0, 1000.0)
            load_spin.setValue(load)
            load_spin.setSuffix(" kN")
            self.table.setCellWidget(row, 1, load_spin)
            
            # Genişlik
            width_spin = QDoubleSpinBox()
            width_spin.setRange(20.0, 100.0)
            width_spin.setValue(width)
            width_spin.setSuffix(" cm")
            self.table.setCellWidget(row, 2, width_spin)
            
            # Yükseklik
            height_spin = QDoubleSpinBox()
            height_spin.setRange(30.0, 150.0)
            height_spin.setValue(height)
            height_spin.setSuffix(" cm")
            self.table.setCellWidget(row, 3, height_spin)
            
            # Beton sınıfı
            concrete_combo = QComboBox()
            concrete_combo.addItems(self.concrete_classes)
            concrete_combo.setCurrentText(concrete)
            self.table.setCellWidget(row, 4, concrete_combo)
    
    def accept(self):
        """Dialog'u kabul et ve senaryoları hazırla"""
        try:
            self.scenarios = []
            for row in range(self.table.rowCount()):
                scenario = {
                    "length": self.table.cellWidget(row, 0).value(),
                    "load": self.table.cellWidget(row, 1).value(),
                    "width": self.table.cellWidget(row, 2).value(),
                    "height": self.table.cellWidget(row, 3).value(),
                    "concrete_class": self.table.cellWidget(row, 4).currentText(),
                    "load_type": "Tekil Yük"  # Varsayılan yük tipi
                }
                self.scenarios.append(scenario)
            
            if not self.scenarios:
                QMessageBox.warning(self, "Uyarı", "En az bir senaryo ekleyin!")
                return
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e)) 