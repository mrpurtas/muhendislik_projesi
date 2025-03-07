from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QSlider, QLabel, QComboBox, QGroupBox, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FuncAnimation

class Beam3DVisualization(QWidget):
    """Kiriş için 3D görselleştirme widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Kiriş Görünümü")
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        
        # Matplotlib figürü ve canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)
        
        # 3D axes oluştur
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Kontrol paneli için grup kutusu
        control_group = QGroupBox("Görselleştirme Kontrolleri")
        control_grid = QGridLayout(control_group)
        
        # Görünüm ayarları grubu
        view_group = QGroupBox("Görünüm Ayarları")
        view_layout = QGridLayout(view_group)
        
        # Görünüm seçenekleri
        view_layout.addWidget(QLabel("Görünüm:"), 0, 0)
        self.view_combo = QComboBox()
        self.view_combo.addItems(["İzometrik", "Üstten", "Yandan", "Önden", "Serbest"])
        self.view_combo.currentIndexChanged.connect(self.change_view)
        self.view_combo.setMinimumWidth(120)
        view_layout.addWidget(self.view_combo, 0, 1)
        
        # Deformasyon ölçeği
        view_layout.addWidget(QLabel("Deformasyon:"), 1, 0)
        scale_layout = QHBoxLayout()
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(1)
        self.scale_slider.setMaximum(100)
        self.scale_slider.setValue(20)
        self.scale_slider.valueChanged.connect(self.update_scale_label)
        scale_layout.addWidget(self.scale_slider)
        self.scale_value = QLabel("2.0")
        self.scale_value.setMinimumWidth(30)
        scale_layout.addWidget(self.scale_value)
        view_layout.addLayout(scale_layout, 1, 1)
        
        # Görselleştirme seçenekleri grubu
        options_group = QGroupBox("Görselleştirme Seçenekleri")
        options_layout = QGridLayout(options_group)
        
        # Butonlar için stil tanımla
        button_style = """
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #c0c0c0;
            border-radius: 4px;
            padding: 5px;
            min-height: 25px;
        }
        QPushButton:checked {
            background-color: #a0d0ff;
            border: 1px solid #0078d7;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        """
        
        # Donatı görünümü
        self.show_reinforcement = QPushButton("Donatıları Göster")
        self.show_reinforcement.setCheckable(True)
        self.show_reinforcement.clicked.connect(self.update_visualization)
        self.show_reinforcement.setStyleSheet(button_style)
        options_layout.addWidget(self.show_reinforcement, 0, 0)
        
        # Kesit görünümü
        self.show_section = QPushButton("Kesit Göster")
        self.show_section.setCheckable(True)
        self.show_section.clicked.connect(self.toggle_section_view)
        self.show_section.setStyleSheet(button_style)
        options_layout.addWidget(self.show_section, 0, 1)
        
        # Kesit pozisyonu slider'ı
        section_layout = QHBoxLayout()
        section_layout.addWidget(QLabel("Kesit Pozisyonu:"))
        self.section_slider = QSlider(Qt.Orientation.Horizontal)
        self.section_slider.setMinimum(0)
        self.section_slider.setMaximum(100)
        self.section_slider.setValue(50)
        self.section_slider.valueChanged.connect(self.update_visualization)
        self.section_slider.setEnabled(False)  # Başlangıçta devre dışı
        section_layout.addWidget(self.section_slider)
        options_layout.addLayout(section_layout, 1, 0, 1, 2)
        
        # Animasyon butonu
        self.animate_button = QPushButton("Animasyon")
        self.animate_button.setCheckable(True)
        self.animate_button.clicked.connect(self.toggle_animation)
        self.animate_button.setStyleSheet(button_style)
        options_layout.addWidget(self.animate_button, 2, 0)
        
        # Gerilme görünümü
        options_layout.addWidget(QLabel("Gerilme Görünümü:"), 2, 1)
        self.stress_combo = QComboBox()
        self.stress_combo.addItems(["Gösterme", "Moment", "Kesme Kuvveti"])
        self.stress_combo.currentIndexChanged.connect(self.update_visualization)
        options_layout.addWidget(self.stress_combo, 3, 1)
        
        # Sıfırla butonu
        self.reset_button = QPushButton("Sıfırla")
        self.reset_button.clicked.connect(self.reset_visualization)
        self.reset_button.setStyleSheet(button_style)
        options_layout.addWidget(self.reset_button, 3, 0)
        
        # Görünüm kaydetme butonu
        self.save_button = QPushButton("Görünümü Kaydet")
        self.save_button.clicked.connect(self.save_view)
        self.save_button.setStyleSheet(button_style)
        options_layout.addWidget(self.save_button, 4, 0, 1, 2)
        
        # Kontrol grid'ine grupları ekle
        control_grid.addWidget(view_group, 0, 0)
        control_grid.addWidget(options_group, 0, 1)
        
        # Layout'a widget'ları ekle
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(control_group)
        
        # Veri değişkenleri
        self.beam_data = None
        self.reinforcement_data = None
        
        # Animasyon için değişkenler
        self.animation = None
        self.is_animating = False
        
        # Başlangıç görünümü
        self.clear_visualization()
        
    def reset_visualization(self):
        """Görselleştirmeyi sıfırla"""
        # Butonları sıfırla
        self.show_reinforcement.setChecked(False)
        self.show_section.setChecked(False)
        self.animate_button.setChecked(False)
        self.section_slider.setEnabled(False)
        self.stress_combo.setCurrentIndex(0)  # "Gösterme" seçeneğine ayarla
        
        # Ölçeği varsayılana ayarla
        self.scale_slider.setValue(20)
        
        # Görünümü sıfırla
        self.view_combo.setCurrentIndex(0)  # İzometrik görünüm
        
        # Animasyonu durdur
        if self.is_animating:
            self.toggle_animation()
        
        # Orijinal veriyi koruyarak görselleştirmeyi güncelle
        if self.beam_data is not None:
            # Orijinal veriyi yedekle
            original_data = self.beam_data.copy()
            
            # Görselleştirmeyi güncelle
            self.update_visualization()
            
            # Eksen sınırlarını ayarla - Kiriş boyutlarına göre
            length = original_data['length']
            width = original_data['width']
            height = original_data['height']
            
            # Eksen sınırlarını ayarla
            self.ax.set_xlim(0, length)
            self.ax.set_ylim(-width/2, width/2)
            self.ax.set_zlim(-height/2 - 10, height/2 + 10)
            
            # İzometrik görünüm
            self.ax.view_init(elev=30, azim=45)
            
            # Canvas'ı güncelle
            self.canvas.draw()
        else:
            # Veri yoksa temizle
            self.clear_visualization()
    
    def update_scale_label(self, value):
        """Ölçek değeri etiketini güncelle"""
        self.scale_value.setText(f"{value/10:.1f}")
        self.update_visualization()
    
    def set_beam_data(self, length, width, height, x_values=None, deflection=None, load_type=None):
        """Kiriş verilerini ayarla"""
        self.beam_data = {
            'length': length,
            'width': width,
            'height': height,
            'x_values': x_values if x_values is not None else np.linspace(0, length, 100),
            'deflection': deflection if deflection is not None else np.zeros(100),
            'load_type': load_type
        }
        self.update_visualization()
    
    def set_reinforcement_data(self, reinforcement_data):
        """Donatı verilerini ayarla"""
        self.reinforcement_data = reinforcement_data
        self.update_visualization()
    
    def clear_visualization(self):
        """Görselleştirmeyi temizle"""
        self.ax.clear()
        self.ax.set_xlabel('Uzunluk (m)')
        self.ax.set_ylabel('Genişlik (cm)')
        self.ax.set_zlabel('Yükseklik (cm)')
        self.ax.set_title('3D Kiriş Görünümü')
        self.ax.text(0.5, 0.5, 0.5, "Hesaplama sonuçları burada görüntülenecek", 
                    horizontalalignment='center', verticalalignment='center')
        self.canvas.draw()
        
        # Veri değişkenlerini sıfırla
        self.beam_data = None
        self.reinforcement_data = None
    
    def update_visualization(self):
        """Görselleştirmeyi güncelle"""
        # Önceki tüm çizimleri temizle
        self.ax.clear()
        
        if self.beam_data is None:
            self.clear_visualization()
            return
        
        # Kiriş parametrelerini al
        length = self.beam_data['length']
        width = self.beam_data['width']
        height = self.beam_data['height']
        x_values = self.beam_data['x_values']
        deflection = self.beam_data['deflection']
        
        # Deformasyon ölçeği
        scale_factor = self.scale_slider.value() / 10.0
        
        # Kiriş mesh'i oluştur
        X, Y = np.meshgrid(x_values, np.linspace(-width/2, width/2, 30))
        Z_bottom = np.zeros_like(X) - height/2
        Z_top = np.zeros_like(X) + height/2
        
        # Deformasyonu ekle
        if deflection is not None and len(deflection) > 0:
            # Deformasyonu y ekseni boyunca tekrarla
            deflection_2d = np.tile(deflection, (Y.shape[0], 1))
            # Ölçeklendir ve uygula
            Z_bottom = Z_bottom + deflection_2d * scale_factor * 100  # cm'ye çevir
            Z_top = Z_top + deflection_2d * scale_factor * 100  # cm'ye çevir
        
        # Gerilme dağılımı
        stress_type = self.stress_combo.currentText()
        stress_values = None
        
        if stress_type != "Gösterme":
            # Gerilme değerlerini al
            if stress_type == "Moment":
                stress_values = self.beam_data.get('moment_distribution', np.zeros_like(x_values))
                stress_label = "Moment (kNm)"
            else:  # Kesme Kuvveti
                stress_values = self.beam_data.get('shear_distribution', np.zeros_like(x_values))
                stress_label = "Kesme Kuvveti (kN)"
            
            # Normalize edilmiş gerilme değerleri (renk haritası için)
            if np.max(np.abs(stress_values)) > 0:
                norm_stress = stress_values / np.max(np.abs(stress_values))
            else:
                norm_stress = np.zeros_like(stress_values)
        
        # Kiriş yüzeylerini çiz
        y_min, y_max = -width/2, width/2
        
        if stress_values is not None:
            # Gerilme renklerini uygula
            stress_colors = plt.cm.jet(0.5 + 0.5 * norm_stress)
            
            # Kiriş yüzeylerini gerilme renkleriyle çiz
            for i in range(len(x_values)-1):
                x = x_values[i]
                x_next = x_values[i+1]
                color = stress_colors[i]
                
                # Alt ve üst yüzeyler
                for j in range(Y.shape[0]-1):
                    y = Y[j, 0]
                    y_next = Y[j+1, 0]
                    
                    # Alt yüzey
                    verts_bottom = [
                        (x, y, Z_bottom[j, i]),
                        (x_next, y, Z_bottom[j, i+1]),
                        (x_next, y_next, Z_bottom[j+1, i+1]),
                        (x, y_next, Z_bottom[j+1, i])
                    ]
                    poly_bottom = Poly3DCollection([verts_bottom], alpha=0.7)
                    poly_bottom.set_facecolor(color)
                    self.ax.add_collection3d(poly_bottom)
                    
                    # Üst yüzey
                    verts_top = [
                        (x, y, Z_top[j, i]),
                        (x_next, y, Z_top[j, i+1]),
                        (x_next, y_next, Z_top[j+1, i+1]),
                        (x, y_next, Z_top[j+1, i])
                    ]
                    poly_top = Poly3DCollection([verts_top], alpha=0.7)
                    poly_top.set_facecolor(color)
                    self.ax.add_collection3d(poly_top)
                
                # Yan yüzeyler (ön ve arka)
                verts_front = [
                    (x, y_min, Z_bottom[0, i]),
                    (x_next, y_min, Z_bottom[0, i+1]),
                    (x_next, y_min, Z_top[0, i+1]),
                    (x, y_min, Z_top[0, i])
                ]
                poly_front = Poly3DCollection([verts_front], alpha=0.7)
                poly_front.set_facecolor(color)
                self.ax.add_collection3d(poly_front)
                
                verts_back = [
                    (x, y_max, Z_bottom[-1, i]),
                    (x_next, y_max, Z_bottom[-1, i+1]),
                    (x_next, y_max, Z_top[-1, i+1]),
                    (x, y_max, Z_top[-1, i])
                ]
                poly_back = Poly3DCollection([verts_back], alpha=0.7)
                poly_back.set_facecolor(color)
                self.ax.add_collection3d(poly_back)
            
            # Sol ve sağ yan yüzeyler
            left_color = stress_colors[0]
            right_color = stress_colors[-1]
            
            for j in range(Y.shape[0]-1):
                y = Y[j, 0]
                y_next = Y[j+1, 0]
                
                # Sol yüzey
                verts_left = [
                    (x_values[0], y, Z_bottom[j, 0]),
                    (x_values[0], y_next, Z_bottom[j+1, 0]),
                    (x_values[0], y_next, Z_top[j+1, 0]),
                    (x_values[0], y, Z_top[j, 0])
                ]
                poly_left = Poly3DCollection([verts_left], alpha=0.7)
                poly_left.set_facecolor(left_color)
                self.ax.add_collection3d(poly_left)
                
                # Sağ yüzey
                verts_right = [
                    (x_values[-1], y, Z_bottom[j, -1]),
                    (x_values[-1], y_next, Z_bottom[j+1, -1]),
                    (x_values[-1], y_next, Z_top[j+1, -1]),
                    (x_values[-1], y, Z_top[j, -1])
                ]
                poly_right = Poly3DCollection([verts_right], alpha=0.7)
                poly_right.set_facecolor(right_color)
                self.ax.add_collection3d(poly_right)
        else:
            # Normal görünüm - Renk haritası ile
            # Alt yüzey
            surf_bottom = self.ax.plot_surface(X, Y, Z_bottom, alpha=0.8, 
                                              cmap=cm.viridis, linewidth=0.5, 
                                              antialiased=True, edgecolor='k')
            # Üst yüzey
            surf_top = self.ax.plot_surface(X, Y, Z_top, alpha=0.8, 
                                           cmap=cm.viridis, linewidth=0.5, 
                                           antialiased=True, edgecolor='k')
        
        # Yan yüzeyler
        for x_idx in range(0, len(x_values), 5):
            x = x_values[x_idx]
            xs = [x, x, x, x, x]
            ys = [y_min, y_max, y_max, y_min, y_min]
            zs_bottom = [Z_bottom[0, x_idx], Z_bottom[-1, x_idx], 
                        Z_top[-1, x_idx], Z_top[0, x_idx], Z_bottom[0, x_idx]]
            self.ax.plot(xs, ys, zs_bottom, 'k-', alpha=0.5, linewidth=1.5)
        
        # Donatıları çiz
        if self.show_reinforcement.isChecked() and self.reinforcement_data:
            self.draw_reinforcement()
        
        # Yük tipini göster
        self.draw_load_type()
        
        # Kesit görünümü
        if self.show_section.isChecked():
            # Kesit pozisyonu
            section_pos = self.section_slider.value() / 100.0 * length
            section_idx = np.argmin(np.abs(x_values - section_pos))
            
            # Kesit düzlemi
            x_section = x_values[section_idx]
            y_section = np.linspace(-width/2, width/2, 20)
            
            # Kesit çizgisi
            self.ax.plot([x_section, x_section], [y_min, y_max], 
                        [Z_bottom[0, section_idx], Z_bottom[-1, section_idx]], 
                        'r-', linewidth=3, label='Kesit')
            
            # Kesit düzlemi
            Y_section, Z_section = np.meshgrid(y_section, np.linspace(-height/2, height/2, 20))
            X_section = np.ones_like(Y_section) * x_section
            
            # Kesit düzlemini çiz
            self.ax.plot_surface(X_section, Y_section, Z_section, alpha=0.3, 
                                color='r', linewidth=0, antialiased=True)
            
            # Kesit bilgisi
            self.ax.text(x_section, 0, height/2 + 5, f"Kesit: {x_section:.2f} m", 
                        color='red', horizontalalignment='center')
        
        # Renk çubuğu (gerilme görünümü için)
        if stress_values is not None:
            # Önceki renk çubuklarını temizle
            if hasattr(self, 'colorbar') and self.colorbar is not None:
                self.colorbar.remove()
            
            # Renk çubuğunu ekle
            sm = plt.cm.ScalarMappable(cmap=plt.cm.jet, 
                                      norm=plt.Normalize(vmin=np.min(stress_values), 
                                                       vmax=np.max(stress_values)))
            sm.set_array([])
            self.colorbar = self.figure.colorbar(sm, ax=self.ax, shrink=0.5, aspect=5, 
                                               label=stress_label)
        
        # Eksen etiketleri ve başlık
        self.ax.set_xlabel('Uzunluk (m)')
        self.ax.set_ylabel('Genişlik (cm)')
        self.ax.set_zlabel('Yükseklik (cm)')
        self.ax.set_title('3D Kiriş Görünümü')
        
        # Eksen sınırlarını ayarla
        self.ax.set_xlim(0, length)
        self.ax.set_ylim(-width/2, width/2)
        self.ax.set_zlim(-height/2 - 10, height/2 + 10)
        
        # Görünümü güncelle
        self.canvas.draw()
        
    def draw_reinforcement(self):
        """Donatıları çiz"""
        if not self.reinforcement_data or not self.beam_data:
            return
        
        # Kiriş parametreleri
        length = self.beam_data['length']
        width = self.beam_data['width']
        height = self.beam_data['height']
        
        # Donatı parametreleri
        options = self.reinforcement_data.get('options', [])
        if not options:
            return
        
        # İlk donatı seçeneğini kullan
        option = options[0]
        count = option.get('count', 4)
        diameter = option.get('diameter', 12) / 10  # mm -> cm
        spacing = option.get('spacing', 10)
        
        # Donatı çubukları için x koordinatları
        x_coords = np.linspace(0, length, 100)
        
        # Alt donatılar
        bottom_cover = 5  # cm
        z_bottom = -height/2 + bottom_cover
        
        # Donatı yerleşimi
        if count <= 2:
            # Tek sıra donatı
            y_positions = [0]
        else:
            # Çoklu donatı
            available_width = width - 2 * bottom_cover
            y_positions = np.linspace(-available_width/2, available_width/2, min(count, 6))
        
        # Donatıları çiz - Daha gerçekçi görünüm
        for y_pos in y_positions:
            # Silindir şeklinde donatı çiz
            theta = np.linspace(0, 2*np.pi, 20)
            radius = diameter / 2
            
            # Donatı boyunca birkaç noktada silindir çiz
            for x_pos in np.linspace(0.1, length-0.1, 10):
                circle_x = np.ones_like(theta) * x_pos
                circle_y = y_pos + radius * np.cos(theta)
                circle_z = z_bottom + radius * np.sin(theta)
                self.ax.plot(circle_x, circle_y, circle_z, 'r-', linewidth=2)
            
            # Donatı çubuğunu çiz
            self.ax.plot(x_coords, [y_pos] * len(x_coords), [z_bottom] * len(x_coords), 
                        'r-', linewidth=diameter*2, label='Donatı')
        
        # Etriyeler - Daha gerçekçi görünüm
        stirrup_spacing = 20  # cm
        num_stirrups = int(length * 100 / stirrup_spacing) + 1
        stirrup_positions = np.linspace(0, length, num_stirrups)
        
        for x_pos in stirrup_positions:
            # Etriye köşe noktaları
            xs = [x_pos, x_pos, x_pos, x_pos, x_pos]
            ys = [-width/2 + bottom_cover, width/2 - bottom_cover, 
                 width/2 - bottom_cover, -width/2 + bottom_cover, -width/2 + bottom_cover]
            zs = [z_bottom, z_bottom, height/2 - bottom_cover, 
                 height/2 - bottom_cover, z_bottom]
            self.ax.plot(xs, ys, zs, 'g-', linewidth=1.5, alpha=0.7)
            
            # Etriye kancaları
            hook_length = 5  # cm
            # Alt sol kanca
            self.ax.plot([x_pos, x_pos], 
                        [-width/2 + bottom_cover, -width/2 + bottom_cover], 
                        [z_bottom, z_bottom + hook_length], 
                        'g-', linewidth=1.5, alpha=0.7)
            # Alt sağ kanca
            self.ax.plot([x_pos, x_pos], 
                        [width/2 - bottom_cover, width/2 - bottom_cover], 
                        [z_bottom, z_bottom + hook_length], 
                        'g-', linewidth=1.5, alpha=0.7)
        
        # Donatı bilgilerini göster
        self.ax.text(length/2, 0, -height/2 - 5, 
                    f"Donatı: {count}Φ{int(diameter*10)}mm", 
                    color='red', horizontalalignment='center')
        
    def draw_load_type(self):
        """Yük tipini göster"""
        if not self.beam_data or not self.beam_data.get('load_type'):
            return
        
        # Kiriş parametreleri
        length = self.beam_data['length']
        height = self.beam_data['height']
        load_type = self.beam_data['load_type']
        
        # Yük yüksekliği
        load_height = height/2 + 10  # cm
        
        # Yük tipine göre çizim
        if load_type == "Tekil Yük":
            # Kiriş ortasında tekil yük
            x_pos = length / 2
            self.ax.quiver(x_pos, 0, load_height, 0, 0, -5, 
                          color='r', arrow_length_ratio=0.3, linewidth=3)
            self.ax.text(x_pos, 0, load_height + 2, "Tekil Yük", 
                        horizontalalignment='center')
            
        elif load_type == "Düzgün Yayılı Yük":
            # Düzgün yayılı yük
            x_positions = np.linspace(0.1, length - 0.1, 10)
            for x_pos in x_positions:
                self.ax.quiver(x_pos, 0, load_height, 0, 0, -3, 
                              color='b', arrow_length_ratio=0.3, linewidth=2)
            self.ax.text(length/2, 0, load_height + 2, "Düzgün Yayılı Yük", 
                        horizontalalignment='center')
                
        elif load_type == "Üçgen Yayılı Yük":
            # Üçgen yayılı yük
            x_positions = np.linspace(0.1, length - 0.1, 10)
            for i, x_pos in enumerate(x_positions):
                # Üçgen dağılım: sağa doğru artan
                arrow_length = -3 * (i + 1) / len(x_positions)
                self.ax.quiver(x_pos, 0, load_height, 0, 0, arrow_length, 
                              color='g', arrow_length_ratio=0.3, linewidth=2)
            self.ax.text(length/2, 0, load_height + 2, "Üçgen Yayılı Yük", 
                        horizontalalignment='center')
    
    def change_view(self):
        """Görünüm açısını değiştir"""
        view_type = self.view_combo.currentText()
        
        if view_type == "İzometrik":
            self.ax.view_init(elev=30, azim=45)
        elif view_type == "Üstten":
            self.ax.view_init(elev=90, azim=0)
        elif view_type == "Yandan":
            self.ax.view_init(elev=0, azim=0)
        elif view_type == "Önden":
            self.ax.view_init(elev=0, azim=90)
            
        self.canvas.draw()
        
    def toggle_section_view(self):
        """Kesit görünümünü aç/kapat"""
        self.section_slider.setEnabled(self.show_section.isChecked())
        self.update_visualization()
        
    def toggle_animation(self):
        """Animasyonu başlat/durdur"""
        self.is_animating = self.animate_button.isChecked()
        
        if self.is_animating and self.beam_data is not None:
            self.start_animation()
        else:
            self.stop_animation()

    def start_animation(self):
        """Deformasyon animasyonunu başlat"""
        if self.animation is not None:
            self.animation.event_source.stop()
        
        # Animasyon için veri hazırla
        frames = 50
        self.anim_scale_factors = np.linspace(0, self.scale_slider.value() / 10.0, frames)
        self.anim_frame = 0
        
        # Animasyon fonksiyonu
        def update_anim(frame):
            if not self.is_animating:
                return
            
            self.anim_frame = (self.anim_frame + 1) % frames
            scale = self.anim_scale_factors[self.anim_frame]
            
            # Kiriş parametrelerini al
            length = self.beam_data['length']
            width = self.beam_data['width']
            height = self.beam_data['height']
            x_values = self.beam_data['x_values']
            deflection = self.beam_data['deflection']
            
            # Önceki çizimleri temizle
            self.ax.clear()
            
            # Kiriş mesh'i güncelle
            X, Y = np.meshgrid(x_values, np.linspace(-width/2, width/2, 20))
            Z_bottom = np.zeros_like(X) - height/2
            Z_top = np.zeros_like(X) + height/2
            
            # Deformasyonu ekle
            if deflection is not None and len(deflection) > 0:
                deflection_2d = np.tile(deflection, (Y.shape[0], 1))
                Z_bottom = Z_bottom + deflection_2d * scale * 100
                Z_top = Z_top + deflection_2d * scale * 100
            
            # Alt ve üst yüzeyleri çiz
            self.ax.plot_surface(X, Y, Z_bottom, alpha=0.7, 
                                cmap=cm.coolwarm, linewidth=0, antialiased=True)
            self.ax.plot_surface(X, Y, Z_top, alpha=0.7, 
                                cmap=cm.coolwarm, linewidth=0, antialiased=True)
            
            # Eksen etiketleri
            self.ax.set_xlabel('Uzunluk (m)')
            self.ax.set_ylabel('Genişlik (cm)')
            self.ax.set_zlabel('Yükseklik (cm)')
            self.ax.set_title('3D Kiriş Animasyonu')
            
            self.canvas.draw()
        
        # Animasyonu başlat
        self.animation = FuncAnimation(self.figure, update_anim, frames=frames, 
                                      interval=50, blit=False)
        self.canvas.draw()

    def stop_animation(self):
        """Animasyonu durdur"""
        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
        
        # Normal görünüme dön
        self.update_visualization()

    def save_view(self):
        """Mevcut görünümü PNG dosyası olarak kaydet"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        
        # Varsayılan dosya adı
        default_filename = f"beam_3d_view_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # Dosya kaydetme diyaloğu
        filename, _ = QFileDialog.getSaveFileName(
            self, "Görünümü Kaydet", default_filename, "PNG Dosyaları (*.png)"
        )
        
        if filename:
            # Görünümü kaydet
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            
            # Kullanıcıya bilgi ver
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Kayıt Başarılı", 
                                  f"Görünüm başarıyla kaydedildi:\n{filename}") 