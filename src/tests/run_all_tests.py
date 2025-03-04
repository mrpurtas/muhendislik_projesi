import unittest
import time
import sys
import os
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
from src.tests.test_beam_calculation import TestBeamCalculation
from src.tests.test_reinforcement import TestReinforcement
from src.tests.test_load_types import TestLoadTypes
from src.tests.test_integration import TestIntegration
from src.tests.test_performance import TestPerformance

# Colorama'yı başlat
init()

# Proje kök dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def print_header(text):
    """Renkli başlık yazdır"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

def print_success(text):
    """Başarı mesajı yazdır"""
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")

def print_error(text):
    """Hata mesajı yazdır"""
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")

def print_info(text):
    """Bilgi mesajı yazdır"""
    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")

class CustomTestResult(unittest.TextTestResult):
    """Özelleştirilmiş test sonuç sınıfı"""
    
    def startTest(self, test):
        super().startTest(test)
        test_name = self.getDescription(test)
        print(f"Çalıştırılıyor: {test_name}...", end=" ")
        sys.stdout.flush()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"{Fore.GREEN}BAŞARILI ✓{Style.RESET_ALL}")
    
    def addError(self, test, err):
        super().addError(test, err)
        print(f"{Fore.RED}HATA ✗{Style.RESET_ALL}")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"{Fore.RED}BAŞARISIZ ✗{Style.RESET_ALL}")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        print(f"{Fore.YELLOW}ATLANDI - {reason}{Style.RESET_ALL}")

class CustomTestRunner(unittest.TextTestRunner):
    """Özelleştirilmiş test çalıştırıcı sınıfı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resultclass = CustomTestResult

def run_all_tests():
    """Tüm testleri çalıştır"""
    # Test yükleyici oluştur
    loader = unittest.TestLoader()
    
    # Test süitini oluştur
    test_suite = unittest.TestSuite()
    
    # TestBeamCalculation sınıfındaki tüm testleri ekle
    test_suite.addTests(loader.loadTestsFromTestCase(TestBeamCalculation))
    
    # TestReinforcement sınıfındaki tüm testleri ekle
    test_suite.addTests(loader.loadTestsFromTestCase(TestReinforcement))
    
    # TestPerformance sınıfındaki tüm testleri ekle
    test_suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Test süitini çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

def run_performance_tests():
    """Performans testlerini çalıştır"""
    print_header("Performans Testleri Çalıştırılıyor")
    
    try:
        # Hesaplama performans testini çalıştır
        print_info("Hesaplama Performans Testi başlatılıyor...")
        TestPerformance.test_calculation_performance()
        print_success("Hesaplama Performans Testi tamamlandı.")
        
        # Donatı hesaplama performans testini çalıştır
        print_info("Donatı Hesaplama Performans Testi başlatılıyor...")
        TestPerformance.test_reinforcement_performance()
        print_success("Donatı Hesaplama Performans Testi tamamlandı.")
        
        return True
    except Exception as e:
        print_error(f"Performans testleri sırasında hata oluştu: {str(e)}")
        return False

