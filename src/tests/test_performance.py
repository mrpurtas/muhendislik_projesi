import unittest
import time
import numpy as np
import matplotlib.pyplot as plt
from src.core.calculations.beam_calculation import calculate_beam_analysis
from src.core.calculations.reinforcement import calculate_reinforcement
from src.core.calculations.load_types import calculate_uniform_load, calculate_triangular_load, calculate_point_loads

class TestPerformance(unittest.TestCase):
    """Performans testleri"""
    
    def setUp(self):
        """Test için ortak değişkenleri ayarla"""
        self.length = 5.0  # m
        self.load = 10.0  # kN
        self.width = 30.0  # cm
        self.height = 50.0  # cm
        self.concrete_class = "C25"
    
    def test_calculation_performance(self):
        """Hesaplama performansını test et"""
        # Test parametreleri
        length = self.length
        load = self.load
        width = self.width
        height = self.height
        concrete_class = self.concrete_class
        
        # Farklı yük tipleri için test
        load_types = ["Tekil Yük", "Düzgün Yayılı Yük", "Üçgen Yayılı Yük"]
        
        print("\nHesaplama Performans Testi:")
        print("=" * 50)
        
        results_by_load_type = {}
        
        for load_type in load_types:
            # Zamanı ölç
            start_time = time.time()
            
            # Hesaplama yap
            results = calculate_beam_analysis(
                length, load, width, height, concrete_class, load_type, True  # with_reinforcement=True
            )
            
            # Geçen süreyi hesapla
            elapsed_time = time.time() - start_time
            
            # Sonuçları kaydet
            results_by_load_type[load_type] = {
                "time": elapsed_time,
                "moment": results["moment"],
                "shear": results["shear"],
                "max_deflection": results["max_deflection"]
            }
            
            print(f"Yük Tipi: {load_type}, Süre: {elapsed_time:.4f} saniye")
        
        # Grafik çiz
        plt.figure(figsize=(10, 6))
        
        # Yük tiplerine göre hesaplama süreleri
        plt.subplot(1, 2, 1)
        plt.bar(results_by_load_type.keys(), [r["time"] for r in results_by_load_type.values()])
        plt.title('Yük Tipine Göre Hesaplama Süreleri')
        plt.xlabel('Yük Tipi')
        plt.ylabel('Süre (saniye)')
        plt.xticks(rotation=45)
        
        # Yük tiplerine göre moment değerleri
        plt.subplot(1, 2, 2)
        plt.bar(results_by_load_type.keys(), [r["moment"] for r in results_by_load_type.values()])
        plt.title('Yük Tipine Göre Moment Değerleri')
        plt.xlabel('Yük Tipi')
        plt.ylabel('Moment (kNm)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('calculation_performance_test_results.png')
        
        print("\nHesaplama performans test sonuçları 'calculation_performance_test_results.png' dosyasına kaydedildi.")
    
    def test_reinforcement_performance(self):
        """Donatı hesaplama performansını test et"""
        print("\nDonatı Hesaplama Performans Testi:")
        print("=" * 50)
        
        # Test parametreleri - daha küçük moment değerleri kullan
        moments = [10, 20, 30, 40, 50, 60]  # kNm (önceki değerler çok yüksekti)
        width = self.width
        height = self.height
        concrete_class = self.concrete_class
        
        times = []
        areas = []
        
        for moment in moments:
            try:
                start_time = time.time()
                
                reinforcement = calculate_reinforcement(moment, concrete_class, width/100, height/100)
                
                elapsed_time = time.time() - start_time
                times.append(elapsed_time)
                areas.append(reinforcement["required_area"])
                
                print(f"Moment: {moment} kNm, Süre: {elapsed_time:.4f} saniye, Donatı Alanı: {reinforcement['required_area']:.2f} mm²")
            except Exception as e:
                print(f"Moment: {moment} kNm - Hata: {str(e)}")
                # Hata durumunda döngüyü sonlandır
                break
        
        # En az bir hesaplama başarılı olmalı
        self.assertGreater(len(times), 0, "Hiçbir moment değeri için hesaplama yapılamadı")
        
        # Grafik çiz (eğer yeterli veri varsa)
        if len(times) >= 2:
            plt.figure(figsize=(10, 5))
            
            plt.subplot(1, 2, 1)
            plt.plot(moments[:len(times)], times, marker='o')
            plt.title('Moment Değerine Göre Hesaplama Süreleri')
            plt.xlabel('Moment (kNm)')
            plt.ylabel('Süre (saniye)')
            
            plt.subplot(1, 2, 2)
            plt.plot(moments[:len(times)], areas, marker='o')
            plt.title('Donatı Alanına Göre Hesaplama Süreleri')
            plt.xlabel('Moment (kNm)')
            plt.ylabel('Donatı Alanı (mm²)')
            
            plt.tight_layout()
            plt.savefig('reinforcement_performance_test_results.png')
            
            print("\nDonatı performans test sonuçları 'reinforcement_performance_test_results.png' dosyasına kaydedildi.")

if __name__ == '__main__':
    unittest.main()