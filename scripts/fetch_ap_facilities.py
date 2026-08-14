import json
import urllib.request
import urllib.parse
import os
import uuid

def fetch_layer_features(layer_url):
    features = []
    offset = 0
    batch_size = 1000
    
    while True:
        # Use f=geojson because ArcGIS JSON without returnGeometry=true sometimes omits it
        query_url = f"{layer_url}/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&resultOffset={offset}&resultRecordCount={batch_size}"
        print(f"Fetching {query_url}...")
        req = urllib.request.Request(query_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'features' not in data:
                    print("No features found in response, breaking.")
                    break
                    
                batch_features = data['features']
                features.extend(batch_features)
                print(f"Fetched {len(batch_features)} features. Total so far: {len(features)}")
                
                if len(batch_features) < batch_size:
                    break
                    
                offset += batch_size
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
            
    return features

def normalize_ap_data():
    phc_url = "https://apsdmagis.ap.gov.in/gisserver/rest/services/Hosted/NP_Health/FeatureServer/4"
    hosp_url = "https://apsdmagis.ap.gov.in/gisserver/rest/services/Hosted/NP_Health/FeatureServer/2"
    
    print("--- Fetching PHCs ---")
    phc_features = fetch_layer_features(phc_url)
    
    print("\n--- Fetching Hospitals ---")
    hosp_features = fetch_layer_features(hosp_url)
    
    facilities = []
    seen_coords = set()
    
    def add_facility(name, fac_type, lat, lng, district, mandal, village, contact=""):
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180) or (lat == 0 and lng == 0):
            return
            
        coord_key = (round(lat, 5), round(lng, 5))
        if coord_key in seen_coords:
            return
        seen_coords.add(coord_key)
        
        facilities.append({
            "id": str(uuid.uuid4()),
            "name": name.title() if name else "Unknown Facility",
            "type": fac_type,
            "lat": lat,
            "lng": lng,
            "district": district.title() if district else "",
            "mandal": mandal.title() if mandal else "",
            "village": village.title() if village else "",
            "contact": contact
        })

    phc_metadata = {}
    for f in phc_features:
        props = f.get('properties', {}) or f.get('attributes', {})
        name = (props.get('phc') or props.get('PHC') or "").strip().upper()
        dist = (props.get('dname') or props.get('DNAME') or "").strip().upper()
        if name:
            phc_metadata[(name, dist)] = {
                "mandal": props.get('dmname') or props.get('DMNAME') or "",
                "village": props.get('dvname') or props.get('DVNAME') or ""
            }

    for f in hosp_features:
        props = f.get('properties', {}) or f.get('attributes', {})
        geom = f.get('geometry')
        
        # Try both GeoJSON and Esri JSON geometry formats
        if geom:
            if 'coordinates' in geom:
                lng, lat = geom.get('coordinates', [0, 0])
            else:
                lng = geom.get('x', 0)
                lat = geom.get('y', 0)
        else:
            continue
            
        name = props.get('hospital_n') or props.get('HOSPITAL_N') or "Hospital"
        fac_type = props.get('hospital_t') or props.get('HOSPITAL_T') or "Hospital"
        district = props.get('district_name') or props.get('DISTRICT_NAME') or props.get('district') or ""
        
        # Normalize types
        if "Primary Health" in fac_type:
            fac_type = "PHC"
        elif "Community Health" in fac_type:
            fac_type = "CHC"
        elif "District" in fac_type:
            fac_type = "District Hospital"
        elif "Area" in fac_type:
            fac_type = "Area Hospital"
            
        # Cross-reference to find mandal and village
        mandal = ""
        village = ""
        if fac_type == "PHC":
            key = (name.strip().upper(), district.strip().upper())
            meta = phc_metadata.get(key)
            if not meta:
                # Try just name match
                for (k_name, k_dist), m in phc_metadata.items():
                    if k_name == key[0]:
                        meta = m
                        break
            if meta:
                mandal = meta["mandal"]
                village = meta["village"]
            
        add_facility(name, fac_type, lat, lng, district, mandal, village)
        
    print(f"\nTotal valid facilities extracted: {len(facilities)}")
    
    with open("data/facilities.json", "w", encoding="utf-8") as f:
        json.dump(facilities, f, indent=2, ensure_ascii=False)
        
    print("Saved to data/facilities.json")
    
    # Validation summary
    print("\n--- Validation Summary ---")
    print(f"Total records: {len(facilities)}")
    print(f"PHC count: {sum(1 for f in facilities if f['type'] == 'PHC')}")
    print(f"CHC count: {sum(1 for f in facilities if f['type'] == 'CHC')}")
    print(f"Hospital count: {sum(1 for f in facilities if 'Hospital' in f['type'])}")
    districts = set(f['district'] for f in facilities if f['district'])
    print(f"Number of districts: {len(districts)}")
    mandals = set(f['mandal'] for f in facilities if f['mandal'])
    print(f"Number of mandals: {len(mandals)}")
    villages = set(f['village'] for f in facilities if f['village'])
    print(f"Number of villages: {len(villages)}")
    print(f"Missing district: {sum(1 for f in facilities if not f['district'])}")
    print(f"Missing village: {sum(1 for f in facilities if not f['village'])}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    normalize_ap_data()
