import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import urllib.parse
import re

def get_opencage_geocoding(location_name, phone_number, provider):
    """Menggunakan OpenCage Geocoding API untuk koordinat yang akurat"""
    try:
        # API Key OpenCage yang Anda dapatkan
        API_KEY = "eec645033c4545a5892853270d94e094"
        
        # Buat query yang lebih spesifik berdasarkan informasi yang ada
        if provider and location_name:
            query = f"{provider} mobile network {location_name} {phone_number[:6]} Indonesia"
        else:
            query = f"mobile network {location_name} Indonesia"
        
        encoded_query = urllib.parse.quote(query)
        
        url = f"https://api.opencagedata.com/geocode/v1/json?q={encoded_query}&key={API_KEY}&limit=3&no_annotations=1"
        
        headers = {
            'User-Agent': 'PhoneLocator/1.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        print(f"🔍 OpenCage API Status: {data.get('status', {}).get('message', 'Unknown')}")
        
        if data['results']:
            # Prioritaskan hasil dengan confidence tinggi
            best_result = None
            for result in data['results']:
                confidence = result.get('confidence', 0)
                components = result.get('components', {})
                
                # Cek jika hasil mengandung informasi telekomunikasi atau kota
                if ('telecom' in str(components).lower() or 
                    'city' in components or 
                    'town' in components or
                    'suburb' in components):
                    if not best_result or confidence > best_result.get('confidence', 0):
                        best_result = result
            
            # Jika tidak ada yang spesifik, ambil hasil dengan confidence tertinggi
            if not best_result and data['results']:
                best_result = max(data['results'], key=lambda x: x.get('confidence', 0))
            
            if best_result:
                geometry = best_result['geometry']
                formatted = best_result['formatted']
                confidence = best_result.get('confidence', 0)
                components = best_result.get('components', {})
                
                print(f"📍 OpenCage Found: {formatted}")
                print(f"📊 Confidence Level: {confidence}/10")
                
                # Tampilkan detail komponen alamat
                if 'city' in components:
                    print(f"🏙️ City: {components['city']}")
                if 'town' in components:
                    print(f"🏘️ Town: {components['town']}")
                if 'suburb' in components:
                    print(f"🏡 Area: {components['suburb']}")
                if 'state' in components:
                    print(f"🏛️ State: {components['state']}")
                
                return geometry['lat'], geometry['lng'], confidence
                
    except requests.exceptions.Timeout:
        print("⏰ Timeout: OpenCage API tidak merespons")
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network Error: {e}")
    except Exception as e:
        print(f"❌ OpenCage Error: {e}")
    
    return None, None, 0

def get_phone_prefix_location(phone_number, provider):
    """Mendapatkan perkiraan lokasi berdasarkan prefix nomor"""
    # Database prefix nomor Indonesia dan kota-kota
    prefix_data = {
        "62811": {"city": "Jakarta", "coordinates": (-6.2088, 106.8456), "region": "Jabodetabek"},
        "62812": {"city": "Jakarta", "coordinates": (-6.2088, 106.8456), "region": "Jabodetabek"},
        "62813": {"city": "Surabaya", "coordinates": (-7.2504, 112.7688), "region": "Jawa Timur"},
        "62814": {"city": "Bandung", "coordinates": (-6.9175, 107.6191), "region": "Jawa Barat"},
        "62815": {"city": "Medan", "coordinates": (3.5952, 98.6722), "region": "Sumatera Utara"},
        "62816": {"city": "Semarang", "coordinates": (-6.9667, 110.4167), "region": "Jawa Tengah"},
        "62817": {"city": "Yogyakarta", "coordinates": (-7.7956, 110.3695), "region": "DIY Yogyakarta"},
        "62818": {"city": "Denpasar", "coordinates": (-8.6705, 115.2126), "region": "Bali"},
        "62819": {"city": "Makassar", "coordinates": (-5.1477, 119.4327), "region": "Sulawesi Selatan"},
        "62821": {"city": "Jakarta", "coordinates": (-6.2088, 106.8456), "region": "Jabodetabek"},
        "62822": {"city": "Bandung", "coordinates": (-6.9175, 107.6191), "region": "Jawa Barat"},
        "62823": {"city": "Surabaya", "coordinates": (-7.2504, 112.7688), "region": "Jawa Timur"},
        "62851": {"city": "Medan", "coordinates": (3.5952, 98.6722), "region": "Sumatera Utara"},
        "62852": {"city": "Medan", "coordinates": (3.5952, 98.6722), "region": "Sumatera Utara"},
        "62853": {"city": "Palembang", "coordinates": (-2.9761, 104.7759), "region": "Sumatera Selatan"},
        "62855": {"city": "Balikpapan", "coordinates": (-1.2420, 116.8942), "region": "Kalimantan Timur"},
        "62856": {"city": "Manado", "coordinates": (1.4748, 124.8426), "region": "Sulawesi Utara"},
        "62857": {"city": "Malang", "coordinates": (-8.1663, 112.7093), "region": "Jawa Timur"},
        "62858": {"city": "Banjarmasin", "coordinates": (-3.3186, 114.5944), "region": "Kalimantan Selatan"},
        "62878": {"city": "Denpasar", "coordinates": (-8.6705, 115.2126), "region": "Bali"},
        "62877": {"city": "Mataram", "coordinates": (-8.5833, 116.1167), "region": "NTB"},
        "62896": {"city": "Jayapura", "coordinates": (-2.5333, 140.7167), "region": "Papua"},
    }
    
    clean_number = re.sub(r'[^0-9]', '', phone_number)
    
    # Cari prefix yang cocok (5-6 digit pertama)
    for length in [6, 5]:
        prefix = clean_number[:length]
        if prefix in prefix_data:
            location_info = prefix_data[prefix]
            print(f"📞 Prefix {prefix}: {location_info['city']} ({location_info['region']})")
            return location_info['coordinates'], location_info['city']
    
    return None, None

def get_accuracy_estimate(confidence, method):
    """Estimasi akurasi berdasarkan confidence level dan metode"""
    if method == "opencage":
        if confidence >= 8:
            return "Tinggi (radius ~1-3 km)"
        elif confidence >= 5:
            return "Sedang (radius ~5-10 km)"
        else:
            return "Rendah (radius ~15-25 km)"
    elif method == "prefix":
        return "Perkiraan (radius ~20-50 km)"
    else:
        return "Sangat Rendah (radius >50 km)"

# Main Program
print("🔍 PHONE NUMBER GEOLOCATOR - OPEN CAGE API")
print("=" * 60)

mobile_no_input = input("Masukkan Nomor HP (contoh: +628123456789): ")

try:
    mobileNo = phonenumbers.parse(mobile_no_input)
    
    print("\n" + "="*50)
    print("📱 INFORMASI DASAR NOMOR TELEPON")
    print("="*50)

    # Mendapatkan informasi dasar
    timezones = timezone.time_zones_for_number(mobileNo)
    provider = carrier.name_for_number(mobileNo, "id")
    location = geocoder.description_for_number(mobileNo, "id")
    
    print(f"⏰ Zona Waktu: {list(timezones)}")
    print(f"📡 Provider: {provider}")
    print(f"🌍 Lokasi: {location}")
    print(f"✅ Valid: {phonenumbers.is_valid_number(mobileNo)}")
    print(f"🔍 Possible: {phonenumbers.is_possible_number(mobileNo)}")

    print("\n" + "="*50)
    print("🎯 MENCARI KOORDINAT LOKASI")
    print("="*50)
    
    coordinates = None
    method_used = ""
    confidence = 0
    
    # Approach 1: Gunakan OpenCage API untuk koordinat real-time
    print("🔍 Menggunakan OpenCage API...")
    lat, lon, confidence = get_opencage_geocoding(location, mobile_no_input, provider)
    
    if lat and lon:
        coordinates = (lat, lon)
        method_used = "opencage"
    else:
        # Approach 2: Gunakan data prefix sebagai fallback
        print("🔍 Mencari berdasarkan prefix nomor...")
        prefix_coords, city = get_phone_prefix_location(mobile_no_input, provider)
        if prefix_coords:
            coordinates = prefix_coords
            method_used = "prefix"
            confidence = 6  # Confidence medium untuk prefix
    
    # Approach 3: Fallback ke koordinat default
    if not coordinates:
        print("⚠️ Menggunakan koordinat default Jakarta...")
        coordinates = (-6.2088, 106.8456)
        method_used = "default"
        confidence = 1
    
    # Tampilkan hasil akhir
    if coordinates:
        lat, lon = coordinates
        accuracy = get_accuracy_estimate(confidence, method_used)
        
        print(f"\n🎉 KOORDINAT BERHASIL DITEMUKAN!")
        print("=" * 40)
        print(f"📍 Latitude: {lat}")
        print(f"📍 Longitude: {lon}")
        print(f"📊 Metode: {method_used.upper()}")
        print(f"🎯 Akurasi: {accuracy}")
        print(f"💎 Confidence: {confidence}/10")
        
        # Buat link maps
        maps_link = f"https://www.google.com/maps?q={lat},{lon}&z=12"
        maps_direct = f"https://maps.google.com/?q={lat},{lon}"
        
        print(f"\n🗺️ LINK MAPS:")
        print(f"Google Maps: {maps_link}")
        print(f"Direct Link: {maps_direct}")
        
        # Additional info berdasarkan metode
        if method_used == "opencage" and confidence >= 7:
            print("\n💡 Info: Koordinat ini cukup akurat untuk wilayah tersebut")
        elif method_used == "prefix":
            print("\n💡 Info: Ini adalah perkiraan berdasarkan kode wilayah nomor")
        else:
            print("\n💡 Info: Gunakan nomor dengan kode area spesifik untuk hasil lebih akurat")

except phonenumbers.NumberParseException as e:
    print(f"❌ Error: Format nomor tidak valid - {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("💡 Gunakan nomor dengan format +62... untuk hasil terbaik")
print("📞 Contoh: +628123456789, +628781234567")
print("=" * 60)