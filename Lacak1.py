import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import json

def get_location_coordinates(location_name):
    """
    Mendapatkan koordinat latitude dan longitude dari nama lokasi
    menggunakan Nominatim API (OpenStreetMap)
    """
    try:
        # Format location name untuk pencarian
        location_clean = location_name.split(',')[0].strip()
        
        # Gunakan Nominatim API
        url = f"https://nominatim.openstreetmap.org/search?q={location_clean}&format=json&limit=1"
        headers = {
            'User-Agent': 'PhoneNumberLocator/1.0 (your-email@example.com)'
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data and len(data) > 0:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return float(lat), float(lon)
        else:
            return None, None
            
    except Exception as e:
        print(f"Error mendapatkan koordinat: {e}")
        return None, None

def get_google_maps_link(lat, lon):
    """Membuat link Google Maps dari koordinat"""
    if lat and lon:
        return f"https://www.google.com/maps?q={lat},{lon}"
    return None

# Input nomor telepon
mobileNo = input("Masukkan Nomor HP : ")
mobileNo = phonenumbers.parse(mobileNo)

print("\n" + "="*50)
print("INFORMASI NOMOR TELEPON")
print("="*50)

# Mendapatkan Lokasi timezone
timezones = timezone.time_zones_for_number(mobileNo)
print(f"Zona Waktu: {list(timezones)}")

# Mendapatkan Provider
provider = carrier.name_for_number(mobileNo, "id")
print(f"Provider: {provider}")

# Mendapatkan Negara/Lokasi
location = geocoder.description_for_number(mobileNo, "id")
print(f"Lokasi: {location}")

# Mendapatkan koordinat lokasi
if location and location != "":
    print("\nMencari koordinat lokasi...")
    latitude, longitude = get_location_coordinates(location)
    
    if latitude and longitude:
        print(f"Koordinat: {latitude}, {longitude}")
        maps_link = get_google_maps_link(latitude, longitude)
        print(f"Link Google Maps: {maps_link}")
    else:
        print("Koordinat tidak ditemukan untuk lokasi tersebut")
else:
    print("Lokasi tidak ditemukan")

# Validasi sebuah nomor hp
print(f"\nValid Mobile Number: {phonenumbers.is_valid_number(mobileNo)}")

# Cek posibilitas sebuah nomor
print(f"Mengecek posibilitas sebuah nomor: {phonenumbers.is_possible_number(mobileNo)}")
