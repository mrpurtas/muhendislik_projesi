import math

class TS500:
    """TS500 standardına göre sabitler ve hesaplamalar"""
    
    # Malzeme güvenlik katsayıları
    GAMMA_C = 1.5  # Beton
    GAMMA_S = 1.15  # Çelik
    
    # Beton sınıfları ve karakteristik dayanımları (MPa)
    CONCRETE_CLASSES = {
        "C20": 20, "C25": 25, "C30": 30, "C35": 35,
        "C40": 40, "C45": 45, "C50": 50
    }
    
    # Çelik sınıfları ve karakteristik dayanımları (MPa)
    STEEL_CLASSES = {
        "S220": 220,
        "S420": 420,
        "S500": 500
    }
    
    @staticmethod
    def calculate_fcd(fck):
        """Beton tasarım dayanımı"""
        return fck / TS500.GAMMA_C
    
    @staticmethod
    def calculate_fyd(fyk):
        """Çelik tasarım dayanımı"""
        return fyk / TS500.GAMMA_S
    
    @staticmethod
    def calculate_min_reinforcement_ratio(fck):
        """Minimum donatı oranı"""
        return max(0.8 / 1000, 0.233 * math.sqrt(fck) / 1000)

    @staticmethod
    def get_fck(concrete_class):
        """Beton sınıfına göre karakteristik basınç dayanımı"""
        return TS500.CONCRETE_CLASSES.get(concrete_class, 30)  # Varsayılan C30

    @staticmethod
    def calculate_min_reinforcement_area(width, height, concrete_class):
        """
        Minimum donatı alanını hesaplar.
        
        Args:
            width (float): Kiriş genişliği (m)
            height (float): Kiriş yüksekliği (m)
            concrete_class (str): Beton sınıfı
        
        Returns:
            float: Minimum donatı alanı (mm²)
        """
        # Beton sınıfına göre minimum donatı oranı
        min_reinforcement_ratio = {
            "C20": 0.0018,
            "C25": 0.0030,
            "C30": 0.0032,
            "C35": 0.0034,
            "C40": 0.0036,
            "C45": 0.0038,
            "C50": 0.0040
        }
        
        if concrete_class not in min_reinforcement_ratio:
            raise ValueError(f"Geçersiz beton sınıfı: {concrete_class}")
        
        # Kesit alanı (mm²)
        section_area = width * height * 1000000  # m² -> mm²
        
        # Minimum donatı alanı (mm²)
        min_area = section_area * min_reinforcement_ratio[concrete_class]
        
        return min_area

