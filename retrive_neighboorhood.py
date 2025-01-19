from geopy.geocoders import Nominatim
import time
import requests
from bs4 import BeautifulSoup

geolocator = Nominatim(user_agent="geoapi")

def get_neighboorhood_info(address: str) -> dict:
    neighboorhood = {}
    url = generate_link(address)
    
    if not url:
        return {
            "Amenities" : "N/A",
            "Commute" : "N/A",
            "Cost Of Living" : "N/A",
            "Crime" : "N/A",
            "Employment" : "N/A",
            "Health" : "N/A",
            "Housing" : "N/A",
            "Ratings" : "N/A"
        }
    else:
        return url

def generate_link(address: str) -> str: 
    """
    Generates a neighborhood URL based on a provided address, scrapes the webpage,
    and retrieves a specific link.

    Args:
        address (str): Address in the format "Street Address, City, State".

    Returns:
        str: Final URL for the neighborhood information, or `None` if no relevant link is found.

    Raises:
        Exception: If geocoding or webpage retrieval fails after retries.
    """
    location = geolocator.geocode(address)
    split_address = address.split(",")
    print("Full Location:", location.address)
    addr_url = split_address[0].replace(" ", "+")
    city = split_address[1].strip().lower()
    state = split_address[2].strip()[:2].lower()

    pre_url = f"https://www.areavibes.com/search-results/?st={state}&ct={city}zip=&addr={addr_url}&ll={location.latitude}+{location.longitude}"
    time.sleep(3)

    for attempt in range(3):
        try:
            response = requests.get(pre_url, timeout=10)
            if response.status_code == 200:
                break
        except requests.RequestException as e:
            print(f"Web scraping attempt {attempt + 1} failed: {e}")
            time.sleep(2)  

    if not response or response.status_code != 200:
        raise Exception("Failed to retrieve the webpage after multiple attempts.")

    soup = BeautifulSoup(response.text, 'html.parser')
    element = soup.find("a", class_="pri") 

    if element:
        href = element.get("href")  
        print("Href:", href)
        url = f"https://www.areavibes.com{href}"
        print(f"URL FOR NEIGHBOORHOOD: {url}")
        return url
    else:
        print("No element found with class 'pri'.")
        Nothing = None
        print("NO URL FOR NEIGHBOORHOOD")
        return nothing