def create_test_report(unit_result, perf_result, elapsed_time):
    """Test raporu oluştur"""
    report_path = "test_report.html"
    
    success_count = unit_result.testsRun - len(unit_result.failures) - len(unit_result.errors)
    success_rate = (success_count / unit_result.testsRun) * 100 if unit_result.testsRun > 0 else 0
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MHA Test Raporu</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #3498db; }}
            .success {{ color: green; }}
            .error {{ color: red; }}
            .info {{ color: orange; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>Mühendislik Hesaplama Aracı (MHA) Test Raporu</h1>
        <p>Oluşturulma Tarihi: {time.strftime("%d.%m.%Y %H:%M:%S")}</p>
        <p>Toplam Test Süresi: {elapsed_time:.2f} saniye</p>
        
        <h2>Birim Test Sonuçları</h2>
        <p>Çalıştırılan Test Sayısı: {unit_result.testsRun}</p>
        <p class="success">Başarılı Test Sayısı: {success_count} ({success_rate:.1f}%)</p>
        <p class="error">Başarısız Test Sayısı: {len(unit_result.failures)}</p>
        <p class="error">Hatalı Test Sayısı: {len(unit_result.errors)}</p>
        
        <h2>Performans Test Sonuçları</h2>
        <p class="{'success' if perf_result else 'error'}">
            Performans Testleri: {'Başarılı' if perf_result else 'Başarısız'}
        </p>
        
        <h2>Test Detayları</h2>
        <table>
            <tr>
                <th>Test Modülü</th>
                <th>Durum</th>
            </tr>
            <tr>
                <td>Kiriş Hesaplama Testleri</td>
                <td class="{'success' if not any(test_id.startswith('test_beam_calculation') for test_id, _ in unit_result.failures + unit_result.errors) else 'error'}">
                    {'Başarılı' if not any(test_id.startswith('test_beam_calculation') for test_id, _ in unit_result.failures + unit_result.errors) else 'Başarısız'}
                </td>
            </tr>
            <tr>
                <td>Donatı Hesaplama Testleri</td>
                <td class="{'success' if not any(test_id.startswith('test_reinforcement') for test_id, _ in unit_result.failures + unit_result.errors) else 'error'}">
                    {'Başarılı' if not any(test_id.startswith('test_reinforcement') for test_id, _ in unit_result.failures + unit_result.errors) else 'Başarısız'}
                </td>
            </tr>
            <tr>
                <td>Yük Tipleri Testleri</td>
                <td class="{'success' if not any(test_id.startswith('test_load_types') for test_id, _ in unit_result.failures + unit_result.errors) else 'error'}">
                    {'Başarılı' if not any(test_id.startswith('test_load_types') for test_id, _ in unit_result.failures + unit_result.errors) else 'Başarısız'}
                </td>
            </tr>
            <tr>
                <td>Entegrasyon Testleri</td>
                <td class="{'success' if not any(test_id.startswith('test_integration') for test_id, _ in unit_result.failures + unit_result.errors) else 'error'}">
                    {'Başarılı' if not any(test_id.startswith('test_integration') for test_id, _ in unit_result.failures + unit_result.errors) else 'Başarısız'}
                </td>
            </tr>
            <tr>
                <td>Performans Testleri</td>
                <td class="{'success' if perf_result else 'error'}">
                    {'Başarılı' if perf_result else 'Başarısız'}
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print_info(f"Test raporu oluşturuldu: {os.path.abspath(report_path)}")

if __name__ == "__main__":
    start_time = time.time()
    
    # Tüm testleri çalıştır
    result = run_all_tests()
    
    # Toplam süreyi hesapla
    elapsed_time = time.time() - start_time
    
    print_header("Tüm Testler Tamamlandı")
    print(f"Toplam Süre: {elapsed_time:.2f} saniye")
    
    # Test sonuçlarını göster
    print("\nTest Sonuçları:")
    print(f"Çalıştırılan test sayısı: {result.testsRun}")
    print(f"Başarılı test sayısı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Başarısız test sayısı: {len(result.failures)}")
    print(f"Hata veren test sayısı: {len(result.errors)}")
    
    # Başarısız testleri göster
    if result.failures:
        print("\nBaşarısız Testler:")
        for failure in result.failures:
            print(f"- {failure[0]}")
    
    # Hata veren testleri göster
    if result.errors:
        print("\nHata Veren Testler:")
        for error in result.errors:
            print(f"- {error[0]}")
    
    # Çıkış kodu ayarla (başarısız test varsa 1, yoksa 0)
    sys.exit(len(result.failures) + len(result.errors))
    
    # Performans testlerini çalıştır
    perf_test_result = run_performance_tests()
    
    # Test raporu oluştur
    create_test_report(result, perf_test_result, elapsed_time) 