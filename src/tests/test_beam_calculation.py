import unittest
import numpy as np
from src.core.calculations.beam_calculation import (
    calculate_beam_analysis, calculate_moment,
    calculate_deflection, calculate_deflection_uniform_load, calculate_deflection_triangular_load
)
from src.core.calculations.load_types import (
    calculate_uniform_load, calculate_triangular_load, calculate_point_loads,
    calculate_moment_distribution_uniform_load, calculate_shear_distribution_uniform_load,
    calculate_deflection_distribution_uniform_load,
    calculate_moment_distribution_triangular_load, calculate_shear_distribution_triangular_load,
    calculate_deflection_distribution_triangular_load
)

class TestBeamCalculation(unittest.TestCase):
    """Kiriş hesaplama fonksiyonlarını test eden sınıf"""
    
    def setUp(self):
        """Test için ortak değişkenleri ayarla"""
        self.length = 5.0  # m
        self.load = 10.0  # kN
        self.width = 30.0  # cm
        self.height = 50.0  # cm
        self.concrete_class = "C25"
    
    def test_moment_calculation(self):
        """Moment hesaplama fonksiyonunu test et"""
        # Tekil yük
        moment_point = calculate_moment(self.load, self.length, "Tekil Yük")
        expected_moment_point = self.load * self.length / 4
        self.assertAlmostEqual(moment_point, expected_moment_point, places=2)
        
        # Düzgün yayılı yük
        moment_uniform = calculate_moment(self.load, self.length, "Düzgün Yayılı Yük")
        expected_moment_uniform = self.load * self.length**2 / 8
        self.assertAlmostEqual(moment_uniform, expected_moment_uniform, places=2)
        
        # Üçgen yayılı yük
        moment_triangular = calculate_moment(self.load, self.length, "Üçgen Yayılı Yük")
        expected_moment_triangular = self.load * self.length**2 / 12
        self.assertAlmostEqual(moment_triangular, expected_moment_triangular, places=2)
    
    def test_shear_calculation(self):
        """Kesme kuvveti hesaplama fonksiyonunu test et"""
        # Tekil yük
        result_point = calculate_point_loads(self.load, self.length)
        shear_point = result_point["shear"]
        expected_shear_point = self.load / 2
        self.assertAlmostEqual(shear_point, expected_shear_point, places=2)
        
        # Düzgün yayılı yük
        result_uniform = calculate_uniform_load(self.length, self.load)
        shear_uniform = result_uniform["shear"]
        expected_shear_uniform = self.load / 2
        self.assertAlmostEqual(shear_uniform, expected_shear_uniform, places=2)
        
        # Üçgen yayılı yük
        result_triangular = calculate_triangular_load(self.length, self.load)
        shear_triangular = result_triangular["shear"]
        expected_shear_triangular = self.load / 3
        self.assertAlmostEqual(shear_triangular, expected_shear_triangular, places=2)
    
    def test_max_deflection_calculation(self):
        """Maksimum sehim hesaplama fonksiyonunu test et"""
        # Elastisite modülü ve atalet momenti hesapla
        E = 30e9  # N/m²
        I = (self.width/100) * (self.height/100)**3 / 12  # m⁴
        
        # Tekil yük
        deflection_point = calculate_deflection(self.load, self.length, E, I)
        self.assertGreater(deflection_point, 0)
        
        # Düzgün yayılı yük
        deflection_uniform = calculate_deflection_uniform_load(self.load, self.length, E, I)
        self.assertGreater(deflection_uniform, 0)
        
        # Üçgen yayılı yük
        deflection_triangular = calculate_deflection_triangular_load(self.load, self.length, E, I)
        self.assertGreater(deflection_triangular, 0)
    
    def test_beam_analysis(self):
        """Kiriş analizi fonksiyonunu test et"""
        # Tekil yük için test
        results_point = calculate_beam_analysis(
            self.length, self.load, self.width, self.height, 
            self.concrete_class, "Tekil Yük"
        )
        
        # Beklenen değerler
        expected_moment = self.load * self.length / 4  # P*L/4
        expected_shear = self.load / 2  # P/2 (değiştirildi)
        
        # Sonuçları kontrol et
        self.assertAlmostEqual(results_point["moment"], expected_moment, places=2)
        self.assertAlmostEqual(results_point["shear"], expected_shear, places=2)
        self.assertGreater(results_point["max_deflection"], 0)
        
        # Düzgün yayılı yük için test
        # ...
    
    def test_beam_analysis_with_reinforcement(self):
        """Donatı hesabı ile kiriş analizi fonksiyonunu test et"""
        # Tekil yük
        results_point = calculate_beam_analysis(
            self.length, self.load, self.width, self.height, 
            self.concrete_class, "Tekil Yük", True  # with_reinforcement=True
        )
        
        self.assertIn("moment", results_point)
        self.assertIn("shear", results_point)
        self.assertIn("max_deflection", results_point)
        self.assertIn("distributions", results_point)
        self.assertIn("reinforcement", results_point)
        
        # Donatı hesabı sonuçlarını kontrol et
        self.assertIn("min_area", results_point["reinforcement"])
        self.assertIn("required_area", results_point["reinforcement"])
        self.assertIn("options", results_point["reinforcement"])
        
        self.assertGreater(results_point["reinforcement"]["required_area"], 0)
        self.assertGreaterEqual(results_point["reinforcement"]["required_area"], 
                              results_point["reinforcement"]["min_area"])
        self.assertGreater(len(results_point["reinforcement"]["options"]), 0)
    
    def test_invalid_load_type(self):
        """Geçersiz yük tipi için hata kontrolü"""
        with self.assertRaises(ValueError):
            calculate_beam_analysis(
                self.length, self.load, self.width, self.height, 
                self.concrete_class, "Geçersiz Yük Tipi", False
            )

if __name__ == '__main__':
    unittest.main()