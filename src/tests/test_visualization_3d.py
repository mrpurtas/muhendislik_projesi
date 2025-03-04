import unittest
import numpy as np
from PyQt6.QtWidgets import QApplication
import sys
from src.app.ui.visualization_3d import Beam3DVisualization

class TestVisualization3D(unittest.TestCase):
    """3D görselleştirme modülü testleri"""
    
    @classmethod
    def setUpClass(cls):
        # PyQt uygulaması başlat
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def test_initialization(self):
        """Widget başlatma testi"""
        widget = Beam3DVisualization()
        self.assertIsNotNone(widget)
        self.assertIsNotNone(widget.figure)
        self.assertIsNotNone(widget.ax)
    
    def test_set_beam_data(self):
        """Kiriş verisi ayarlama testi"""
        widget = Beam3DVisualization()
        
        # Test verileri
        length = 5.0
        width = 30.0
        height = 50.0
        x_values = np.linspace(0, length, 100)
        deflection = np.sin(np.pi * x_values / length) * 0.01
        
        # Verileri ayarla
        widget.set_beam_data(length, width, height, x_values, deflection, "Tekil Yük")
        
        # Verilerin doğru ayarlandığını kontrol et
        self.assertEqual(widget.beam_data['length'], length)
        self.assertEqual(widget.beam_data['width'], width)
        self.assertEqual(widget.beam_data['height'], height)
        self.assertEqual(widget.beam_data['load_type'], "Tekil Yük")
        self.assertTrue(np.array_equal(widget.beam_data['x_values'], x_values))
        self.assertTrue(np.array_equal(widget.beam_data['deflection'], deflection))
    
    def test_set_reinforcement_data(self):
        """Donatı verisi ayarlama testi"""
        widget = Beam3DVisualization()
        
        # Test verileri
        reinforcement = {
            'min_area': 100.0,
            'required_area': 150.0,
            'options': [
                {'count': 4, 'diameter': 12, 'spacing': 10, 'area': 452.4}
            ]
        }
        
        # Verileri ayarla
        widget.set_reinforcement_data(reinforcement)
        
        # Verilerin doğru ayarlandığını kontrol et
        self.assertEqual(widget.reinforcement_data, reinforcement)

if __name__ == '__main__':
    unittest.main() 