import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapi")

def get_neighborhood_from_areavibes(address: str) -> str:
    """
    Retrieves the neighborhood from AreaVibes for the given address.
    """
    try:
        # Geocode the address to get latitude and longitude
        location = geolocator.geocode(address)
        if not location:
            return "Geolocation failed"
        
        lat, lon = location.latitude, location.longitude

        # Generate the AreaVibes URL
        addr_url = address.split(",")[0].replace(" ", "+")
        city = address.split(",")[1].strip().lower()
        state = address.split(",")[2].strip()[:2].lower()
        areavibes_url = f"https://www.areavibes.com/{city}-{state}/?ll={lat}+{lon}&addr={addr_url}"

        # Request the AreaVibes page
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
        response = requests.get(areavibes_url, headers=headers)

        # Parse the response content
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract neighborhood information (adjust selector as needed)
            neighborhood_element = soup.find("div", class_="neighborhood-title")
            if neighborhood_element:
                return neighborhood_element.text.strip()
            else:
                return "Neighborhood not found on AreaVibes"
        else:
            return f"Failed to fetch AreaVibes page: {response.status_code}"

    except Exception as e:
        return f"Error: {e}"

# Example usage
address = "701 5th Ave N, Seattle, WA 98109"
neighborhood = get_neighborhood_from_areavibes(address)
print(f"Neighborhood: {neighborhood}")




# NEIGHBOORHOOD
                # https://www.areavibes.com/miami-fl/?ll=25.8581+-80.17137&addr=+north+bayshore
                #https://www.areavibes.com/seattle-wa/lower+queen+anne/?ll=47.62569+-122.34781&addr=701+5th+avenue+north
                # https://www.areavibes.com/seattle-wa/downtown/
                # Geolocation
                location = geolocator.geocode(info["Address"])
                address_components = location.raw.get("address", {})
                county = address_components.get("county", "County not found")
                print(county)
                # print(neighborhood)
                if location:
                    split_address = info["Address"].split(",")
                    print("Full Location:", location.address)

                    # Extract components
                    addr_url = split_address[0].replace(" ", "+")
                    city = split_address[1].strip().lower()
                    state = split_address[2].strip()[:2].lower()

                    # Customizing the neighborhood (e.g., "downtown" or "uptown")
                    ## TODO MAKE THIS AUTOMATIC
                    neighborhood = "downtown"  
                    
                    lat = location.latitude
                    lng = location.longitude

                    # Constructing the URL for a specific neighborhood
                    url2 = f"https://www.areavibes.com/{city}-{state}/{neighborhood}/?ll={lat}+{lng}&addr={addr_url}"
                    print("Generated AreaVibes URL:", url2)

                    # Optional: Make a request to the constructed URL
                    response2 = requests.get(url2, headers=headers)
                    if response2.status_code == 200:
                        print("Neighborhood data successfully retrieved!")
                else:
                    print("Geolocation failed for the address.")