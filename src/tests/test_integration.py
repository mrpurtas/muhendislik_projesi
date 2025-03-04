import unittest
import numpy as np
from src.core.calculations.beam_calculation import calculate_beam_analysis
from src.core.calculations.reinforcement import calculate_reinforcement

class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri için sınıf"""
    
    def setUp(self):
        """Test için ortak değişkenleri ayarla"""
        self.length = 5.0  # m
        self.load = 10.0  # kN
        self.width = 30.0  # cm
        self.height = 50.0  # cm
        self.concrete_class = "C25"
    
    def test_beam_analysis_with_reinforcement_integration(self):
        """Kiriş analizi ve donatı hesabı entegrasyonunu test et"""
        # Kiriş analizi yap
        results = calculate_beam_analysis(
            self.length, self.load, self.width, self.height, 
            self.concrete_class, "Tekil Yük", True
        )
        
        # Donatı hesabı sonuçlarını kontrol et
        self.assertIn("reinforcement", results)
        self.assertIn("min_area", results["reinforcement"])
        self.assertIn("required_area", results["reinforcement"])
        self.assertIn("options", results["reinforcement"])
        
        # Doğrudan donatı hesabı yap
        direct_reinforcement = calculate_reinforcement(
            results["moment"], self.width, self.height, self.concrete_class
        )
        
        # İki hesaplama sonucunun aynı olduğunu kontrol et
        self.assertAlmostEqual(
            results["reinforcement"]["required_area"],
            direct_reinforcement["required_area"],
            places=2
        )
        
        self.assertAlmostEqual(
            results["reinforcement"]["min_area"],
            direct_reinforcement["min_area"],
            places=2
        )
    
    def test_different_load_types_integration(self):
        """Farklı yük tipleri için entegrasyon testi"""
        load_types = ["Tekil Yük", "Düzgün Yayılı Yük", "Üçgen Yayılı Yük"]
        
        for load_type in load_types:
            # Kiriş analizi yap
            results = calculate_beam_analysis(
                self.length, self.load, self.width, self.height, 
                self.concrete_class, load_type, True
            )
            
            # Temel sonuçları kontrol et
            self.assertIn("moment", results)
            self.assertIn("shear", results)
            self.assertIn("max_deflection", results)
            self.assertIn("distributions", results)
            self.assertIn("reinforcement", results)
            
            # Dağılım verilerini kontrol et
            self.assertIn("x", results["distributions"])
            self.assertIn("moment", results["distributions"])
            self.assertIn("shear", results["distributions"])
            self.assertIn("deflection", results["distributions"])
            
            # Dağılım verilerinin boyutlarını kontrol et
            x_points = results["distributions"]["x"]
            moment_dist = results["distributions"]["moment"]
            shear_dist = results["distributions"]["shear"]
            deflection_dist = results["distributions"]["deflection"]
            
            self.assertEqual(len(moment_dist), len(x_points))
            self.assertEqual(len(shear_dist), len(x_points))
            self.assertEqual(len(deflection_dist), len(x_points))
            
            # Maksimum moment değerini kontrol et
            max_moment_dist = np.max(moment_dist)
            self.assertAlmostEqual(max_moment_dist, results["moment"], places=2)
            
            # Maksimum kesme kuvveti değerini kontrol et
            max_shear_dist = np.max(np.abs(shear_dist))
            self.assertAlmostEqual(max_shear_dist, results["shear"], places=2)
    
    def test_different_concrete_classes_integration(self):
        """Farklı beton sınıfları için entegrasyon testi"""
        concrete_classes = ["C20", "C25", "C30", "C35", "C40", "C45", "C50"]
        
        for concrete_class in concrete_classes:
            # Kiriş analizi yap
            results = calculate_beam_analysis(
                self.length, self.load, self.width, self.height, 
                concrete_class, "Tekil Yük", True
            )
            
            # Temel sonuçları kontrol et
            self.assertIn("moment", results)
            self.assertIn("shear", results)
            self.assertIn("max_deflection", results)
            self.assertIn("distributions", results)
            self.assertIn("reinforcement", results)
            
            # Donatı hesabı sonuçlarını kontrol et
            self.assertIn("min_area", results["reinforcement"])
            self.assertIn("required_area", results["reinforcement"])
            self.assertIn("options", results["reinforcement"])
            
            self.assertGreater(results["reinforcement"]["required_area"], 0)
            self.assertGreaterEqual(results["reinforcement"]["required_area"], 
                                  results["reinforcement"]["min_area"])
            self.assertGreater(len(results["reinforcement"]["options"]), 0)

if __name__ == '__main__':
    unittest.main() 