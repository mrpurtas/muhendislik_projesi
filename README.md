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
<img width="600" alt="Ekran Resmi 2025-03-02 00 44 46" src="https://github.com/user-attachments/assets/55176650-ea5d-4e0f-b139-afde4f1b8688" />


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


# Mevcut klasöre gidin
cd muhendislik_projesi

# Tüm dosyaları ekleyin

git init
git add .

# Commit'i yapın
git commit -m "İlk commit: Mühendislik projesi"

# Yeni uzak depoyu ekleyin
git remote add origin https://github.com/mrpurtas/muhendislik_projesi.git

# Değişiklikleri push edin
git push -u origin main

#Değişiklikleri Çekmek (Pull)

# Ana branch'a geçin
git checkout main

# Uzak depodaki son değişiklikleri çekin
git pull origin main

# Git kullanıcı bilgilerinizi ayarlayın
git config --global user.name "Adınız Soyadınız"
git config --global user.email "email@example.com"
