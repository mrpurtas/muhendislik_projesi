import unittest
import numpy as np
from src.core.calculations.load_types import (
    calculate_uniform_load, calculate_triangular_load, calculate_point_loads
)

class TestLoadTypes(unittest.TestCase):
    """Yük tipi fonksiyonlarını test eden sınıf"""
    
    def setUp(self):
        """Test için ortak değişkenleri ayarla"""
        self.load = 10.0  # kN veya kN/m
        self.length = 5.0  # m
    
    def test_uniform_load(self):
        """Düzgün yayılı yük hesaplama fonksiyonunu test et"""
        moment, shear, max_deflection = calculate_uniform_load(self.load, self.length)
        
        # Düzgün yayılı yük için moment = q*L²/8
        expected_moment = self.load * self.length**2 / 8
        self.assertAlmostEqual(moment, expected_moment, places=2)
        
        # Düzgün yayılı yük için kesme kuvveti = q*L/2
        expected_shear = self.load * self.length / 2
        self.assertAlmostEqual(shear, expected_shear, places=2)
        
        # Sehim değerinin pozitif olduğunu kontrol et
        self.assertGreater(max_deflection, 0)
    
    def test_triangular_load(self):
        """Üçgen yayılı yük hesaplama fonksiyonunu test et"""
        moment, shear, max_deflection = calculate_triangular_load(self.load, self.length)
        
        # Üçgen yayılı yük için moment = q*L²/12
        expected_moment = self.load * self.length**2 / 12
        self.assertAlmostEqual(moment, expected_moment, places=2)
        
        # Üçgen yayılı yük için kesme kuvveti = q*L/3
        expected_shear = self.load * self.length / 3
        self.assertAlmostEqual(shear, expected_shear, places=2)
        
        # Sehim değerinin pozitif olduğunu kontrol et
        self.assertGreater(max_deflection, 0)
    
    def test_point_loads(self):
        """Tekil yük hesaplama fonksiyonunu test et"""
        moment, shear, max_deflection = calculate_point_loads(self.load, self.length)
        
        # Tekil yük için moment = P*L/4
        expected_moment = self.load * self.length / 4
        self.assertAlmostEqual(moment, expected_moment, places=2)
        
        # Tekil yük için kesme kuvveti = P/2
        expected_shear = self.load / 2
        self.assertAlmostEqual(shear, expected_shear, places=2)
        
        # Sehim değerinin pozitif olduğunu kontrol et
        self.assertGreater(max_deflection, 0)
    
    def test_distributions(self):
        """Dağılım hesaplama fonksiyonlarını test et"""
        # Test noktaları
        x_points = np.linspace(0, self.length, 100)
        E = 30e9  # N/m²
        I = 1e-4  # m⁴
        
        # Düzgün yayılı yük dağılımları
        from src.core.calculations.load_types import (
            calculate_moment_distribution_uniform_load,
            calculate_shear_distribution_uniform_load,
            calculate_deflection_distribution_uniform_load
        )
        
        moment_dist = calculate_moment_distribution_uniform_load(self.load, self.length, x_points)
        shear_dist = calculate_shear_distribution_uniform_load(self.load, self.length, x_points)
        deflection_dist = calculate_deflection_distribution_uniform_load(self.load, self.length, E, I, x_points)
        
        self.assertEqual(len(moment_dist), len(x_points))
        self.assertEqual(len(shear_dist), len(x_points))
        self.assertEqual(len(deflection_dist), len(x_points))
        
        # Maksimum moment değerini kontrol et
        max_moment = np.max(moment_dist)
        expected_max_moment = self.load * self.length**2 / 8
        self.assertAlmostEqual(max_moment, expected_max_moment, places=2)
        
        # Maksimum kesme kuvveti değerini kontrol et
        max_shear = np.max(np.abs(shear_dist))
        expected_max_shear = self.load * self.length / 2
        self.assertAlmostEqual(max_shear, expected_max_shear, places=2)

if __name__ == '__main__':
    unittest.main() 