import numpy as np
from src.core.calculations.load_types import calculate_uniform_load, calculate_triangular_load

def calculate_moment(load: float, length: float) -> float:
    """Tekil yük için basit moment hesabı."""
    return (load * length) / 4

def calculate_deflection(load: float, length: float, E: float, I: float) -> float:
    """Elastik sehim hesabı (Tekil yük ortada)."""
    return (load * length**3) / (48 * E * I)

def calculate_moment_diagram(load: float, length: float, x_values: np.ndarray) -> np.ndarray:
    """Moment diyagramı hesabı."""
    return (load * x_values/2) * (1 - x_values/length)

def calculate_shear_diagram(load: float, length: float, x_values: np.ndarray) -> np.ndarray:
    """Kesme kuvveti diyagramı hesabı."""
    return np.where(x_values < length/2, load/2, -load/2)

def calculate_deflection_diagram(load: float, length: float, E: float, I: float, x_values: np.ndarray) -> np.ndarray:
    """Sehim diyagramı hesabı."""
    return (load * x_values * (length**2 - x_values**2)) / (16 * E * I * 1e6)

def calculate_beam_analysis(length, load, width, height, concrete_class, load_type="Tekil Yük", calc_reinforcement=False):
    """Kiriş analizi için tüm hesaplamaları yapar."""
    # Atalet momenti
    I = (width * height**3) / 12
    
    # Elastisite modülü
    E = float(concrete_class[1:]) * 1000  # MPa
    
    # Yük tipine göre moment ve kesme kuvveti hesabı
    if load_type == "Tekil Yük":
        moment = calculate_moment(load, length)
        shear = load / 2
    elif load_type == "Düzgün Yayılı Yük":
        moment, shear = calculate_uniform_load(load, length)
    elif load_type == "Üçgen Yayılı Yük":
        moment, shear = calculate_triangular_load(load, length)
    else:
        moment = calculate_moment(load, length)
        shear = load / 2
    
    # Sehim hesabı
    max_deflection = calculate_deflection(load, length, E, I * 1e6)
    
    # X ekseni değerleri
    x = np.linspace(0, length, 100)
    
    # Diyagramları hesapla
    moment_diagram = calculate_moment_diagram(load, length, x)
    shear_diagram = calculate_shear_diagram(load, length, x)
    deflection_diagram = calculate_deflection_diagram(load, length, E, I * 1e6, x)
    
    # Donatı hesabı
    reinforcement_results = None
    if calc_reinforcement:
        from src.core.calculations.reinforcement import calculate_reinforcement
        reinforcement_results = calculate_reinforcement(moment, concrete_class, width, height)
    
    return {
        # Giriş parametrelerini de ekleyelim
        "length": length,
        "load": load,
        "width": width,
        "height": height,
        "concrete_class": concrete_class,
        
        # Hesaplama sonuçları
        "moment": moment,
        "shear": shear,
        "max_deflection": max_deflection,
        "I": I,
        "E": E,
        "x": x,
        "moment_diagram": moment_diagram,
        "shear_diagram": shear_diagram,
        "deflection_diagram": deflection_diagram,
        "reinforcement_results": reinforcement_results
    }