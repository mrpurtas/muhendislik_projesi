import numpy as np

def calculate_uniform_load(length, total_load, E=None, I=None):
    """Düzgün yayılı yük için hesaplamalar"""
    # Birim uzunluk başına yük (kN/m)
    q = total_load / length
    
    # Maksimum moment (kNm)
    max_moment = q * length**2 / 8
    
    # Maksimum kesme kuvveti (kN)
    max_shear = q * length / 2
    
    # Varsayılan değerler, eğer parametreler belirtilmemişse
    if E is None:
        E = 32000000  # Beton elastisite modülü (kN/m²)
    if I is None:
        I = 0.0001  # Atalet momenti (m⁴) - varsayılan değer
    
    # Maksimum sehim (m)
    max_deflection = 5 * q * length**4 / (384 * E * I)
    
    return {
        "moment": max_moment,
        "shear": max_shear,
        "deflection": max_deflection
    }

def calculate_triangular_load(length, max_load, E=None, I=None):
    """Üçgen yayılı yük için hesaplamalar"""
    # Birim uzunluk başına maksimum yük (kN/m)
    q_max = max_load / length
    
    # Maksimum moment (kNm)
    max_moment = q_max * length**2 / 12
    
    # Maksimum kesme kuvveti (kN)
    max_shear = q_max * length / 3
    
    # Varsayılan değerler, eğer parametreler belirtilmemişse
    if E is None:
        E = 32000000  # Beton elastisite modülü (kN/m²)
    if I is None:
        I = 0.0001  # Atalet momenti (m⁴) - varsayılan değer
    
    # Maksimum sehim (m)
    max_deflection = q_max * length**4 / (120 * E * I)
    
    return {
        "moment": max_moment,
        "shear": max_shear,
        "deflection": max_deflection
    }

def calculate_point_loads(loads, length, E=None, I=None):
    """
    Tekil yük veya yükler için hesaplamalar
    
    Args:
        loads: Tekil yük değeri (float) veya [(konum, yük), ...] şeklinde yük listesi
        length (float): Kiriş uzunluğu (m)
        E (float, optional): Elastisite modülü (kN/m²), belirtilmezse varsayılan değer kullanılır
        I (float, optional): Atalet momenti (m⁴), belirtilmezse varsayılan değer kullanılır
    
    Returns:
        dict: Hesaplama sonuçları
    """
    # Varsayılan değerler, eğer parametreler belirtilmemişse
    if E is None:
        E = 32000000  # Beton elastisite modülü (kN/m²)
    if I is None:
        I = 0.0001  # Atalet momenti (m⁴) - varsayılan değer
    
    # Tekil yük (kN) veya yük listesi kontrolü
    if isinstance(loads, (int, float)):
        # Tek bir yük değeri verilmişse, ortada bir yük olarak kabul et
        P = loads
        
        # Maksimum moment (kNm) - ortada tekil yük için
        max_moment = P * length / 4
        
        # Maksimum kesme kuvveti (kN)
        max_shear = P / 2
        
        # Maksimum sehim (m)
        max_deflection = P * length**3 / (48 * E * I)
        
        return {
            "moment": max_moment,
            "shear": max_shear,
            "deflection": max_deflection
        }
    else:
        # Birden fazla yük için hesaplama
        # Moment ve kesme için x noktaları
        x = np.linspace(0, length, 100)
        moments = np.zeros_like(x)
        shears = np.zeros_like(x)
        
        for pos, P in loads:
            # Her yük için moment ve kesme dağılımı
            moments += P * (length - pos) * x / length
            shears += np.where(x < pos, P, 0)
        
        # Maksimum değerler
        max_moment = np.max(moments)
        max_shear = np.max(np.abs(shears))
        
        # Maksimum sehim (m)
        max_deflection = max([P * pos * (length - pos)**2 * (3*length - pos) / (48 * E * I * length)
                             for pos, P in loads])
        
        return {
            "moment": max_moment,
            "shear": max_shear,
            "deflection": max_deflection,
            "moment_distribution": moments,
            "shear_distribution": shears,
            "x_points": x
        }

def calculate_moment_distribution_uniform_load(load, length, x_points):
    """Düzgün yayılı yük için moment dağılımı"""
    moment_distribution = []
    for x in x_points:
        moment = (load * x * (length - x)) / 2
        moment_distribution.append(moment)
    return moment_distribution

def calculate_shear_distribution_uniform_load(load, length, x_points):
    """Düzgün yayılı yük için kesme kuvveti dağılımı"""
    shear_distribution = []
    for x in x_points:
        shear = load * (length/2 - x)
        shear_distribution.append(shear)
    return shear_distribution

def calculate_deflection_distribution_uniform_load(load, length, E, I, x_points):
    """
    Düzgün yayılı yük için sehim dağılımı
    
    Args:
        load (float): Yük değeri (kN/m)
        length (float): Kiriş uzunluğu (m)
        E (float): Elastisite modülü (N/m²)
        I (float): Atalet momenti (m⁴)
        x_points (array): Kiriş boyunca noktalar (m)
    
    Returns:
        array: Sehim değerleri (m)
    """
    # Yük kN/m'den N/m'ye dönüştürülüyor (1 kN/m = 1000 N/m)
    load_N_per_m = load * 1000
    
    deflection_distribution = []
    for x in x_points:
        # Düzgün yayılı yük için sehim formülü
        deflection = (load_N_per_m * x * (length**3 - 2*length*x**2 + x**3)) / (24 * E * I)
        deflection_distribution.append(deflection)
    
    return deflection_distribution

def calculate_moment_distribution_triangular_load(load, length, x_points):
    """Üçgen yayılı yük için moment dağılımı"""
    moment_distribution = []
    for x in x_points:
        moment = (load * x**2 * (3*length - 2*x)) / (6 * length)
        moment_distribution.append(moment)
    return moment_distribution

def calculate_shear_distribution_triangular_load(load, length, x_points):
    """Üçgen yayılı yük için kesme kuvveti dağılımı"""
    shear_distribution = []
    for x in x_points:
        shear = (load * (length - x)**2) / (2 * length)
        shear_distribution.append(shear)
    return shear_distribution

def calculate_deflection_distribution_triangular_load(load, length, E, I, x_points):
    """
    Üçgen yayılı yük için sehim dağılımı
    
    Args:
        load (float): Maksimum yük değeri (kN/m)
        length (float): Kiriş uzunluğu (m)
        E (float): Elastisite modülü (N/m²)
        I (float): Atalet momenti (m⁴)
        x_points (array): Kiriş boyunca noktalar (m)
    
    Returns:
        array: Sehim değerleri (m)
    """
    # Yük kN/m'den N/m'ye dönüştürülüyor (1 kN/m = 1000 N/m)
    load_N_per_m = load * 1000
    
    deflection_distribution = []
    for x in x_points:
        # Üçgen yayılı yük için sehim formülü - length terimi paydadan kaldırıldı
        deflection = (load_N_per_m * x**2 * (10*length**3 - 10*length**2*x + 5*length*x**2 - x**3)) / (120 * E * I)
        deflection_distribution.append(deflection)
    
    return deflection_distribution 