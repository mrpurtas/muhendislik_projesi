# 🏗️ Mühendislik Hesaplama Aracı (MHA)

Mühendislik Hesaplama Aracı (MHA), kirişlerin yapısal analizinden betonarme donatı hesabına kadar pek çok mühendislik hesabını otomatikleştiren ve kullanıcıya görsel çıktılar sunan bir masaüstü uygulamasıdır.

---

## 📋 İçindekiler
1. [Özellikler](#özellikler)  
2. [Kurulum](#kurulum)  
3. [Git İşlemleri](#git-işlemleri)  
4. [Kullanım Kılavuzu](#kullanım-kılavuzu)  
5. [Proje Yapısı](#proje-yapısı)  
6. [Teknik Detaylar](#teknik-detaylar)  
8. [Katkıda Bulunma](#katkıda-bulunma)  

---

## 🚀 Özellikler

### Kiriş Analizi
- Eğilme momenti hesaplama  
- Kesme kuvveti diyagramları  
- Elastik sehim analizi  
- Farklı yük tipleri (tekil, düzgün yayılı, üçgen yayılı)

### Parametrik Tasarım
- 50+ farklı kesit boyutu seçeneği  
- 10 farklı beton sınıfı (C20–C50)  
- 5 farklı yük kombinasyonu

### Betonarme Tasarım
- Donatı hesabı (beton sınıfları C20–C50)  
- Kesit boyutları optimizasyonu

### Görsel Çıktılar
- Etkileşimli moment, kesme ve sehim diyagramları  
- PNG formatında grafik kaydetme  
- CSV raporu oluşturma  
- PDF rapor üretimi

---

## 🔧 Kurulum

### Ön Koşullar
- **Python** 3.10+  
- **pip** paket yöneticisi  
- **Git** (sürüm kontrolü için)

### Adım Adım Kurulum

1. **Projeyi Klonlayın:**
   
git clone https://github.com/kullaniciadiniz/muhendislik_projesi.git
cd muhendislik_projesi

3. **Sanal Ortam Oluşturun ve Aktif Edin
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

4. **Bağımlılıkları Yükleyin:
pip install -r requirements.txt

5. **Uygulamayı Başlatın:
python -m src.app.main

🔄 Git İşlemleri
# Git kullanıcı bilgilerinizi ayarlayın
git config --global user.name "Adınız Soyadınız"
git config --global user.email "email@example.com"

1. İlk Kez Projeyi İndirme (Clone)
git clone https://github.com/kullaniciadiniz/muhendislik_projesi.git

2. Güncellemeleri Alma (Pull)
# Ana branch'a geçin
git checkout main

# Uzak depodaki son değişiklikleri çekin
git pull origin main

3. Değişiklikleri Gönderme (Push)
# Değişiklikleri ekleyip commit'leyin
git add .
git commit -m "Değişiklik mesajı"

# Uzak repoya gönderin
git push -u origin main