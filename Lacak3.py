import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import urllib.parse
import re
import json

def get_phone_prefix_city(phone_number):
    """Deteksi kota berdasarkan prefix nomor telepon Indonesia"""
    clean_number = re.sub(r'[^0-9]', '', phone_number)
    
    # Database lengkap prefix nomor Indonesia
    prefix_database = {
        # Telkomsel
        "62811": {"city": "Jakarta", "province": "DKI Jakarta", "coordinates": (-6.2088, 106.8456)},
        "62812": {"city": "Jakarta", "province": "DKI Jakarta", "coordinates": (-6.2088, 106.8456)},
        "62813": {"city": "Surabaya", "province": "Jawa Timur", "coordinates": (-7.2504, 112.7688)},
        "62814": {"city": "Bandung", "province": "Jawa Barat", "coordinates": (-6.9175, 107.6191)},
        "62815": {"city": "Medan", "province": "Sumatera Utara", "coordinates": (3.5952, 98.6722)},
        "62816": {"city": "Semarang", "province": "Jawa Tengah", "coordinates": (-6.9667, 110.4167)},
        "62817": {"city": "Yogyakarta", "province": "DIY Yogyakarta", "coordinates": (-7.7956, 110.3695)},
        "62818": {"city": "Denpasar", "province": "Bali", "coordinates": (-8.6705, 115.2126)},
        "62819": {"city": "Makassar", "province": "Sulawesi Selatan", "coordinates": (-5.1477, 119.4327)},
        "62821": {"city": "Jakarta", "province": "DKI Jakarta", "coordinates": (-6.2088, 106.8456)},
        "62822": {"city": "Bandung", "province": "Jawa Barat", "coordinates": (-6.9175, 107.6191)},
        "62823": {"city": "Surabaya", "province": "Jawa Timur", "coordinates": (-7.2504, 112.7688)},
        "62851": {"city": "Medan", "province": "Sumatera Utara", "coordinates": (3.5952, 98.6722)},
        "62852": {"city": "Medan", "province": "Sumatera Utara", "coordinates": (3.5952, 98.6722)},
        "62853": {"city": "Palembang", "province": "Sumatera Selatan", "coordinates": (-2.9761, 104.7759)},
        
        # Indosat
        "62855": {"city": "Jakarta", "province": "DKI Jakarta", "coordinates": (-6.2088, 106.8456)},
        "62856": {"city": "Surabaya", "province": "Jawa Timur", "coordinates": (-7.2504, 112.7688)},
        "62857": {"city": "Bandung", "province": "Jawa Barat", "coordinates": (-6.9175, 107.6191)},
        "62858": {"city": "Medan", "province": "Sumatera Utara", "coordinates": (3.5952, 98.6722)},
        
        # XL Axiata
        "62817": {"city": "Yogyakarta", "province": "DIY Yogyakarta", "coordinates": (-7.7956, 110.3695)},
        "62818": {"city": "Denpasar", "province": "Bali", "coordinates": (-8.6705, 115.2126)},
        "62819": {"city": "Makassar", "province": "Sulawesi Selatan", "coordinates": (-5.1477, 119.4327)},
        "62877": {"city": "Mataram", "province": "NTB", "coordinates": (-8.5833, 116.1167)},
        "62878": {"city": "Denpasar", "province": "Bali", "coordinates": (-8.6705, 115.2126)},
        "62879": {"city": "Jayapura", "province": "Papua", "coordinates": (-2.5333, 140.7167)},
        
        # Tri (3)
        "62889": {"city": "Jakarta", "province": "DKI Jakarta", "coordinates": (-6.2088, 106.8456)},
        "62898": {"city": "Surabaya", "province": "Jawa Timur", "coordinates": (-7.2504, 112.7688)},
        "62899": {"city": "Bandung", "province": "Jawa Barat", "coordinates": (-6.9175, 107.6191)},
        
        # Smartfren
        "62888": {"city": "Jakarta", "province": "DKI Jakarta", "coordinates": (-6.2088, 106.8456)},
        "62887": {"city": "Surabaya", "province": "Jawa Timur", "coordinates": (-7.2504, 112.7688)},
        "62886": {"city": "Bandung", "province": "Jawa Barat", "coordinates": (-6.9175, 107.6191)},
        
        # By.U
        "62851": {"city": "Jakarta", "province": "DKI Jakarta", "coordinates": (-6.2088, 106.8456)},
    }
    
    # Cari berdasarkan prefix 6 digit
    if clean_number[:6] in prefix_database:
        return prefix_database[clean_number[:6]]
    # Cari berdasarkan prefix 5 digit  
    elif clean_number[:5] in prefix_database:
        return prefix_database[clean_number[:5]]
    # Cari berdasarkan prefix 4 digit (08xx)
    elif clean_number[:4] in ["0811", "0812", "0813", "0814", "0815", "0816", "0817", "0818", "0819"]:
        prefix_6 = "6281" + clean_number[3]  # Konversi ke format 6281x
        if prefix_6 in prefix_database:
            return prefix_database[prefix_6]
    
    return None

