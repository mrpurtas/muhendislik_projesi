from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QCheckBox, QPushButton, QLabel, QComboBox, QGroupBox)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.setGeometry(200, 200, 400, 300)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Grafik ayarları
        graph_group = QGroupBox("Grafik Ayarları")
        graph_layout = QVBoxLayout()
        
        self.dark_mode = QCheckBox("Koyu Tema")
        graph_layout.addWidget(self.dark_mode)
        
        self.grid_lines = QCheckBox("Izgara Çizgileri")
        self.grid_lines.setChecked(True)
        graph_layout.addWidget(self.grid_lines)
        
        graph_group.setLayout(graph_layout)
        layout.addWidget(graph_group)
        
        # Birim ayarları
        unit_group = QGroupBox("Birim Ayarları")
        unit_layout = QVBoxLayout()
        
        unit_layout.addWidget(QLabel("Uzunluk Birimi:"))
        self.length_unit = QComboBox()
        self.length_unit.addItems(["metre (m)", "santimetre (cm)", "milimetre (mm)"])
        unit_layout.addWidget(self.length_unit)
        
        unit_group.setLayout(unit_layout)
        layout.addWidget(unit_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Kaydet")
        self.cancel_button = QPushButton("İptal")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout) 