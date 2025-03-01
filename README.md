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

4. Dallar (Branch) ile Çalışma
# Yeni bir dal oluşturun
git checkout -b ozellik/harika-ozellik

# Çalışma bittiğinde ana dala geri dönün
git checkout main

# Daldaki değişiklikleri ana dala merge edin
git merge ozellik/harika-ozellik

5. Durumu Kontrol Etme
# Mevcut durum
git status

# Commit geçmişini satır satır özetle
git log --oneline


## Kullanım Kılavuzu

### Ana Ekran
Uygulamayı başlattığınızda ilk olarak **Ana Pencere** açılır. Burada kiriş analizi ve donatı hesabına dair temel parametreleri girebilirsiniz.

1. **Kiriş Uzunluğu (m)**: Kirişin toplam uzunluğunu giriniz.  
2. **Yük (kN)**: Uygulanan yük değerini giriniz.  
3. **Yük Tipi**: Tekil, düzgün yayılı veya üçgen yayılı yüklerden birini seçiniz.  
4. **Beton Sınıfı**: C20–C50 arası beton sınıfını seçiniz.  
5. **Kesit Boyutları (cm)**: Kirişin genişlik (**b**) ve yüksekliğini (**h**) giriniz.  
6. **Donatı Hesabı**: Seçili ise donatı hesabı da yapılır.

#### Butonlar
- **Hesapla**: Girilen parametrelerle kiriş analizini ve donatı hesabını yapar.  
- **Sıfırla**: Tüm girdileri ve sonuçları temizler.  
- **Ayarlar**: Grafik ve birim ayarlarını düzenleyebileceğiniz pencereyi açar.  
- **Donatı Hesabı**: Ayrı bir pencerede daha detaylı donatı hesabı ve donatı seçimi yapmanızı sağlar.

#### Sonuç Alanı
- Maksimum moment, kesme kuvveti ve sehim değerleri
- Hesaplandıysa donatı alanı bilgileri
- Toplam hesap süresi ve dosya kayıt bilgileri

#### Grafik Alanı
- Kesme kuvveti diyagramı
- Moment diyagramı
- Sehim diyagramı

---

### Donatı Hesabı Penceresi
- **Beton sınıfı**, **kesit boyutu** ve **hesaplanan moment** gibi bilgileri gösterir.  
- Farklı donatı çapları ve adetleri için toplam donatı alanını hesaplar.  
- Kullanıcı, uygun donatı detayını seçebilir.

---

### Ayarlar Penceresi
- **Koyu Tema**: Uygulamanın ve grafiklerin arka plan rengini koyu yapar.  
- **Izgara Çizgileri**: Grafikleri ızgara çizgileriyle görüntüler veya gizler.  
- **Birim Ayarları**: Uzunluk, yük vb. birimlerini değiştirmenize olanak tanır (örn. m, cm, mm).

---

## Proje Yapısı
Aşağıdaki görsel, uygulamanın temel klasör ve dosya yapısını göstermektedir:

![Proje Yapısı](https://github.com/user-attachments/assets/55176650-ea5d-4e0f-b139-afde4f1b8688)


---

## Teknik Detaylar

### Hesaplama Modülleri

- **beam_calculation.py**  
  Kiriş üzerindeki moment, kesme kuvveti ve sehim değerlerini hesaplar. Farklı mesnet koşulları ve yük tiplerini destekler.

- **load_types.py**  
  Tekil, düzgün yayılı ve üçgen yayılı yükler için özel fonksiyonlar içerir. Her yük tipi için moment ve kesme katsayılarını hesaplar.

- **reinforcement.py**  
  Betonarme donatı alanı hesabı yapar. Farklı beton dayanımları ve donatı çapları üzerinde hesaplama yapar.

- **file_io.py**  
  Hesaplama sonuçlarını CSV olarak kaydetme, grafiklerin PNG formatında çıktı alınması gibi fonksiyonlar içerir.

### Kullanılan Teknolojiler
- **Python 3.10+**  
- **PyQt6** (Kullanıcı arayüzü)  
- **Matplotlib** (Grafik çizimi)  
- **NumPy** (Sayısal hesaplamalar)  
- **Pytest** (Birim testleri)

---


## Katkıda Bulunma

1. Bu depoyu **fork** edin.  
2. Yeni bir dal (branch) oluşturun (örn. `git checkout -b yeni-ozellik`).  
3. Değişikliklerinizi yapın ve commit edin (örn. `git commit -am "Yeni özellik eklendi"`).  
4. Dalınızı uzak depoya gönderin (örn. `git push origin yeni-ozellik`).  
5. Bir **Pull Request** açarak yaptığınız değişikliklerin birleştirilmesini talep edin.








