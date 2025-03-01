def calculate_uniform_load(load_per_meter, length):
    """Düzgün yayılı yük için hesaplamalar"""
    moment = (load_per_meter * length**2) / 8
    shear = (load_per_meter * length) / 2
    return moment, shear

def calculate_triangular_load(max_load, length):
    """Üçgen yayılı yük için hesaplamalar"""
    moment = (max_load * length**2) / 12
    shear = (max_load * length) / 3
    return moment, shear 