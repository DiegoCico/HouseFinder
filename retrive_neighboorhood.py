from geopy.geocoders import Nominatim
import time
import requests
from bs4 import BeautifulSoup



geolocator = Nominatim(user_agent="geoapi")


# https://www.areavibes.com/miami-fl/?ll=25.8581+-80.17137&addr=+north+bayshore
                #https://www.areavibes.com/seattle-wa/lower+queen+anne/?ll=47.62569+-122.34781&addr=701+5th+avenue+north
                # https://www.areavibes.com/seattle-wa/downtown/
                # Geolocation

# 701 5th Ave N,Seattle, WA 98109

# https://www.areavibes.com/search-results/?st=wa&ct=seattle&hd=lower+queen+anne&zip=&addr=701+5th+avenue+north&ll=47.62569+-122.34781
# https://www.areavibes.com/search-results/?st=wa&ct=seattle&hd=lower+queen+anne&zip=&addr=701+5th+avenue+north&ll=47.62569+-122.34781#google_vignette
# https://www.areavibes.com/search-results/?st=wa&ct=seattle&hd=lower+queen+anne&zip=&addr=701+5th+avenue+north&ll=47.62569+-122.34781

#https://www.areavibes.com/search-results/?st=wa&ct=seattlezip=&addr=701+5th+avenue+north&ll=47.62569+-122.34781

def get_neighboorhood_info(address: str) -> dict:
    neighboorhood = {}
    url = generate_link(address)
    print(url)

def generate_link(address: str) -> str: 
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
        Nothing = "N/A"
        print("NO URL FOR NEIGHBOORHOOD")
        return nothing