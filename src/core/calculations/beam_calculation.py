import numpy as np
from .load_types import (
    calculate_uniform_load, calculate_triangular_load, calculate_point_loads,
    calculate_moment_distribution_uniform_load, calculate_shear_distribution_uniform_load,
    calculate_deflection_distribution_uniform_load,
    calculate_moment_distribution_triangular_load, calculate_shear_distribution_triangular_load,
    calculate_deflection_distribution_triangular_load
)
from .reinforcement import calculate_reinforcement as calc_reinforcement

def calculate_moment(load: float, length: float, load_type="Tekil Yük") -> float:
    """Basit kiriş için moment hesabı
    
    Args:
        load (float): Yük değeri (kN)
        length (float): Kiriş uzunluğu (m)
        load_type (str): Yük tipi
    
    Returns:
        float: Maksimum moment değeri (kNm)
    """
    print(f"Moment hesaplanıyor: Yük={load}, Uzunluk={length}, Tip={load_type}")
    
    if load_type == "Düzgün Yayılı Yük":
        moment = (load * length**2) / 8
    elif load_type == "Üçgen Yayılı Yük":
        moment = (load * length**2) / 12
    else:  # Tekil Yük
        moment = (load * length) / 4
    
    print(f"Hesaplanan moment: {moment} kNm")
    return moment

def calculate_deflection(load: float, length: float, E: float, I: float) -> float:
    """
    Elastik sehim hesabı (Tekil yük ortada).
    
    Args:
        load (float): Yük değeri (kN)
        length (float): Kiriş uzunluğu (m)
        E (float): Elastisite modülü (N/m²)
        I (float): Atalet momenti (m⁴)
    
    Returns:
        float: Maksimum sehim değeri (m)
    """
    # Yük kN'dan N'a dönüştürülüyor (1 kN = 1000 N)
    load_N = load * 1000
    
    # Sehim hesabı (m cinsinden)
    deflection = (load_N * length**3) / (48 * E * I)
    
    return deflection  # m cinsinden

def calculate_moment_diagram(load: float, length: float, x_values: np.ndarray) -> np.ndarray:
    """Moment diyagramı hesabı."""
    return (load * x_values/2) * (1 - x_values/length)

def calculate_shear_diagram(load: float, length: float, x_values: np.ndarray) -> np.ndarray:
    """Kesme kuvveti diyagramı hesabı."""
    return np.where(x_values < length/2, load/2, -load/2)

def calculate_deflection_diagram(load: float, length: float, E: float, I: float, x_values: np.ndarray) -> np.ndarray:
    """Sehim diyagramı hesabı."""
    # Yük kN'dan N'a dönüştürülüyor (1 kN = 1000 N)
    load_N = load * 1000
    
    # Metre cinsinden hesaplama yapılıyor
    deflection_m = (load_N * x_values * (length**2 - x_values**2)) / (16 * E * I)
    # Milimetre cinsine dönüştürülüyor (1 m = 1000 mm)
    return deflection_m * 1000