def calculate_reinforcement(moment, concrete_class, width, height, cover=0.05):
    """
    Betonarme donatı hesabı yapar
    
    Args:
        moment (float): Moment değeri (kNm)
        concrete_class (str): Beton sınıfı (C20, C25, C30, ...)
        width (float): Kesit genişliği (m)
        height (float): Kesit yüksekliği (m)
        cover (float): Paspayı (m), varsayılan 0.05m (5cm)
    
    Returns:
        dict: Donatı hesabı sonuçları
    """
    try:
        # Beton sınıfına göre karakteristik dayanımları al
        fck = TS500.get_fck(concrete_class)  # MPa
        fcd = TS500.calculate_fcd(fck)       # MPa
        fyk = 420  # S420 çeliği için (MPa)
        fyd = TS500.calculate_fyd(fyk)       # MPa
        
        # Etkin yükseklik (d) hesabı
        d = height - cover  # m
        
        # Boyutsuz moment hesabı
        Md = moment  # kNm
        K = Md / (width * d * d * fcd * 1000)  # kNm -> Nm için 1000 ile çarp
        
        # Donatı oranı hesabı
        if K > 0.85:  # Maksimum K değeri kontrolü
            raise ValueError("Moment değeri çok yüksek, kesit boyutlarını artırın!")
        
        # Donatı oranı hesabı
        ksi = 1 - math.sqrt(1 - 2*K)
        
        # Çekme donatısı alanı
        As = (0.85 * fcd * width * ksi * d) / fyd  # m²
        As_mm2 = As * 1000000  # m² -> mm²
        
        # Basınç donatısı hesabı
        As2_mm2 = 0
        if K > 0.38:  # Basınç donatısı gerekiyor
            # Basınç bölgesi sınır değeri
            ksi_limit = 0.85 * 0.85 / (0.85 + fyd/700)
            
            # Basınç donatısı hesabı
            delta_M = Md - 0.38 * width * d * d * fcd * 1000 / 1000  # kNm
            z = d - 0.4 * ksi_limit * d  # Kuvvet kolu
            As2_mm2 = (delta_M * 1000000) / (fyd * z)  # mm²
            
            # Çekme donatısı güncelleme
            As_mm2 = (0.38 * width * d * d * fcd * 1000 / fyd) * 1000000 + As2_mm2
        
        # Minimum donatı kontrolü - beton sınıfına göre hesaplanıyor
        min_As = TS500.calculate_min_reinforcement_area(width, height, concrete_class)
        required_As = max(As_mm2, min_As)
        
        # Donatı seçenekleri
        options = []
        
        # Standart donatı çapları
        diameters = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
        
        for diameter in diameters:
            # Tek bir donatının alanı
            area_single = math.pi * (diameter/2)**2  # mm²
            
            # Gerekli donatı sayısı
            count = math.ceil(required_As / area_single)
            
            # Toplam alan
            total_area = count * area_single
            
            # Minimum aralık kontrolü (en az donatı çapı kadar veya 2.5 cm)
            min_spacing = max(diameter, 25)  # mm
            max_count = int((width*1000 - 2*cover*1000) / min_spacing) + 1  # Paspayı
            
            if count <= max_count:
                options.append({
                    "diameter": diameter,
                    "count": count,
                    "area": total_area,
                    "spacing": (width*1000 - 2*cover*1000) / (count-1) if count > 1 else 0
                })
        
        # Basınç donatısı seçenekleri
        compression_options = []
        if As2_mm2 > 0:
            for diameter in diameters:
                # Tek bir donatının alanı
                area_single = math.pi * (diameter/2)**2  # mm²
                
                # Gerekli donatı sayısı
                count = math.ceil(As2_mm2 / area_single)
                
                # Toplam alan
                total_area = count * area_single
                
                compression_options.append({
                    "diameter": diameter,
                    "count": count,
                    "area": total_area
                })
        
        # Sonuçları döndür
        result = {
            "min_area": min_As,
            "required_area": required_As,
            "options": options
        }
        
        # Basınç donatısı varsa ekle
        if As2_mm2 > 0:
            result["compression_required_area"] = As2_mm2
            result["compression_options"] = compression_options
            result["has_compression_reinforcement"] = True
        else:
            result["has_compression_reinforcement"] = False
        
        return result
        
    except Exception as e:
        raise Exception(f"Donatı hesabı hatası: {str(e)}")

def get_reinforcement_options(required_area, width, effective_height, cover=0.05, stirrup_diameter=8):
    """
    Gerekli donatı alanına göre donatı seçeneklerini hesaplar.
    
    Args:
        required_area (float): Gerekli donatı alanı (mm²)
        width (float): Kiriş genişliği (m)
        effective_height (float): Etkin kiriş yüksekliği (m)
        cover (float): Paspayı (m), varsayılan 0.05m (5cm)
        stirrup_diameter (float): Etriye çapı (mm), varsayılan 8mm
    
    Returns:
        list: Donatı seçenekleri listesi
    """
    # Donatı çapları (mm)
    diameters = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
    
    # Donatı seçenekleri
    options = []
    
    # Minimum donatı aralığı (mm)
    min_spacing = 25  # mm
    
    # Maksimum donatı aralığı (mm)
    max_spacing = 200  # mm
    
    # Her çap için hesaplama yap
    for diameter in diameters:
        # Tek donatının alanı (mm²)
        single_bar_area = 3.14159 * (diameter/2)**2
        
        # Gerekli donatı sayısı
        required_count = required_area / single_bar_area
        
        # Yukarı yuvarlama
        count = int(required_count) + (1 if required_count > int(required_count) else 0)
        
        # En az 2 donatı olmalı
        count = max(2, count)
        
        # Toplam donatı alanı (mm²)
        total_area = count * single_bar_area
        
        # Donatı aralığı (mm)
        # Kiriş genişliği - 2 * (pas payı + etriye çapı) - count * çap
        clear_width = width * 1000 - 2 * (cover * 1000 + stirrup_diameter) - count * diameter
        
        # Donatılar arası boşluk
        spacing = clear_width / (count - 1) if count > 1 else 0
        
        # Donatı aralığı kontrolü
        if spacing < min_spacing and count > 2:
            continue  # Bu çap için donatı sığmıyor, bir sonraki çapa geç
        
        # Donatı seçeneğini ekle
        options.append({
            "diameter": diameter,
            "count": count,
            "area": total_area,
            "spacing": spacing
        })
    
    # Donatı seçeneklerini sırala (önce çapa göre, sonra adete göre)
    options.sort(key=lambda x: (x["diameter"], x["count"]))
    
    return options 