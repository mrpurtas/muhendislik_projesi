from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLineEdit, QPushButton, QLabel, QComboBox, QGroupBox, QProgressBar, QCheckBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import os
import time
from src.core.utils.file_io import save_to_csv
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from src.core.calculations.beam_calculation import calculate_beam_analysis, calculate_moment
from math import ceil, sqrt
from src.core.calculations.load_types import calculate_uniform_load, calculate_triangular_load
from src.core.calculations.reinforcement import calculate_reinforcement

class CalculationThread(QThread):
    calculation_complete = pyqtSignal(dict)
    calculation_error = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
    
    def run(self):
        try:
            start_time = time.time()
            self.progress_update.emit(10)
            
            # Parametreleri al
            length = self.params["length"]
            load = self.params["load"]
            width = self.params["width"]
            height = self.params["height"]
            concrete_class = self.params["concrete_class"]
            load_type = self.params["load_type"]
            calc_reinforcement = self.params["calc_reinforcement"]
            
            # Hesaplama işlemlerini core modülüne taşıyoruz
            self.progress_update.emit(30)
            
            # Yapay gecikme ekleyelim (kullanıcı deneyimi için)
            time.sleep(0.3)  # 300 ms gecikme
            
            # Hesaplama sonuçlarını al
            beam_results = calculate_beam_analysis(
                length, load, width, height, concrete_class, 
                load_type=load_type, 
                calc_reinforcement=calc_reinforcement
            )
            
            self.progress_update.emit(70)
            
            # Yapay gecikme ekleyelim (kullanıcı deneyimi için)
            time.sleep(0.2)  # 200 ms gecikme
            
            # Giriş parametrelerini sonuçlara ekle
            beam_results["length"] = length
            beam_results["load"] = load
            beam_results["width"] = width
            beam_results["height"] = height
            beam_results["concrete_class"] = concrete_class
            
            # Zaman bilgisini ekle
            elapsed_time = time.time() - start_time
            # Gerçek süreyi göster (artık yapay gecikme eklediğimiz için minimum değere gerek yok)
            beam_results["elapsed_time"] = elapsed_time
            
            self.progress_update.emit(100)
            self.calculation_complete.emit(beam_results)
            
        except Exception as e:
            self.calculation_error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mühendislik Hesaplama Aracı")
        self.setGeometry(100, 100, 1200, 800)
        self.graph_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                     'outputs', 'graphs')
        if not os.path.exists(self.graph_path):
            os.makedirs(self.graph_path)
        self.initUI()

    def initUI(self):
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Giriş parametreleri için grup kutusu
        input_group = QGroupBox("Hesaplama Parametreleri")
        input_layout = QHBoxLayout()
        
        # Sol taraf - Temel parametreler
        left_layout = QVBoxLayout()
        
        # Kiriş Uzunluğu
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Kiriş Uzunluğu (m):"))
        self.input_length = QLineEdit()
        length_layout.addWidget(self.input_length)
        left_layout.addLayout(length_layout)
        
        # Yük
        load_layout = QHBoxLayout()
        load_layout.addWidget(QLabel("Yük (kN):"))
        self.input_load = QLineEdit()
        load_layout.addWidget(self.input_load)
        left_layout.addLayout(load_layout)
        
        # Yük tipi seçimi için ComboBox ekleyin
        load_type_layout = QHBoxLayout()
        load_type_layout.addWidget(QLabel("Yük Tipi:"))
        self.load_type = QComboBox()
        self.load_type.addItems(["Tekil Yük", "Düzgün Yayılı Yük", "Üçgen Yayılı Yük"])
        load_type_layout.addWidget(self.load_type)
        left_layout.addLayout(load_type_layout)
        
        input_layout.addLayout(left_layout)
        
        # Sağ taraf - Beton ve kesit parametreleri
        right_layout = QVBoxLayout()
        
        # Beton Sınıfı
        concrete_layout = QHBoxLayout()
        concrete_layout.addWidget(QLabel("Beton Sınıfı:"))
        self.concrete_class = QComboBox()
        self.concrete_class.addItems(["C20", "C25", "C30", "C35", "C40", "C45", "C50"])
        concrete_layout.addWidget(self.concrete_class)
        right_layout.addLayout(concrete_layout)
        
        # Donatı hesabı için checkbox ekleyin
        reinforcement_layout = QHBoxLayout()
        self.calculate_reinforcement = QCheckBox("Donatı Hesabı Yap")
        reinforcement_layout.addWidget(self.calculate_reinforcement)
        right_layout.addLayout(reinforcement_layout)
        
        # Kesit Boyutları
        section_layout = QHBoxLayout()
        section_layout.addWidget(QLabel("Kesit (cm):"))
        self.input_width = QLineEdit()
        self.input_width.setPlaceholderText("Genişlik")
        self.input_height = QLineEdit()
        self.input_height.setPlaceholderText("Yükseklik")
        section_layout.addWidget(self.input_width)
        section_layout.addWidget(self.input_height)
        right_layout.addLayout(section_layout)
        
        input_layout.addLayout(right_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Butonlar için yatay layout
        button_layout = QHBoxLayout()
        
        # Hesapla Butonu
        self.btn_calculate = QPushButton("Hesapla")
        self.btn_calculate.clicked.connect(self.calculate)
        button_layout.addWidget(self.btn_calculate)
        
        # Sıfırla Butonu
        self.btn_reset = QPushButton("Sıfırla")
        self.btn_reset.clicked.connect(self.reset)
        button_layout.addWidget(self.btn_reset)
        
        # Ayarlar Butonu
        self.btn_settings = QPushButton("Ayarlar")
        self.btn_settings.clicked.connect(self.show_settings)
        button_layout.addWidget(self.btn_settings)
        
        # Donatı hesabı butonu
        self.btn_reinforcement = QPushButton("Donatı Hesabı")
        self.btn_reinforcement.clicked.connect(self.show_reinforcement)
        button_layout.addWidget(self.btn_reinforcement)
        
        layout.addLayout(button_layout)
        
        # Sonuç Alanı
        self.result_label = QLabel()
        layout.addWidget(self.result_label)
        
        # Grafik Alanı
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        central_widget.setLayout(layout)

    def save_graphs(self):
        """Grafikleri outputs/graphs klasörüne kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.graph_path, f'beam_analysis_{timestamp}.png')
        self.figure.savefig(filename, dpi=300, bbox_inches='tight')
        return filename

    def save_results_to_csv(self, results):
        """Hesaplama sonuçlarını CSV dosyasına kaydet"""
        # CSV için veri hazırla
        headers = ["Parametre", "Değer", "Birim"]
        data = [
            headers,
            ["Kiriş Uzunluğu", results["length"], "m"],
            ["Yük", results["load"], "kN"],
            ["Kesit Genişliği", results["width"], "cm"],
            ["Kesit Yüksekliği", results["height"], "cm"],
            ["Beton Sınıfı", results["concrete_class"], ""],
            ["Maksimum Moment", results["moment"], "kNm"],
            ["Maksimum Kesme Kuvveti", results["shear"], "kN"],
            ["Maksimum Sehim", results["max_deflection"]*1000, "mm"],
            ["Hesaplama Süresi", results["elapsed_time"], "saniye"]
        ]
        
        # CSV dosya yolunu oluştur
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                               'outputs', 'reports')
        if not os.path.exists(csv_path):
            os.makedirs(csv_path)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(csv_path, f'beam_results_{timestamp}.csv')
        
        # CSV'ye kaydet
        save_to_csv(data, filename)
        return filename

    def calculate(self):
        """Hesaplama işlemini başlat"""
        try:
            # Giriş değerlerini al
            length = float(self.input_length.text())
            load = float(self.input_load.text())
            width = float(self.input_width.text())
            height = float(self.input_height.text())
            concrete_class = self.concrete_class.currentText()
            load_type = self.load_type.currentText()
            calc_reinforcement = self.calculate_reinforcement.isChecked()
            
            # İlerleme çubuğunu göster
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Hesaplama thread'ini başlat
            self.calculation_thread = CalculationThread({
                "length": length,
                "load": load,
                "width": width,
                "height": height,
                "concrete_class": concrete_class,
                "load_type": load_type,
                "calc_reinforcement": calc_reinforcement
            })
            self.calculation_thread.calculation_complete.connect(self.on_calculation_complete)
            self.calculation_thread.calculation_error.connect(self.on_calculation_error)
            self.calculation_thread.progress_update.connect(self.update_progress)
            self.calculation_thread.start()
            
        except ValueError:
            self.result_label.setText("Hata: Lütfen tüm değerleri doğru formatta girin!")

    def draw_graphs(self, results):
        """Hesaplama sonuçlarını grafiklere çiz"""
        self.figure.clear()
        
        # Üç grafik ekle
        ax1 = self.figure.add_subplot(311)  # Kesme Kuvveti
        ax2 = self.figure.add_subplot(312)  # Moment
        ax3 = self.figure.add_subplot(313)  # Sehim
        
        # Kesme Kuvveti
        ax1.plot(results["x"], results["shear_diagram"], 'r-', label='Kesme Kuvveti')
        ax1.grid(True)
        ax1.set_title('Kesme Kuvveti Diyagramı')
        ax1.set_ylabel('Kesme Kuvveti (kN)')
        ax1.legend()
        
        # Moment
        ax2.plot(results["x"], results["moment_diagram"], 'b-', label='Moment')
        ax2.grid(True)
        ax2.set_title('Moment Diyagramı')
        ax2.set_ylabel('Moment (kNm)')
        ax2.legend()
        
        # Sehim
        ax3.plot(results["x"], results["deflection_diagram"], 'g-', label='Sehim')
        ax3.grid(True)
        ax3.set_title('Sehim Diyagramı')
        ax3.set_xlabel('Kiriş Uzunluğu (m)')
        ax3.set_ylabel('Sehim (m)')
        ax3.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()

    def on_calculation_complete(self, results):
        # Grafikleri çiz
        self.draw_graphs(results)
        
        # Grafikleri kaydet
        saved_file = self.save_graphs()
        
        # Sonuçları CSV'ye kaydet
        csv_file = self.save_results_to_csv(results)
        
        # Donatı sonuçlarını göster
        if results.get("reinforcement_results"):
            reinforcement = results["reinforcement_results"]
            reinforcement_text = f"\nDonatı Hesabı:\n"
            reinforcement_text += f"Gerekli Donatı Alanı: {reinforcement['required_area']:.2f} mm²\n"
            reinforcement_text += "Donatı Seçenekleri:\n"
            
            for option in reinforcement["options"]:
                diameter, count = option
                reinforcement_text += f"- {count} adet Ø{diameter} mm\n"
            
            self.result_label.setText(
                f"Maksimum Moment: {results['moment']:.2f} kNm\n"
                f"Maksimum Kesme Kuvveti: {results['shear']:.2f} kN\n"
                f"Maksimum Sehim: {results['max_deflection']*1000:.2f} mm\n"
                f"Grafik kaydedildi: {os.path.basename(saved_file)}\n"
                f"CSV raporu kaydedildi: {os.path.basename(csv_file)}\n"
                f"İşlem süresi: {results['elapsed_time']:.2f} saniye\n"
                f"{reinforcement_text}"
            )
        else:
            self.result_label.setText(
                f"Maksimum Moment: {results['moment']:.2f} kNm\n"
                f"Maksimum Kesme Kuvveti: {results['shear']:.2f} kN\n"
                f"Maksimum Sehim: {results['max_deflection']*1000:.2f} mm\n"
                f"Grafik kaydedildi: {os.path.basename(saved_file)}\n"
                f"CSV raporu kaydedildi: {os.path.basename(csv_file)}\n"
                f"İşlem süresi: {results['elapsed_time']:.2f} saniye"
            )
        
        # İlerleme çubuğunu gizle
        self.progress_bar.setVisible(False)

    def on_calculation_error(self, error_message):
        self.result_label.setText(f"Hata: {error_message}")
        self.progress_bar.setVisible(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.progress_bar.repaint()

    def show_settings(self):
        """Ayarlar penceresini göster"""
        from src.app.ui.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self)
        settings_dialog.save_button.clicked.connect(lambda: self.apply_settings(settings_dialog))
        settings_dialog.cancel_button.clicked.connect(settings_dialog.close)
        settings_dialog.exec()
    
    def apply_settings(self, dialog):
        """Ayarları uygula"""
        # Koyu tema ayarı
        if dialog.dark_mode.isChecked():
            self.figure.set_facecolor('#2D2D30')
            for ax in self.figure.get_axes():
                ax.set_facecolor('#2D2D30')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
                for text in ax.get_legend().get_texts():
                    text.set_color('white')
        else:
            self.figure.set_facecolor('white')
            for ax in self.figure.get_axes():
                ax.set_facecolor('white')
                ax.tick_params(colors='black')
                ax.xaxis.label.set_color('black')
                ax.yaxis.label.set_color('black')
                ax.title.set_color('black')
                for text in ax.get_legend().get_texts():
                    text.set_color('black')
        
        # Izgara çizgileri
        for ax in self.figure.get_axes():
            ax.grid(dialog.grid_lines.isChecked())
        
        self.canvas.draw()
        dialog.close()

    def reset(self):
        """Tüm değerleri ve grafikleri sıfırla"""
        # Giriş alanlarını temizle
        self.input_length.clear()
        self.input_load.clear()
        self.input_width.clear()
        self.input_height.clear()
        self.concrete_class.setCurrentIndex(0)
        
        # Sonuç etiketini temizle
        self.result_label.clear()
        
        # Grafikleri temizle
        self.figure.clear()
        self.canvas.draw()

    def show_reinforcement(self):
        """Donatı hesabı penceresini göster"""
        try:
            # Gerekli parametreleri al
            length = float(self.input_length.text())
            load = float(self.input_load.text())
            width = float(self.input_width.text())
            height = float(self.input_height.text())
            concrete_class = self.concrete_class.currentText()
            
            # Moment hesapla
            from src.core.calculations.beam_calculation import calculate_moment
            moment = calculate_moment(load, length)
            
            # Donatı hesabı penceresini aç
            from src.app.ui.reinforcement_dialog import ReinforcementDialog
            dialog = ReinforcementDialog(moment, concrete_class, width, height, self)
            dialog.exec()
            
        except ValueError:
            self.result_label.setText("Hata: Lütfen tüm değerleri doğru formatta girin!")