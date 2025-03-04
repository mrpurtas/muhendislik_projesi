from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLineEdit, QPushButton, QLabel, QComboBox, QGroupBox, QProgressBar, QCheckBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QGridLayout)
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
from concurrent.futures import ThreadPoolExecutor
import threading
from src.app.ui.scenario_results_dialog import ScenarioResultsDialog
from src.app.ui.scenario_dialog import ScenarioDialog

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
            calc_reinforcement = self.params["with_reinforcement"]
            
            # Hesaplama işlemlerini core modülüne taşıyoruz
            self.progress_update.emit(30)
            
            # Yapay gecikmeleri kaldır
            # time.sleep(0.3)  # 300 ms gecikme
            
            # Hesaplama sonuçlarını al
            beam_results = calculate_beam_analysis(
                length, load, width, height, concrete_class, 
                load_type=load_type, 
                with_reinforcement=calc_reinforcement
            )
            
            self.progress_update.emit(70)
            
            # Yapay gecikmeleri kaldır
            # time.sleep(0.2)  # 200 ms gecikme
            
            # Giriş parametrelerini sonuçlara ekle
            beam_results["length"] = length
            beam_results["load"] = load
            beam_results["width"] = width
            beam_results["height"] = height
            beam_results["concrete_class"] = concrete_class
            
            # Zaman bilgisini ekle
            elapsed_time = time.time() - start_time
            beam_results["elapsed_time"] = elapsed_time
            
            # Hesaplama süresini görselleştirme için formatla
            if "elapsed_time" in beam_results:
                elapsed_time_str = f"{beam_results['elapsed_time']:.8f}"  # 8 ondalık basamak göster
                result_text = f"Hesaplama Süresi: {elapsed_time_str} saniye"
            
            self.progress_update.emit(100)
            self.calculation_complete.emit(beam_results)
            
        except Exception as e:
            self.calculation_error.emit(str(e))