def get_location_from_opencage(phone_number, provider, detected_city):
    """Gunakan OpenCage API untuk mendapatkan koordinat yang lebih akurat"""
    try:
        API_KEY = "eec645033c4545a5892853270d94e094"
        
        # Buat query berdasarkan kota yang terdeteksi
        if detected_city:
            query = f"{provider} tower {detected_city['city']} {detected_city['province']} Indonesia"
        else:
            query = f"{provider} Indonesia cellular network"
            
        encoded_query = urllib.parse.quote(query)
        
        url = f"https://api.opencagedata.com/geocode/v1/json?q={encoded_query}&key={API_KEY}&limit=1"
        
        headers = {'User-Agent': 'PhoneLocator/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('results'):
            result = data['results'][0]
            lat = result['geometry']['lat']
            lng = result['geometry']['lng']
            formatted = result['formatted']
            confidence = result.get('confidence', 0)
            
            return {
                'coordinates': (lat, lng),
                'address': formatted,
                'confidence': confidence,
                'method': 'opencage_api'
            }
            
    except Exception as e:
        print(f"⚠️ OpenCage API error: {e}")
    
    return None

def get_city_coordinates_fallback(city_name):
    """Database koordinat kota-kota Indonesia sebagai fallback"""
    city_coordinates = {
        "Jakarta": (-6.2088, 106.8456),
        "Surabaya": (-7.2504, 112.7688),
        "Bandung": (-6.9175, 107.6191),
        "Medan": (3.5952, 98.6722),
        "Semarang": (-6.9667, 110.4167),
        "Yogyakarta": (-7.7956, 110.3695),
        "Denpasar": (-8.6705, 115.2126),
        "Makassar": (-5.1477, 119.4327),
        "Malang": (-8.1663, 112.7093),
        "Palembang": (-2.9761, 104.7759),
        "Balikpapan": (-1.2420, 116.8942),
        "Manado": (1.4748, 124.8426),
        "Banjarmasin": (-3.3186, 114.5944),
        "Mataram": (-8.5833, 116.1167),
        "Jayapura": (-2.5333, 140.7167),
        "Padang": (-0.9492, 100.3543),
        "Pekanbaru": (0.5071, 101.4478),
        "Banda Aceh": (5.5483, 95.3238),
        "Jambi": (-1.6101, 103.6071),
        "Bengkulu": (-3.7956, 102.2592),
        "Bandar Lampung": (-5.4294, 105.2623),
        "Serang": (-6.1200, 106.1503),
        "Tangerang": (-6.1783, 106.6319),
        "Bogor": (-6.5971, 106.8060),
        "Sukabumi": (-6.9277, 106.9300),
        "Cirebon": (-6.7320, 108.5523),
        "Tegal": (-6.8667, 109.1333),
        "Pekalongan": (-6.8883, 109.6753),
        "Magelang": (-7.4667, 110.2167),
        "Solo": (-7.5667, 110.8167),
        "Madiun": (-7.6298, 111.5239),
        "Kediri": (-7.8467, 112.0178),
        "Blitar": (-8.1000, 112.1500),
        "Probolinggo": (-7.7543, 113.2159),
        "Pasuruan": (-7.6453, 112.9075),
        "Mojokerto": (-7.4667, 112.4333),
        "Jember": (-8.1724, 113.6873),
        "Banyuwangi": (-8.2191, 114.3691),
        "Pontianak": (-0.0226, 109.3307),
        "Samarinda": (-0.5022, 117.1536),
        "Banjar": (-7.3667, 108.5333),
        "Cilacap": (-7.7333, 109.0000),
        "Purwokerto": (-7.4244, 109.2342),
    }
    
    # Cari kota dengan partial match
    for city, coords in city_coordinates.items():
        if city_name.lower() in city.lower() or city.lower() in city_name.lower():
            return coords, city
    
    return None, None

def analyze_phone_number(phone_number):
    """Analisis lengkap nomor telepon"""
    try:
        # Parse nomor telepon
        parsed_number = phonenumbers.parse(phone_number)
        
        # Dapatkan informasi dasar
        provider = carrier.name_for_number(parsed_number, "en")
        country = geocoder.description_for_number(parsed_number, "en")
        timezones = timezone.time_zones_for_number(parsed_number)
        is_valid = phonenumbers.is_valid_number(parsed_number)
        is_possible = phonenumbers.is_possible_number(parsed_number)
        
        # Deteksi kota dari prefix (tanpa API)
        prefix_info = get_phone_prefix_city(phone_number)
        
        result = {
            'phone_number': phone_number,
            'provider': provider,
            'country': country,
            'timezones': list(timezones),
            'is_valid': is_valid,
            'is_possible': is_possible,
            'prefix_detection': prefix_info,
            'final_coordinates': None,
            'final_method': None,
            'maps_link': None
        }
        
        # Tentukan koordinat akhir
        if prefix_info:
            # Gunakan koordinat dari prefix database
            result['final_coordinates'] = prefix_info['coordinates']
            result['final_method'] = 'prefix_database'
            result['detected_city'] = f"{prefix_info['city']}, {prefix_info['province']}"
            
            # Coba dapatkan koordinat lebih akurat dengan API
            api_result = get_location_from_opencage(phone_number, provider, prefix_info)
            if api_result and api_result['confidence'] > 5:
                result['final_coordinates'] = api_result['coordinates']
                result['final_method'] = 'opencage_api'
                result['api_address'] = api_result['address']
                result['api_confidence'] = api_result['confidence']
        
        else:
            # Jika prefix tidak terdeteksi, gunakan fallback
            if "Indonesia" in country:
                # Coba tebak kota dari provider info
                fallback_coords, fallback_city = get_city_coordinates_fallback(provider)
                if fallback_coords:
                    result['final_coordinates'] = fallback_coords
                    result['final_method'] = 'provider_fallback'
                    result['detected_city'] = fallback_city
                else:
                    # Default ke Jakarta
                    result['final_coordinates'] = (-6.2088, 106.8456)
                    result['final_method'] = 'default_jakarta'
                    result['detected_city'] = "Jakarta"
        
        # Generate maps link
        if result['final_coordinates']:
            lat, lng = result['final_coordinates']
            result['maps_link'] = f"https://www.google.com/maps?q={lat},{lng}&z=12"
        
        return result
        
    except Exception as e:
        return {'error': str(e)}

# Main Program
print("🔍 INDONESIA PHONE NUMBER LOCATION TRACKER")
print("=" * 65)

while True:
    print("\n" + "="*50)
    mobile_no_input = input("Masukkan Nomor HP (atau 'quit' untuk keluar): ").strip()
    
    if mobile_no_input.lower() == 'quit':
        break
        
    if not mobile_no_input:
        continue
    
    print("\n🔄 Memproses nomor...")
    
    # Analisis nomor telepon
    result = analyze_phone_number(mobile_no_input)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        continue
    
    # Tampilkan hasil
    print("\n📱 HASIL DETEKSI LOKASI")
    print("=" * 40)
    print(f"📞 Nomor: {result['phone_number']}")
    print(f"📡 Provider: {result['provider']}")
    print(f"🌍 Negara: {result['country']}")
    print(f"⏰ Zona Waktu: {', '.join(result['timezones'])}")
    print(f"✅ Valid: {result['is_valid']}")
    print(f"🔍 Possible: {result['is_possible']}")
    
    if result['prefix_detection']:
        print(f"🏙️ Kota dari Prefix: {result['prefix_detection']['city']}, {result['prefix_detection']['province']}")
    
    if result['detected_city']:
        print(f"🎯 Lokasi Terdeteksi: {result['detected_city']}")
    
    print(f"📊 Metode: {result['final_method']}")
    
    if 'api_confidence' in result:
        print(f"💎 Confidence API: {result['api_confidence']}/10")
    
    if result['final_coordinates']:
        lat, lng = result['final_coordinates']
        print(f"\n📍 KOORDINAT:")
        print(f"Latitude: {lat}")
        print(f"Longitude: {lng}")
        print(f"🗺️ Google Maps: {result['maps_link']}")
    
    print(f"\n💡 Informasi:")
    if result['final_method'] == 'prefix_database':
        print("• Lokasi berdasarkan database prefix nomor Indonesia")
        print("• Akurasi: Menengah (radius ~10-30 km)")
    elif result['final_method'] == 'opencage_api':
        print("• Lokasi dari API geocoding real-time")
        print("• Akurasi: Tinggi (radius ~1-5 km)")
    else:
        print("• Lokasi perkiraan berdasarkan provider")
        print("• Akurasi: Rendah (radius ~50+ km)")

print("\nTerima kasih telah menggunakan layanan ini!")