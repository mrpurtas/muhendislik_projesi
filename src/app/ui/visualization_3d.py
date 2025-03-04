from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QComboBox
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
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
        
        # Daha iyi düzenlenmiş kontrol paneli
        control_layout = QHBoxLayout()
        
        # Sol kontrol grubu
        left_controls = QVBoxLayout()
        left_controls.addWidget(QLabel("<b>Görünüm Ayarları</b>"))
        
        # Görünüm seçenekleri
        view_layout = QHBoxLayout()
        view_layout.addWidget(QLabel("Görünüm:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["İzometrik", "Üstten", "Yandan", "Önden", "Serbest"])
        self.view_combo.currentIndexChanged.connect(self.change_view)
        view_layout.addWidget(self.view_combo)
        left_controls.addLayout(view_layout)
        
        # Deformasyon ölçeği
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Deformasyon:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(1)
        self.scale_slider.setMaximum(100)
        self.scale_slider.setValue(20)
        self.scale_slider.valueChanged.connect(self.update_visualization)
        scale_layout.addWidget(self.scale_slider)
        self.scale_value = QLabel("2.0")
        scale_layout.addWidget(self.scale_value)
        left_controls.addLayout(scale_layout)
        
        # Sağ kontrol grubu
        right_controls = QVBoxLayout()
        right_controls.addWidget(QLabel("<b>Görselleştirme Seçenekleri</b>"))
        
        # Donatı ve kesit görünümü
        options_layout = QHBoxLayout()
        self.show_reinforcement = QPushButton("Donatılar")
        self.show_reinforcement.setCheckable(True)
        self.show_reinforcement.clicked.connect(self.update_visualization)
        options_layout.addWidget(self.show_reinforcement)
        
        self.show_section = QPushButton("Kesit")
        self.show_section.setCheckable(True)
        self.show_section.clicked.connect(self.toggle_section_view)
        options_layout.addWidget(self.show_section)
        
        self.animate_button = QPushButton("Animasyon")
        self.animate_button.setCheckable(True)
        self.animate_button.clicked.connect(self.toggle_animation)
        options_layout.addWidget(self.animate_button)
        
        # Gerilme görünümü
        stress_layout = QHBoxLayout()
        stress_layout.addWidget(QLabel("Gerilme:"))
        self.stress_combo = QComboBox()
        self.stress_combo.addItems(["Gösterme", "Moment", "Kesme Kuvveti"])
        self.stress_combo.currentIndexChanged.connect(self.update_visualization)
        stress_layout.addWidget(self.stress_combo)
        
        # Görünüm kaydetme butonu
        self.save_button = QPushButton("Görünümü Kaydet")
        self.save_button.clicked.connect(self.save_view)
        control_layout.addWidget(self.save_button)
        
        # Kontrol gruplarını ana kontrol paneline ekle
        control_layout.addLayout(left_controls, 1)
        control_layout.addLayout(right_controls, 1)
        
        # Layout'a widget'ları ekle
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(control_layout)
        
        # Veri değişkenleri
        self.beam_data = None
        self.reinforcement_data = None
        
        # Başlangıç görünümü
        self.clear_visualization()
        
        # Animasyon için değişkenler
        self.animation = None
        self.is_animating = False
        
        # Slider değeri değiştiğinde etiketi güncelle
        self.scale_slider.valueChanged.connect(self.update_scale_label)
        
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
        
    def set_reinforcement_data(self, reinforcement):
        """Donatı verilerini ayarla"""
        self.reinforcement_data = reinforcement
        self.update_visualization()
        
    def clear_visualization(self):
        """Görselleştirmeyi temizle"""
        self.ax.clear()
        self.ax.set_xlabel('Uzunluk (m)')
        self.ax.set_ylabel('Genişlik (cm)')
        self.ax.set_zlabel('Yükseklik (cm)')
        self.ax.set_title('3D Kiriş Görünümü')
        self.canvas.draw()
        
    def update_visualization(self):
        """Görselleştirmeyi güncelle"""
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
        
        # Kiriş mesh'i oluştur - Daha yüksek çözünürlük
        X, Y = np.meshgrid(x_values, np.linspace(-width/2, width/2, 30))  # 20 yerine 30 nokta
        Z_bottom = np.zeros_like(X) - height/2
        Z_top = np.zeros_like(X) + height/2
        
        # Deformasyonu ekle
        if deflection is not None and len(deflection) > 0:
            # Deformasyonu y ekseni boyunca tekrarla
            deflection_2d = np.tile(deflection, (Y.shape[0], 1))
            # Ölçeklendir ve uygula
            Z_bottom = Z_bottom + deflection_2d * scale_factor * 100  # cm'ye çevir
            Z_top = Z_top + deflection_2d * scale_factor * 100  # cm'ye çevir
        
        # Kiriş yüzeylerini çiz - Daha iyi renk haritası ve kenar çizgileri
        # Alt yüzey
        surf_bottom = self.ax.plot_surface(X, Y, Z_bottom, alpha=0.8, 
                                          cmap=cm.viridis, linewidth=0.5, 
                                          antialiased=True, edgecolor='k')
        # Üst yüzey
        surf_top = self.ax.plot_surface(X, Y, Z_top, alpha=0.8, 
                                       cmap=cm.viridis, linewidth=0.5, 
                                       antialiased=True, edgecolor='k')
        
        # Yan yüzeyler - Daha iyi görünüm
        y_min, y_max = -width/2, width/2
        for x_idx in range(0, len(x_values), 5):  # Her 10 yerine her 5 noktada bir yan yüzey
            x = x_values[x_idx]
            xs = [x, x, x, x, x]
            ys = [y_min, y_max, y_max, y_min, y_min]
            zs_bottom = [Z_bottom[0, x_idx], Z_bottom[-1, x_idx], 
                        Z_top[-1, x_idx], Z_top[0, x_idx], Z_bottom[0, x_idx]]
            self.ax.plot(xs, ys, zs_bottom, 'k-', alpha=0.5, linewidth=1.5)
        
        # Ön ve arka yüzeyler
        for y_idx in [0, -1]:  # İlk ve son y değeri
            y = [-width/2, width/2][y_idx]
            xs = x_values
            ys = [y] * len(x_values)
            zs_bottom = Z_bottom[y_idx, :]
            zs_top = Z_top[y_idx, :]
            self.ax.plot(xs, ys, zs_bottom, 'k-', alpha=0.3)
            self.ax.plot(xs, ys, zs_top, 'k-', alpha=0.3)
        
        # Donatıları göster
        if self.show_reinforcement.isChecked() and self.reinforcement_data is not None:
            self.draw_reinforcement()
        
        # Yük tipini göster
        if self.beam_data.get('load_type'):
            self.draw_load_type()
        
        # Kesit görünümü
        if self.show_section.isChecked() and self.beam_data is not None:
            # Kesit pozisyonu
            section_pos = self.section_slider.value() / 100.0 * length
            section_idx = np.argmin(np.abs(x_values - section_pos))
            
            # Kesit düzlemi
            x_section = x_values[section_idx]
            y_section = np.linspace(-width/2, width/2, 20)
            z_bottom_section = Z_bottom[:, section_idx]
            z_top_section = Z_top[:, section_idx]
            
            # Kesit çizgisi
            self.ax.plot([x_section, x_section], [y_min, y_max], [Z_bottom[0, section_idx], Z_bottom[-1, section_idx]], 
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
        
        # Gerilme dağılımı
        stress_type = self.stress_combo.currentText()
        if stress_type != "Gösterme" and self.beam_data is not None:
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
            
            # Gerilme renklerini uygula
            stress_colors = plt.cm.jet(0.5 + 0.5 * norm_stress)
            
            # Kiriş üzerinde gerilme dağılımını göster
            for i in range(len(x_values)-1):
                x = x_values[i]
                x_next = x_values[i+1]
                color = stress_colors[i]
                
                # Üst yüzeyde gerilme çizgisi
                self.ax.plot([x, x_next], [0, 0], [Z_top[10, i], Z_top[10, i+1]], 
                            color=color, linewidth=5)
            
            # Renk çubuğu
            sm = plt.cm.ScalarMappable(cmap=plt.cm.jet, 
                                      norm=plt.Normalize(vmin=np.min(stress_values), 
                                                       vmax=np.max(stress_values)))
            sm.set_array([])
            cbar = self.figure.colorbar(sm, ax=self.ax, shrink=0.5, aspect=5, 
                                      label=stress_label)
        
        # Eksen etiketleri
        self.ax.set_xlabel('Uzunluk (m)')
        self.ax.set_ylabel('Genişlik (cm)')
        self.ax.set_zlabel('Yükseklik (cm)')
        self.ax.set_title('3D Kiriş Görünümü')
        
        # Görünüm sınırları
        self.ax.set_xlim(0, length)
        self.ax.set_ylim(-width/2, width/2)
        self.ax.set_zlim(-height/2 - 10, height/2 + 10)
        
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
            
            # Kiriş mesh'i güncelle
            X, Y = np.meshgrid(x_values, np.linspace(-width/2, width/2, 20))
            Z_bottom = np.zeros_like(X) - height/2
            Z_top = np.zeros_like(X) + height/2
            
            # Deformasyonu ekle
            if deflection is not None and len(deflection) > 0:
                deflection_2d = np.tile(deflection, (Y.shape[0], 1))
                Z_bottom = Z_bottom + deflection_2d * scale * 100
                Z_top = Z_top + deflection_2d * scale * 100
            
            # Yüzeyleri güncelle
            for collection in self.ax.collections:
                collection.remove()
            
            # Alt ve üst yüzeyleri çiz
            self.ax.plot_surface(X, Y, Z_bottom, alpha=0.7, 
                                cmap=cm.coolwarm, linewidth=0, antialiased=True)
            self.ax.plot_surface(X, Y, Z_top, alpha=0.7, 
                                cmap=cm.coolwarm, linewidth=0, antialiased=True)
            
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

    def update_scale_label(self, value):
        self.scale_value.setText(f"{value/10:.1f}")
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