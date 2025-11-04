"""

import requests

url = "https://rest.isric.org/soilgrids/v2.0/properties/query"

parameters = {
    "lat": 7.15,
    "lon": 2.05,
    "property": "soc",
    "depth": "0-5cm",
    "value": "mean"
}

response = requests.get(url, params=parameters)
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code} - {response.text}")
    print(f"Error: {response.status_code} - {response.text}")

print("--------------------------------------------------\n")
print(response)

print("--------------------------------------------------\n")
print(data)



la sortie est la suivante :

{
'type': 'Feature', 
'geometry': {'type': 'Point', 'coordinates': [2.05, 7.15]}, 
'properties': {'layers': [{'name': 'soc', 'unit_measure': {'d_factor': 10, 'mapped_units': 'dg/kg', 'target_units': 'g/kg', 'uncertainty_unit': ''}, 
                'depths': [{'range': {'top_depth': 0, 'bottom_depth': 5, 'unit_depth': 'cm'}, 
                'label': '0-5cm', 'values': {'mean': 261}}]}]}, 
'query_time_s': 0.16894745826721191
}
"""



import requests

def get_soil_property(lat, lon, prop):
    """
    Interroge l'API SoilGrids pour une propriété, une latitude et une longitude données.
    """
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    parameters = {
        "lat": lat,
        "lon": lon,
        "property": prop,
        "depth": "0-5cm",
        "value": "mean"
    }

    print(f"--- Interrogation pour la propriété : {prop} ---")
    r = requests.get(url, params=parameters)

    if r.status_code == 200:
        data = r.json()
        try:
            # On extrait la valeur ET le facteur de division
            mean_value = data['properties']['layers'][0]['depths'][0]['values']['mean']
            d_factor = data['properties']['layers'][0]['unit_measure']['d_factor']
            unit = data['properties']['layers'][0]['unit_measure']['target_units']

            if mean_value is not None and d_factor is not None:
                # On fait le calcul !
                final_value = mean_value / d_factor
                print(f"Propriété '{prop}' : {final_value:.2f} {unit}")
                return final_value
            else:
                print(f"Donnée non disponible (None) pour '{prop}'.")
                return None

        except (KeyError, IndexError, TypeError) as e:
            print(f"Erreur en parsant la réponse JSON pour '{prop}': {e}")
            return None
    else:
        print(f"Erreur API pour '{prop}': {r.status_code} - {r.text}")
        return None

# --- Nos tests ---
latitude_test = 7.15
longitude_test = 2.05

get_soil_property(latitude_test, longitude_test, "sand")
get_soil_property(latitude_test, longitude_test, "clay")
get_soil_property(latitude_test, longitude_test, "ph")
get_soil_property(latitude_test, longitude_test, "soc")