# 🏗️ Mühendislik Hesaplama Aracı (MHA)



## 📋 İçindekiler
- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Proje Yapısı](#-proje-yapısı)
- [Kullanım Kılavuzu](#-kullanım-kılavuzu)
- [Testler](#-testler)
- [Katkıda Bulunma](#-katkıda-bulunma)

---

## 🚀 Özellikler
- **Kiriş Analizi:**
  - Eğilme Momenti Hesaplama
  - Kesme Kuvveti Diyagramları
  - Elastik Sehim Analizi
- **Parametrik Tasarım:**
  - 50+ Kesit Boyutu
  - 10 Beton Sınıfı (C20-C50)
 - 5 Yük Kombinasyonu
- **Görsel Çıktılar:**
  - Etkileşimli Moment/Kesme Grafikleri
  - PDF Rapor Üretimi


---

## 🔧 Kurulum

### Ön Koşullar
- Python 3.10+
- pip paket yöneticisi

### Adım Adım Kurulum
1. **Depoyu Klonlayın:**
   ```bash
   git clone https://github.com/kullaniciadiniz/muhendislik_projesi.git
   cd muhendislik_projesi

2. **Sanal Ortam Oluşturun ve Aktif Edin:**

# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

3. **Bağımlılıkları Yükleyin:**
pip install -r requirements.txt

4. **Uygulamayı Başlatın:**
python -m src.app.main



## 📂 Proje Yapısı

# Proje Yapısı

muhendislik_projesi/
├── data/                        # Örnek veri dosyaları
├── outputs/                     # Hesaplama çıktıları
│   ├── graphs/                  # Otomatik kaydedilen grafikler (PNG/PDF)
│   └── reports/                 # Üretilen raporlar (CSV/Excel)
│
├── src/                        # Kaynak kodları
│   ├── app/                    # GUI ve ana uygulama
│   │   ├── ui/                 # Kullanıcı arayüzü bileşenleri
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py           # Ana pencere
│   │   │   ├── reinforcement_dialog.py  # Donatı hesabı penceresi
│   │   │   └── settings_dialog.py       # Ayarlar penceresi
│   │   ├── __init__.py
│   │   └── main.py             # Uygulama başlangıç noktası
│   │
│   ├── core/                   # Hesaplama motoru
│   │   ├── calculations/       # Mühendislik algoritmaları
│   │   │   ├── __init__.py
│   │   │   ├── beam_calculation.py    # Kiriş hesaplamaları
│   │   │   ├── load_types.py         # Yük kombinasyonları
│   │   │   └── reinforcement.py      # Donatı optimizasyonu
│   │   │
│   │   ├── utils/              # Yardımcı fonksiyonlar
│   │   │   ├── __init__.py
│   │   │   └── file_io.py      # CSV/Excel okuma-yazma
│   │   │
│   │   └── __init__.py
│   │
│   └── tests/                  # Unit testler
│       ├── __init__.py
│       └── test_beam_calculation.py  # Kiriş test senaryoları
│
├── .gitignore                  # Git tarafından ignore edilecekler
├── README.md                   # Proje dokümantasyonu
└── requirements.txt            # Bağımlılıklar

### Dosya Açıklamaları

##Uygulama Modülleri (src/app/)

main.py: Uygulamanın başlangıç noktası, ana pencereyi başlatır.
ui/main_window.py: Ana pencere sınıfı, kullanıcı arayüzünü ve hesaplama işlemlerini yönetir.
ui/reinforcement_dialog.py: Donatı hesabı için ayrı bir pencere sunar.
ui/settings_dialog.py: Uygulama ayarlarını değiştirmek için bir pencere sunar.

##Çekirdek Hesaplama Modülleri (src/core/calculations/)
beam_calculation.py: Kiriş analizi için temel hesaplamaları içerir (moment, kesme kuvveti, sehim).
load_types.py: Farklı yük tipleri için hesaplama fonksiyonları (tekil, düzgün yayılı, üçgen yayılı).
reinforcement.py: Betonarme donatı hesabı için fonksiyonlar.

##Yardımcı Modüller (src/core/utils/)
file_io.py: Dosya işlemleri için fonksiyonlar (CSV kaydetme, grafik kaydetme).
Test Modülleri (src/tests/)
test_beam_calculation.py: Kiriş hesaplamalarını test etmek için birim testler.

##Çıktı Dosyaları
outputs/graphs/: Kaydedilen grafik dosyaları (.png formatında)
outputs/reports/: Hesaplama sonuçlarını içeren CSV raporları


## 👥 Katkıda Bulunma

Forklayın ve depoyu klonlayın

Yeni bir branch oluşturun: git checkout -b feature/benim-ozelligim

Değişiklikleri commit edin: git commit -m 'Yeni özellik: ...'

Push işlemi yapın: git push origin feature/benim-ozelligim

Pull Request açın
