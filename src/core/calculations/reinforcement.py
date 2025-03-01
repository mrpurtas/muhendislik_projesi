import math

def calculate_reinforcement(moment, concrete_class, width, height, cover=3.0):
    """Betonarme kiriş için donatı hesabı"""
    # Beton dayanımı (MPa)
    fck = float(concrete_class[1:])
    
    # Çelik dayanımı (MPa)
    fyk = 420  # S420 çeliği
    
    # Etkin yükseklik
    d = height - cover
    
    # Moment kapasitesi katsayısı
    k = moment * 1e6 / (width * d**2 * fck)
    
    # Donatı oranı (yaklaşık formül)
    if k <= 0.15:
        rho = 0.85 * fck / fyk * (1 - math.sqrt(1 - 2 * k / 0.85))
    else:
        rho = 0.004  # Minimum donatı oranı
    
    # Donatı alanı
    As = rho * width * d
    
    # Donatı çapı ve sayısı
    diameters = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
    selected_bars = []
    
    for d in diameters:
        area_per_bar = 3.14159 * (d/2)**2
        num_bars = math.ceil(As / area_per_bar)
        if num_bars <= 8:  # Makul sayıda donatı
            selected_bars.append((d, num_bars))
    
    return {
        "required_area": As,
        "options": selected_bars
    } 