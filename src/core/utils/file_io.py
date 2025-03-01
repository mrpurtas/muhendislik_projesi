import csv

def save_to_csv(data: list, filename: str):
    """Veriyi CSV dosyasına kaydeder."""
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)