def calculate_beam_analysis(length, load, width, height, concrete_class, load_type="Tekil Yük", with_reinforcement=False):
    """Kiriş analizi hesaplamalarını yapar"""
    try:
        print(f"Kiriş analizi başlatılıyor: Yük tipi={load_type}")
        
        # Moment hesabı
        moment = calculate_moment(load, length, load_type)
        
        # Elastisite modülü hesabı
        E = calculate_elasticity_modulus(concrete_class)
        
        # Atalet momenti hesabı
        I = (width/100) * (height/100)**3 / 12  # cm -> m dönüşümü
        
        # Kesme kuvveti ve sehim hesabı
        if load_type == "Düzgün Yayılı Yük":
            shear = load * length / 2
            max_deflection = calculate_deflection_uniform_load(load, length, E, I)
        elif load_type == "Üçgen Yayılı Yük":
            shear = load * length / 2
            max_deflection = calculate_deflection_triangular_load(load, length, E, I)
        else:  # Tekil Yük
            shear = load / 2
            max_deflection = calculate_deflection(load, length, E, I)
        
        # Dağılım verilerini hesapla
        x_values = np.linspace(0, length, 100)
        
        # Yük tipine göre dağılım hesapla
        if load_type == "Düzgün Yayılı Yük":
            moment_distribution = calculate_moment_distribution_uniform_load(load, length, x_values)
            shear_distribution = calculate_shear_distribution_uniform_load(load, length, x_values)
            deflection_distribution = calculate_deflection_distribution_uniform_load(load, length, E, I, x_values)
        elif load_type == "Üçgen Yayılı Yük":
            moment_distribution = calculate_moment_distribution_triangular_load(load, length, x_values)
            shear_distribution = calculate_shear_distribution_triangular_load(load, length, x_values)
            deflection_distribution = calculate_deflection_distribution_triangular_load(load, length, E, I, x_values)
        else:  # Tekil Yük
            moment_distribution = calculate_moment_diagram(load, length, x_values)
            shear_distribution = calculate_shear_diagram(load, length, x_values)
            deflection_distribution = calculate_deflection_diagram(load, length, E, I, x_values)
        
        # Sonuçları döndür
        results = {
            "moment": moment,
            "shear": shear,
            "max_deflection": max_deflection,
            "elasticity_modulus": E/1e9,  # GPa cinsinden
            "x_values": x_values,
            "moment_distribution": moment_distribution,
            "shear_distribution": shear_distribution,
            "deflection_distribution": deflection_distribution,
            "load_type": load_type
        }
        
        # Donatı hesabı isteniyorsa ekle
        if with_reinforcement:
            reinforcement = calc_reinforcement(moment, concrete_class, width/100, height/100)
            results["reinforcement"] = reinforcement
        
        return results
        
    except Exception as e:
        print(f"Kiriş analizi hatası: {str(e)}")
        raise

def calculate_deflection_uniform_load(load, length, E, I):
    """
    Düzgün yayılı yük için maksimum sehim hesabı
    
    Args:
        load (float): Yük değeri (kN/m)
        length (float): Kiriş uzunluğu (m)
        E (float): Elastisite modülü (N/m²)
        I (float): Atalet momenti (m⁴)
    
    Returns:
        float: Maksimum sehim değeri (m)
    """
    # Yük kN/m'den N/m'ye dönüştürülüyor (1 kN/m = 1000 N/m)
    load_N_per_m = load * 1000
    
    # Sehim hesabı - I parametresi fonksiyona geçirilen değeri kullanır
    return (5 * load_N_per_m * length**4) / (384 * E * I)

def calculate_deflection_triangular_load(load, length, E, I):
    """
    Üçgen yayılı yük için maksimum sehim hesabı
    
    Args:
        load (float): Maksimum yük değeri (kN/m)
        length (float): Kiriş uzunluğu (m)
        E (float): Elastisite modülü (N/m²)
        I (float): Atalet momenti (m⁴)
    
    Returns:
        float: Maksimum sehim değeri (m)
    """
    # Yük kN/m'den N/m'ye dönüştürülüyor (1 kN/m = 1000 N/m)
    load_N_per_m = load * 1000
    
    # Sehim hesabı - Düzeltilmiş formül
    return (load_N_per_m * length**4) / (120 * E * I)

def calculate_elasticity_modulus(concrete_class):
    """
    Beton sınıfına göre elastisite modülünü hesaplar
    
    Args:
        concrete_class (str): Beton sınıfı (örn. "C25", "C30", "C35", vb.)
    
    Returns:
        float: Elastisite modülü (N/m²)
    """
    try:
        # Beton sınıfından karakteristik basınç dayanımını çıkar (MPa)
        if concrete_class.startswith("C"):
            fck = float(concrete_class[1:])
        else:
            fck = 30.0
        
        # Eurocode 2'ye göre elastisite modülü hesabı
        E = 22000 * (fck/10)**0.3 * 1e6  # N/m² cinsinden
        
        print(f"Elastisite modülü: {E/1e9:.2f} GPa")
        return E
    
    except Exception as e:
        print(f"Elastisite modülü hesaplama hatası: {str(e)}")
        # Hata durumunda varsayılan değer döndür
        return 30e9  # Varsayılan değer: 30 GPa