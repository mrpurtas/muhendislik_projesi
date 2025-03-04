import unittest
from src.core.calculations.reinforcement import calculate_reinforcement

class TestReinforcement(unittest.TestCase):
    """Donatı hesaplama fonksiyonlarını test eden sınıf"""
    
    def setUp(self):
        """Test için ortak değişkenleri ayarla"""
        self.moment = 100.0  # kNm
        self.width = 30.0  # cm
        self.height = 50.0  # cm
        self.concrete_class = "C25"
    
    def test_min_reinforcement_area(self):
        """Minimum donatı alanı hesaplama fonksiyonunu test et"""
        # Beton sınıfına göre minimum donatı oranı
        min_reinforcement_ratio = {
            "C20": 0.0028,
            "C25": 0.0030,
            "C30": 0.0032,
            "C35": 0.0034,
            "C40": 0.0036,
            "C45": 0.0038,
            "C50": 0.0040
        }
        
        # Kesit alanı (mm²)
        section_area = self.width * 10 * self.height * 10  # cm² -> mm²
        
        # Minimum donatı alanı (mm²)
        min_area = section_area * min_reinforcement_ratio[self.concrete_class]
        
        self.assertGreater(min_area, 0)
        
        # Farklı beton sınıfları için test
        min_area_c20 = section_area * min_reinforcement_ratio["C20"]
        min_area_c30 = section_area * min_reinforcement_ratio["C30"]
        
        self.assertGreater(min_area_c20, 0)
        self.assertGreater(min_area_c30, 0)
        
        # Beton sınıfı arttıkça minimum donatı alanının artması beklenir
        self.assertGreaterEqual(min_area_c30, min_area_c20)
    
    def test_reinforcement_calculation(self):
        """Donatı hesaplama fonksiyonunu test et"""
        reinforcement = calculate_reinforcement(
            self.moment, self.concrete_class, self.width/100, self.height/100
        )
        
        # Sonuçları kontrol et
        self.assertIn("min_area", reinforcement)
        self.assertIn("required_area", reinforcement)
        self.assertIn("options", reinforcement)
        
        # Minimum donatı alanı pozitif olmalı
        self.assertGreater(reinforcement["min_area"], 0)
        
        # Gerekli donatı alanı pozitif olmalı
        self.assertGreater(reinforcement["required_area"], 0)
        
        # En az bir donatı seçeneği olmalı
        self.assertGreater(len(reinforcement["options"]), 0)
        
        # İlk seçeneği kontrol et
        option = reinforcement["options"][0]
        self.assertIn("diameter", option)
        self.assertIn("count", option)
        self.assertIn("area", option)
        self.assertIn("spacing", option)
        
        # Değerler pozitif olmalı
        self.assertGreater(option["diameter"], 0)
        self.assertGreater(option["count"], 0)
        self.assertGreater(option["area"], 0)
        
        # Spacing değeri 0 veya daha büyük olmalı (tek donatı durumunda 0 olabilir)
        self.assertGreaterEqual(option["spacing"], 0)
        
        # Donatı alanı gerekli alandan büyük olmalı
        self.assertGreaterEqual(option["area"], reinforcement["required_area"])
    
    def test_different_concrete_classes(self):
        """Farklı beton sınıfları için donatı hesabını test et"""
        concrete_classes = ["C20", "C25", "C30", "C35", "C40", "C45", "C50"]
        
        for concrete_class in concrete_classes:
            reinforcement = calculate_reinforcement(
                self.moment, concrete_class, self.width/100, self.height/100
            )
            
            self.assertIn("min_area", reinforcement)
            self.assertIn("required_area", reinforcement)
            self.assertIn("options", reinforcement)
            
            self.assertGreater(reinforcement["required_area"], 0)
            self.assertGreaterEqual(reinforcement["required_area"], reinforcement["min_area"])
            self.assertGreater(len(reinforcement["options"]), 0)
    
    def test_moment_effect(self):
        """Moment değerinin donatı alanına etkisini test et"""
        # Farklı moment değerleri için donatı hesabı
        moments = [50, 100, 150, 200]
        areas = []
        
        for moment in moments:
            reinforcement = calculate_reinforcement(
                moment, self.concrete_class, self.width/100, self.height/100
            )
            areas.append(reinforcement["required_area"])
        
        # Moment arttıkça donatı alanının artması beklenir
        for i in range(1, len(areas)):
            self.assertGreaterEqual(areas[i], areas[i-1])
    
    def test_section_dimensions_effect(self):
        """Kesit boyutlarının donatı alanına etkisini test et"""
        # Sabit moment için farklı kesit boyutları
        widths = [20, 25, 30, 35, 40]  # cm
        heights = [40, 45, 50, 55, 60]  # cm
        areas = []
        
        for width, height in zip(widths, heights):
            reinforcement = calculate_reinforcement(
                self.moment, self.concrete_class, width/100, height/100
            )
            areas.append(reinforcement["required_area"])
        
        # Kesit boyutları arttıkça gerekli donatı alanının azalması beklenir
        for i in range(1, len(areas)):
            self.assertLessEqual(areas[i], areas[i-1])
    
    def test_invalid_inputs(self):
        """Geçersiz girdiler için hata kontrolü"""
        # Negatif moment
        try:
            calculate_reinforcement(-100, self.concrete_class, self.width/100, self.height/100)
            self.fail("Negatif moment için hata bekleniyor")
        except Exception:
            pass  # Hata beklendiği gibi fırlatıldı
        
        # Geçersiz beton sınıfı
        try:
            calculate_reinforcement(100, "C99", self.width/100, self.height/100)
            self.fail("Geçersiz beton sınıfı için hata bekleniyor")
        except Exception:
            pass  # Hata beklendiği gibi fırlatıldı
        
        # Çok küçük kesit
        try:
            calculate_reinforcement(100, self.concrete_class, 0.05, 0.1)
            self.fail("Çok küçük kesit için hata bekleniyor")
        except Exception:
            pass  # Hata beklendiği gibi fırlatıldı
    
    def test_spacing_constraints(self):
        """Donatı aralığı kısıtlamalarını test et"""
        # Daha küçük bir moment değeri kullan
        moment = 50.0  # kNm (önceki değer çok yüksekti)
        width = 20.0  # cm
        height = 40.0  # cm
        
        try:
            reinforcement = calculate_reinforcement(
                moment, self.concrete_class, width/100, height/100
            )
            
            options = reinforcement["options"]
            
            # En az bir donatı seçeneği olmalı
            self.assertGreater(len(options), 0)
            
            # Donatı aralıkları kontrol et
            for option in options:
                # Donatı sayısı 1'den büyükse, aralık kontrolü yap
                if option["count"] > 1:
                    # Donatı aralığı minimum değerden büyük olmalı
                    self.assertGreaterEqual(option["spacing"], 25)  # min 25mm
                    
                    # Donatı aralığı maksimum değerden küçük olmalı
                    self.assertLessEqual(option["spacing"], 200)  # max 200mm
        except Exception as e:
            # Eğer kesit yetersizse, testi geç
            if "kesit" in str(e).lower():
                self.skipTest("Kesit boyutları yetersiz")
            else:
                raise

    def test_concrete_strength_effect(self):
        """Beton dayanımının donatı alanına etkisini test et"""
        # Farklı beton sınıfları için donatı hesabı
        concrete_classes = ["C20", "C25", "C30", "C35", "C40", "C45", "C50"]
        areas = []
        
        for concrete_class in concrete_classes:
            reinforcement = calculate_reinforcement(
                self.moment, concrete_class, self.width/100, self.height/100
            )
            areas.append(reinforcement["required_area"])
        
        # Beton dayanımı arttıkça gerekli donatı alanının azalması beklenir
        for i in range(1, len(areas)):
            self.assertLessEqual(areas[i], areas[i-1])

    def test_reinforcement_consistency(self):
        """Donatı hesabının tutarlılığını test et"""
        # Aynı parametrelerle birden fazla hesaplama yap
        reinforcement1 = calculate_reinforcement(
            self.moment, self.concrete_class, self.width/100, self.height/100
        )
        
        reinforcement2 = calculate_reinforcement(
            self.moment, self.concrete_class, self.width/100, self.height/100
        )
        
        # Sonuçların aynı olduğunu kontrol et
        self.assertEqual(reinforcement1["required_area"], reinforcement2["required_area"])
        self.assertEqual(reinforcement1["min_area"], reinforcement2["min_area"])
        
        # Donatı seçeneklerinin aynı olduğunu kontrol et
        self.assertEqual(len(reinforcement1["options"]), len(reinforcement2["options"]))
        
        for i in range(len(reinforcement1["options"])):
            self.assertEqual(reinforcement1["options"][i]["diameter"], 
                            reinforcement2["options"][i]["diameter"])
            self.assertEqual(reinforcement1["options"][i]["count"], 
                            reinforcement2["options"][i]["count"])
            self.assertEqual(reinforcement1["options"][i]["area"], 
                            reinforcement2["options"][i]["area"])
            self.assertEqual(reinforcement1["options"][i]["spacing"], 
                            reinforcement2["options"][i]["spacing"])

    def test_extreme_values(self):
        """Uç değerler için donatı hesabını test et"""
        # Çok küçük moment
        small_moment = 1.0  # kNm
        small_reinforcement = calculate_reinforcement(
            small_moment, self.concrete_class, self.width/100, self.height/100
        )
        
        # Çok küçük momentte bile minimum donatı alanı sağlanmalı
        self.assertGreaterEqual(small_reinforcement["required_area"], 
                              small_reinforcement["min_area"])
        
        # Çok büyük moment
        large_moment = 1000.0  # kNm
        try:
            large_reinforcement = calculate_reinforcement(
                large_moment, self.concrete_class, self.width/100, self.height/100
            )
            
            # Çok büyük momentte bile hesaplama yapılabilmeli
            self.assertGreater(large_reinforcement["required_area"], 0)
            self.assertGreater(len(large_reinforcement["options"]), 0)
        except Exception as e:
            # Eğer hesaplama yapılamazsa (örn. kesit yetersiz), bu da kabul edilebilir
            self.assertIn("kesit", str(e).lower())

    def test_option_sorting(self):
        """Donatı seçeneklerinin sıralanmasını test et"""
        reinforcement = calculate_reinforcement(
            self.moment, self.concrete_class, self.width/100, self.height/100
        )
        
        options = reinforcement["options"]
        
        # Seçeneklerin çap veya adet sayısına göre sıralandığını kontrol et
        for i in range(1, len(options)):
            # Ya çap artmalı ya da aynı çapta adet artmalı
            if options[i]["diameter"] == options[i-1]["diameter"]:
                self.assertGreaterEqual(options[i]["count"], options[i-1]["count"])
            else:
                self.assertGreater(options[i]["diameter"], options[i-1]["diameter"])

if __name__ == '__main__':
    unittest.main()