class ScenarioCalculationThread(QThread):
    calculation_complete = pyqtSignal(list)
    calculation_error = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    
    def __init__(self, scenarios):
        super().__init__()
        self.scenarios = scenarios
        self.lock = threading.Lock()
        self.completed = 0
        self.results = []
        # Boş liste durumunda hata oluşmasını önle
        if not scenarios:
            self.max_workers = 1
        else:
            self.max_workers = min(4, len(scenarios))  # CPU çekirdek sayısına göre, en fazla senaryo sayısı kadar
    
    def run(self):
        try:
            # Boş senaryo listesi kontrolü
            if not self.scenarios:
                self.calculation_complete.emit([])
                return
                
            # ThreadPoolExecutor ile paralel hesaplama
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Tüm senaryolar için hesaplama işlemlerini başlat
                future_to_scenario = {
                    executor.submit(self.calculate_scenario, i, scenario): (i, scenario)
                    for i, scenario in enumerate(self.scenarios)
                }
                
                # Tamamlanan hesaplamaları topla
                for future in future_to_scenario:
                    try:
                        # Hesaplama sonucunu al
                        future.result()
                    except Exception as e:
                        # Hata durumunda işlemi durdur
                        self.calculation_error.emit(f"Senaryo hesaplama hatası: {str(e)}")
                        return
            
            # Sonuçları sırala (senaryo indeksine göre)
            self.results.sort(key=lambda x: x["scenario_index"])
            
            # Sonuçları gönder
            self.calculation_complete.emit(self.results)
            
        except Exception as e:
            self.calculation_error.emit(f"Senaryo hesaplama hatası: {str(e)}")
    
    def calculate_scenario(self, index, scenario):
        """Tek bir senaryo için hesaplama yap"""
        try:
            # Hesaplama yap
            result = calculate_beam_analysis(
                length=scenario["length"],
                load=scenario["load"],
                width=scenario["width"],
                height=scenario["height"],
                concrete_class=scenario["concrete_class"],
                load_type=scenario.get("load_type", "Tekil Yük"),
                with_reinforcement=scenario.get("with_reinforcement", False)  # Donatı hesabı parametresini ekle
            )
            
            # Senaryo parametrelerini sonuca ekle
            result.update({
                "scenario_index": index,
                "length": scenario["length"],
                "load": scenario["load"],
                "width": scenario["width"],
                "height": scenario["height"],
                "concrete_class": scenario["concrete_class"],
                "load_type": scenario.get("load_type", "Tekil Yük"),
                "with_reinforcement": scenario.get("with_reinforcement", False)  # Donatı hesabı bilgisini sonuca ekle
            })
            
            # Thread-safe bir şekilde sonuçları ekle
            with self.lock:
                self.results.append(result)
                self.completed += 1
                # Boş senaryo listesi kontrolü ekle
                if len(self.scenarios) > 0:
                    progress = int((self.completed / len(self.scenarios)) * 100)
                    self.progress_update.emit(progress)
            
        except Exception as e:
            print(f"Senaryo {index} hesaplama hatası: {str(e)}")
            raise e

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kiriş Analizi Uygulaması")
        self.setMinimumSize(800, 600)  # Minimum pencere boyutu
        
        # Grafik ve rapor dizinlerini oluştur
        self.graph_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                  'outputs', 'graphs')
        if not os.path.exists(self.graph_path):
            os.makedirs(self.graph_path)
        
        # Ana widget ve layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Giriş parametreleri için grup kutusu
        input_group = QGroupBox("Hesaplama Parametreleri")
        input_layout = QHBoxLayout()  # QGridLayout yerine QHBoxLayout kullan
        
        # Sol taraf - Temel parametreler
        left_layout = QVBoxLayout()
        
        # Uzunluk
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Uzunluk (m):"))
        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("Kiriş uzunluğu")
        length_layout.addWidget(self.length_input)
        left_layout.addLayout(length_layout)
        
        # Yük
        load_layout = QHBoxLayout()
        load_layout.addWidget(QLabel("Yük (kN):"))
        self.load_input = QLineEdit()
        self.load_input.setPlaceholderText("Uygulanan yük")
        load_layout.addWidget(self.load_input)
        left_layout.addLayout(load_layout)
        
        # Genişlik
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Genişlik (cm):"))
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Kiriş genişliği")
        width_layout.addWidget(self.width_input)
        left_layout.addLayout(width_layout)
        
        # Yükseklik
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Yükseklik (cm):"))
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Kiriş yüksekliği")
        height_layout.addWidget(self.height_input)
        left_layout.addLayout(height_layout)
        
        # Sağ taraf - Ek parametreler
        right_layout = QVBoxLayout()
        
        # Beton sınıfı
        concrete_layout = QHBoxLayout()
        concrete_layout.addWidget(QLabel("Beton Sınıfı:"))
        self.concrete_class = QComboBox()
        self.concrete_class.addItems(["C20", "C25", "C30", "C35", "C40", "C45", "C50"])
        concrete_layout.addWidget(self.concrete_class)
        right_layout.addLayout(concrete_layout)
        
        # Yük tipi
        load_type_layout = QHBoxLayout()
        load_type_layout.addWidget(QLabel("Yük Tipi:"))
        self.load_type = QComboBox()
        self.load_type.addItems(["Tekil Yük", "Düzgün Yayılı Yük", "Üçgen Yayılı Yük"])
        load_type_layout.addWidget(self.load_type)
        right_layout.addLayout(load_type_layout)
        
        # Donatı hesabı
        reinforcement_layout = QHBoxLayout()
        self.reinforcement_check = QCheckBox("Donatı Hesabı Yap")
        reinforcement_layout.addWidget(self.reinforcement_check)
        right_layout.addLayout(reinforcement_layout)
        
        # Donatı sonuçları için onay kutusu
        self.show_reinforcement_table = QCheckBox("Donatı sonuçlarını tablo olarak göster")
        self.show_reinforcement_table.setChecked(True)
        right_layout.addWidget(self.show_reinforcement_table)
        
        # Sol ve sağ layoutları ana layout'a ekle
        input_layout.addLayout(left_layout)
        input_layout.addLayout(right_layout)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
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
        
        # Senaryo yönetimi butonu
        self.btn_scenarios = QPushButton("Senaryo Yönetimi")
        self.btn_scenarios.clicked.connect(self.show_scenarios)
        button_layout.addWidget(self.btn_scenarios)
        
        main_layout.addLayout(button_layout)
        
        # Sonuç alanı - Kaydırılabilir metin alanı olarak değiştir
        result_group = QGroupBox("Hesaplama Sonuçları")
        result_layout = QVBoxLayout()
        
        # QLabel yerine QTextEdit kullan ve salt okunur yap
        self.result_label = QTextEdit()
        self.result_label.setReadOnly(True)
        self.result_label.setFixedHeight(150)  # Yüksekliği sınırla
        self.result_label.setPlaceholderText("Hesaplama sonuçları burada görünecek...")
        
        result_layout.addWidget(self.result_label)
        result_group.setLayout(result_layout)
        
        # Grafik alanı - Minimum yükseklik ayarla
        graph_group = QGroupBox("Grafik Sonuçları")
        graph_layout = QVBoxLayout()
        
        # Matplotlib figürü ve canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)  # Minimum yükseklik ayarla
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        graph_layout.addWidget(self.toolbar)
        graph_layout.addWidget(self.canvas)
        
        graph_group.setLayout(graph_layout)
        
        # Ana layout'a ekle
        main_layout.addWidget(result_group)
        main_layout.addWidget(graph_group)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def save_graphs(self):
        """Grafikleri kaydet"""
        try:
            # Zaman damgası oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Grafik dosya yolunu oluştur
            filename = f"beam_graphs_{timestamp}.png"
            filepath = os.path.join(self.graph_path, filename)
            
            # Grafikleri kaydet
            self.figure.savefig(filepath, dpi=300, bbox_inches='tight')
            
            # Kullanıcıya bilgi ver
            self.result_label.setText(f"{self.result_label.toPlainText()}\n\nGrafikler kaydedildi: {filepath}")
            
        except Exception as e:
            print(f"Grafik kaydetme hatası: {str(e)}")
            self.result_label.setText(f"{self.result_label.toPlainText()}\n\nGrafik kaydetme hatası: {str(e)}")

    def save_results_to_csv(self, results):
        """Hesaplama sonuçlarını CSV dosyasına kaydet"""
        try:
            # Sonuçları hazırla
            data = [
                ["Parametre", "Değer", "Birim"],
                ["Kiriş Uzunluğu", results["length"], "m"],
                ["Yük", results["load"], "kN"],
                ["Kesit Genişliği", results["width"], "cm"],
                ["Kesit Yüksekliği", results["height"], "cm"],
                ["Beton Sınıfı", results["concrete_class"], ""],
                ["Maksimum Moment", results["moment"], "kNm"],
                ["Maksimum Kesme Kuvveti", results["shear"], "kN"],
                ["Maksimum Sehim", results["max_deflection"]*1000, "mm"],  # m -> mm dönüşümü
                ["Hesaplama Süresi", results.get("elapsed_time", 0), "saniye"]
            ]
            
            # Donatı sonuçları varsa ekle
            if "reinforcement" in results:
                reinforcement = results["reinforcement"]
                data.append(["", "", ""])
                data.append(["Donatı Hesabı Sonuçları", "", ""])
                data.append(["Minimum Donatı Alanı", reinforcement["min_area"], "mm²"])
                data.append(["Gerekli Donatı Alanı", reinforcement["required_area"], "mm²"])
                
                # Donatı seçeneklerini ekle
                data.append(["", "", ""])
                data.append(["Donatı Seçenekleri", "", ""])
                for i, option in enumerate(reinforcement["options"]):
                    data.append([
                        f"Seçenek {i+1}",
                        f"{option['count']} adet Ø{option['diameter']} mm",
                        f"Alan: {option['area']:.2f} mm², Aralık: {option['spacing']:.1f} mm"
                    ])
            
            # CSV dosyasını kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(os.path.dirname(self.graph_path), 
                                  'reports', f'beam_results_{timestamp}.csv')
            save_to_csv(data, filename)
            
            return filename
        except Exception as e:
            print(f"CSV kaydetme hatası: {str(e)}")
            return None

    def calculate(self):
        """Hesaplama işlemini başlat"""
        try:
            # Giriş değerlerini al
            if not self.length_input.text() or not self.load_input.text() or \
               not self.width_input.text() or not self.height_input.text():
                self.result_label.setText("Hata: Lütfen tüm değerleri girin!")
                return
            
            try:
                length = float(self.length_input.text().replace(',', '.'))
                load = float(self.load_input.text().replace(',', '.'))
                width = float(self.width_input.text().replace(',', '.'))
                height = float(self.height_input.text().replace(',', '.'))
            except ValueError:
                self.result_label.setText("Hata: Lütfen sayısal değerler girin!")
                return
            
            concrete_class = self.concrete_class.currentText()
            load_type = self.load_type.currentText()
            calc_reinforcement = self.reinforcement_check.isChecked()
            
            # Değerleri kontrol et
            if length <= 0 or load <= 0 or width <= 0 or height <= 0:
                self.result_label.setText("Hata: Tüm değerler pozitif olmalıdır!")
                return
            
            # Değerlerin mantıklı aralıkta olduğunu kontrol et
            if length > 100:  # Çok uzun kirişler için uyarı
                self.result_label.setText("Uyarı: Kiriş uzunluğu çok büyük (>100m)!")
                return
            
            # Kesit boyutları için katı sınırlama yerine sadece uyarı göster
            if width > 1000 or height > 1000:  # Çok büyük kesitler için uyarı
                from PyQt6.QtWidgets import QMessageBox
                response = QMessageBox.warning(
                    self, 
                    "Büyük Kesit Boyutları", 
                    f"Kesit boyutları oldukça büyük (genişlik: {width} cm, yükseklik: {height} cm).\n"
                    "Bu değerler olağandışı görünüyor. Devam etmek istiyor musunuz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if response == QMessageBox.StandardButton.No:
                    return
            
            # Değerleri konsola yazdır (debug için)
            print(f"Hesaplama parametreleri:")
            print(f"Uzunluk: {length} m")
            print(f"Yük: {load} kN")
            print(f"Genişlik: {width} cm")
            print(f"Yükseklik: {height} cm")
            print(f"Beton sınıfı: {concrete_class}")
            print(f"Yük tipi: {load_type}")
            
            # Hesaplama parametrelerini hazırla
            params = {
                "length": length,
                "load": load,
                "width": width,
                "height": height,
                "concrete_class": concrete_class,
                "load_type": load_type,
                "with_reinforcement": calc_reinforcement
            }
            
            # İlerleme çubuğunu göster
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Hesaplama thread'ini başlat
            self.calc_thread = CalculationThread(params)
            self.calc_thread.calculation_complete.connect(self.on_calculation_complete)
            self.calc_thread.calculation_error.connect(self.on_calculation_error)
            self.calc_thread.progress_update.connect(self.progress_bar.setValue)
            self.calc_thread.start()
            
        except Exception as e:
            import traceback
            traceback.print_exc()  # Konsola detaylı hata mesajı yazdır
            self.result_label.setText(f"Beklenmeyen hata: {str(e)}")

    def draw_graphs(self, results):
        """Hesaplama sonuçlarına göre grafikleri çiz"""
        try:
            # Grafik alanını temizle
            self.figure.clear()
            
            # Dağılım verilerini kontrol et
            if "x_values" not in results or "moment_distribution" not in results:
                # Dağılım verileri yoksa basit bir grafik göster
                ax = self.figure.add_subplot(111)
                ax.bar(["Moment", "Kesme", "Sehim"], 
                       [results["moment"], results["shear"], results["max_deflection"]*1000])
                ax.set_ylabel("Değer")
                ax.set_title("Hesaplama Sonuçları")
                self.canvas.draw()
                return
            
            # Dağılım verilerini al
            x_values = results["x_values"]
            moment_distribution = results["moment_distribution"]
            shear_distribution = results["shear_distribution"]
            deflection_distribution = results["deflection_distribution"]
            
            # Grafik boyutlarını ayarla - Daha büyük alt grafikler için
            self.figure.subplots_adjust(hspace=0.4)  # Alt grafikler arası boşluğu artır
            
            # 3 grafik çiz: Moment, Kesme Kuvveti ve Sehim
            ax1 = self.figure.add_subplot(311)
            ax1.plot(x_values, moment_distribution, 'b-', linewidth=2)
            ax1.set_ylabel("Moment (kNm)", fontsize=10)
            ax1.set_title("Moment Diyagramı", fontsize=12)
            ax1.grid(True)
            
            ax2 = self.figure.add_subplot(312)
            ax2.plot(x_values, shear_distribution, 'r-', linewidth=2)
            ax2.set_ylabel("Kesme Kuvveti (kN)", fontsize=10)
            ax2.set_title("Kesme Kuvveti Diyagramı", fontsize=12)
            ax2.grid(True)
            
            ax3 = self.figure.add_subplot(313)
            ax3.plot(x_values, deflection_distribution, 'g-', linewidth=2)
            ax3.set_xlabel("Konum (m)", fontsize=10)
            ax3.set_ylabel("Sehim (mm)", fontsize=10)
            ax3.set_title("Sehim Diyagramı", fontsize=12)
            ax3.grid(True)
            
            # Grafiklerin arasındaki boşluğu ayarla
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Grafik çizme hatası: {str(e)}")
            # Hata durumunda basit bir mesaj göster
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f"Grafik çizilemedi: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()

    def on_calculation_complete(self, results):
        """Hesaplama tamamlandığında"""
        # İlerleme çubuğunu gizle
        self.progress_bar.setVisible(False)
        
        # Sonuçları göster
        moment = results["moment"]
        shear = results["shear"]
        max_deflection = results["max_deflection"]
        elasticity_modulus = results.get("elasticity_modulus", 0)  # GPa cinsinden
        elapsed_time = results.get("elapsed_time", 0)
        
        # Hesaplama parametrelerini al
        length = results.get("length", 0)
        load = results.get("load", 0)
        width = results.get("width", 0)
        height = results.get("height", 0)
        concrete_class = results.get("concrete_class", "")
        load_type = results.get("load_type", "Tekil Yük")
        
        # Sonuç metnini oluştur - Parametreleri de ekle
        result_text = (
            f"Hesaplama Parametreleri:\n"
            f"Uzunluk: {length:.1f} m\n"
            f"Yük: {load:.1f} kN\n"
            f"Genişlik: {width:.1f} cm\n"
            f"Yükseklik: {height:.1f} cm\n"
            f"Beton sınıfı: {concrete_class}\n"
            f"Yük tipi: {load_type}\n\n"
            f"Hesaplama Sonuçları:\n"
            f"Maksimum Moment: {moment:.2f} kNm\n"
            f"Maksimum Kesme Kuvveti: {shear:.2f} kN\n"
            f"Maksimum Sehim: {max_deflection*1000:.2f} mm\n"
            f"Elastisite Modülü: {elasticity_modulus:.1f} GPa\n"
            f"Hesaplama Süresi: {elapsed_time:.6f} saniye"
        )
        
        # QTextEdit için setPlainText kullan
        self.result_label.setPlainText(result_text)
        
        # Grafikleri çiz
        self.draw_graphs(results)
        
        # Sonuçları CSV'ye kaydet
        self.save_results_to_csv(results)
        
        # Donatı sonuçları varsa ve tablo gösterilmek isteniyorsa
        if "reinforcement" in results and hasattr(self, 'show_reinforcement_table') and self.show_reinforcement_table.isChecked():
            self.show_reinforcement_results_table(results["reinforcement"])

    def on_calculation_error(self, error_message):
        """Hesaplama hatası durumunda"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Hesaplama Hatası", 
                           f"Hesaplama sırasında hata oluştu:\n{error_message}")
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
        self.length_input.clear()
        self.load_input.clear()
        self.width_input.clear()
        self.height_input.clear()
        self.concrete_class.setCurrentIndex(0)
        
        # Sonuç etiketini temizle
        self.result_label.clear()
        
        # Grafikleri temizle
        self.figure.clear()
        self.canvas.draw()

    def show_reinforcement(self):
        """Donatı hesabı penceresini göster"""
        try:
            # Gerekli parametreleri al ve doğrula
            if not self.length_input.text() or not self.load_input.text() or \
               not self.width_input.text() or not self.height_input.text():
                self.result_label.setText("Hata: Lütfen tüm değerleri girin!")
                return
            
            # Değerleri doğru formatta dönüştür
            try:
                length = float(self.length_input.text().replace(',', '.'))
                load = float(self.load_input.text().replace(',', '.'))
                width = float(self.width_input.text().replace(',', '.'))
                height = float(self.height_input.text().replace(',', '.'))
            except ValueError:
                self.result_label.setText("Hata: Lütfen sayısal değerler girin!")
                return
            
            concrete_class = self.concrete_class.currentText()
            load_type = self.load_type.currentText()  # Yük tipini al
            
            # Değerlerin mantıklı aralıkta olduğunu kontrol et
            if length <= 0 or load <= 0 or width <= 0 or height <= 0:
                self.result_label.setText("Hata: Değerler pozitif olmalıdır!")
                return
            
            # Moment hesapla (yük tipini ilet)
            moment = calculate_moment(load, length, load_type)
            
            # Değerleri konsola yazdır (debug için)
            print(f"Donatı hesabı parametreleri:")
            print(f"Moment: {moment} kNm")
            print(f"Beton sınıfı: {concrete_class}")
            print(f"Genişlik: {width} cm")
            print(f"Yükseklik: {height} cm")
            print(f"Yük tipi: {load_type}")
            
            # Donatı hesabı penceresini aç
            from src.app.ui.reinforcement_dialog import ReinforcementDialog
            dialog = ReinforcementDialog(moment, concrete_class, width, height, self)
            dialog.exec()
            
        except Exception as e:
            import traceback
            traceback.print_exc()  # Konsola detaylı hata mesajı yazdır
            self.result_label.setText(f"Beklenmeyen hata: {str(e)}")

    def show_scenarios(self):
        """Senaryo yönetimi penceresini göster"""
        dialog = ScenarioDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Senaryo hesaplamalarını başlat
            self.run_parallel_calculations(dialog.scenarios)
    
    def run_parallel_calculations(self, scenarios):
        """Paralel hesaplamaları başlat"""
        # Senaryo listesinin boş olup olmadığını kontrol et
        if not scenarios or len(scenarios) == 0:
            self.result_label.setText("Hata: Hesaplanacak senaryo bulunamadı!")
            return
            
        self.result_label.setText(f"Senaryo hesaplamaları başlatıldı... ({len(scenarios)} senaryo)")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Hesaplama thread'ini başlat
        self.scenario_thread = ScenarioCalculationThread(scenarios)
        self.scenario_thread.calculation_complete.connect(self.on_scenarios_complete)
        self.scenario_thread.calculation_error.connect(self.on_calculation_error)
        self.scenario_thread.progress_update.connect(self.progress_bar.setValue)
        self.scenario_thread.start()
    
    def on_scenarios_complete(self, results):
        """Senaryo hesaplamaları tamamlandığında"""
        # CSV'ye kaydet
        headers = ["Senaryo", "Kiriş Uzunluğu (m)", "Yük (kN)", 
                  "Kesit Genişliği (cm)", "Kesit Yüksekliği (cm)",
                  "Maksimum Moment (kNm)", "Maksimum Kesme (kN)", 
                  "Maksimum Sehim (mm)"]
        
        data = [headers]
        for i, result in enumerate(results):
            row = [
                f"Senaryo {i+1}",
                result["length"],
                result["load"],
                result["width"],
                result["height"],
                result["moment"],
                result["shear"],
                result["max_deflection"]*1000  # mm cinsinden
            ]
            data.append(row)
        
        # CSV dosyasını kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(os.path.dirname(self.graph_path), 
                              'reports', f'scenario_results_{timestamp}.csv')
        save_to_csv(data, filename)
        
        # Sonuçları göster
        self.result_label.setText(
            f"Senaryo hesaplamaları tamamlandı!\n"
            f"Toplam {len(results)} senaryo hesaplandı.\n"
            f"Sonuçlar kaydedildi: {os.path.basename(filename)}"
        )
        
        # Sonuç görselleştirme penceresini göster
        dialog = ScenarioResultsDialog(results, self)
        dialog.exec()
        
        self.progress_bar.setVisible(False)

    def show_reinforcement_results_table(self, reinforcement):
        """Donatı hesabı sonuçlarını tablo olarak göster"""
        # Tablo penceresi oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle("Donatı Hesabı Sonuçları")
        dialog.setGeometry(200, 200, 600, 400)
        
        # Tablo oluştur
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Çap (mm)", "Adet", "Toplam Alan (mm²)", "Aralık (mm)"])
        
        # Tablo verilerini doldur
        options = reinforcement["options"]
        table.setRowCount(len(options))
        
        for i, option in enumerate(options):
            table.setItem(i, 0, QTableWidgetItem(str(option["diameter"])))
            table.setItem(i, 1, QTableWidgetItem(str(option["count"])))
            table.setItem(i, 2, QTableWidgetItem(f"{option['area']:.2f}"))
            table.setItem(i, 3, QTableWidgetItem(f"{option['spacing']:.1f}"))
        
        # Tablo ayarları
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Kapat butonu
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(dialog.accept)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(table)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec()