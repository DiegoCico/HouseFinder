import time
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapi")

def get_info(url: str) -> dict:
    info = {}
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
        for attempt in range(3): 
            response = requests.get(url, headers=headers)
            if response.status_code == 429:  
                print(f"Rate limit hit. Retrying in {2**attempt} seconds...")
                time.sleep(2**attempt)
            else:
                response.raise_for_status()
                html_content = response.text

                # RENTAL
                info["Building Name"] = get_name(html_content)
                info["Address"] = get_address(html_content)
                # info[""]

                # NEIGHBOORHOOD
                # https://www.areavibes.com/miami-fl/?ll=25.8581+-80.17137&addr=+north+bayshore
                location = geolocator.geocode(info["Address"])
                print(location)
                print(f"latitude {location.latitude}")
                print(f"longitute {location.longitude}")
                

                return info
        print("Max retries reached.")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {}

def get_name(html_content : str) -> str:
    """
    Extracts the name of the property from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.find("h1", class_="property-header")    
    return element.text.strip() if element else "Name not found"

def get_address(html_content: str) -> str:
    """
    Extracts the address of the property from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.find("h2", class_="full-address") 
    return element.text.strip() if element else "Address not found"


print(get_info("https://www.redfin.com/WA/Seattle/The-LeeAnn/apartment/171922517"))