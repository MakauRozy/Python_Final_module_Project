import requests

PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
headers = {"User-Agent":"solar-yield-estimator-practice-project/1.0 (makaurozy@gmail.com)"}  
class ApiError(Exception):
    pass

def geocode(place):
    try:
        params = {"q": place, "format": "json", "limit": 1}
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=30)
        print(f"Server replied with: {response.status_code}")

    except requests.RequestException as error:
        raise ApiError(f"Could not reach the location service: {error}")
    
    if response.status_code != 200:
            raise ApiError(f"Location lookup failed ({response.status_code}): {response.text[:200]}")
    
    data = response.json()
    if not data:
            print("No match found.")
            return None
       
    lat=data[0]['lat']
    lon= data[0]['lon']
    print(f"{place} is located on latitude {lat} and longitude {lon}")
    return float(lat), float(lon),place


def fetch_pvgis(lat, lon, peakpower, tilt, aspect, loss):
    """Returns {"yearly_kwh": float, "monthly": [ {month, energy_kwh, irradiation}, ... ]}"""
    params_1= {
        "lat": lat,
        "lon": lon,
        "peakpower": peakpower,
        "loss": loss,
        "angle": tilt,
        "aspect": aspect,
        "outputformat": "json",
    }
    response= requests.get(PVGIS_URL, params=params_1,timeout=30)
    print(response.status_code)
    result=response.json()

    try:
        yearly = result["outputs"]["totals"]["fixed"]["E_y"]
        rows = result["outputs"]["monthly"]["fixed"]
    except (KeyError, TypeError):
        raise ApiError("PVGIS replied, but not in the format expected.")

    monthly = [
        {"month": r["month"], "energy_kwh": r["E_m"], "irradiation": r["H(i)_m"]}
        for r in rows
    ]

    return {"yearly_kwh": yearly, "monthly": monthly}

def get_solar_estimate(place, peakpower, tilt, aspect, loss, known_location=None):

    if known_location:
        matched, lat, lon = known_location
    else:
        found = geocode(place)
        if found is None:
            raise ApiError(f"No location found for '{place}'. "
                           "Try adding the country or a nearby town.")
        lat, lon, matched = found
    result = fetch_pvgis(lat, lon, peakpower, tilt, aspect, loss)
    return matched, lat, lon, result

"""   
if __name__ == "__main__":
   
    found = geocode("Kenya High School")

    if found is None:
        print("No match found.")
    else:
        lat, lon, matched = found
        print("Matched:", matched, lat, lon)
        total = fetch_pvgis(lat, lon, 10, 10, 0, 14)
        print("Yearly kWh:", total["yearly_kwh"])
        # print("Monthly kWh:", total["monthly"])

"""


