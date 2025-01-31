from geopy.geocoders import Nominatim
import time
import requests
from bs4 import BeautifulSoup
import re

geolocator = Nominatim(user_agent="geoapi")

def get_neighboorhood_info(address: str) -> dict:
    neighboorhood = {}
    info = get_info(address)

    return info


def get_info(address: str) -> dict:
    """
    Retrieves information about the neighborhood based on the provided address.
    Extracts detailed metrics like amenities, commute, cost of living, etc.,
    including their grades and associated numbers.

    Args:
        address (str): The address in the format "Street Address, City, State".

    Returns:
        dict: A dictionary containing detailed neighborhood metrics.
    """
    url = generate_link(address)

    info = {
        "Livability": "N/A",
        "Amenities": "N/A",
        "Commute": "N/A",
        "Cost Of Living": "N/A",
        "Crime": "N/A",
        "Employment": "N/A",
        "Health": "N/A",
        "Housing": "N/A",
        "Schools": "N/A",
        "Ratings": "N/A"
    }

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        livability_score = soup.find("span", class_="cw-score-numerator")
        if livability_score:
            info["Livability"] = f"{livability_score.text.strip()}/100"

        categories = soup.find_all("div", class_="widget-entry ac")
        for category in categories:
            category_name = category.find("span")
            grade_element = category.find("i")
            if category_name:
                category_text = category_name.text.strip()
                grade_text = grade_element.text.strip() if grade_element else "N/A"
                info[category_text] = grade_text

        subcategories = soup.find_all("div", class_="widget-indiv-entry")
        for subcategory in subcategories:
            subcategory_name = subcategory.find("b")
            if subcategory_name:
                subcategory_text = subcategory_name.text.strip()

                subcategory_number = subcategory_name.next_sibling
                if subcategory_number and isinstance(subcategory_number, str):
                    subcategory_number = re.sub(r"\s+", " ", subcategory_number).strip(" ()")  
                else:
                    subcategory_number = "N/A"

                grade_element = subcategory.find("i")
                grade_text = grade_element.text.strip() if grade_element else "N/A"
                info[subcategory_text] = f"({subcategory_number}) {grade_text}".replace("\n", "").strip()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return info


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
    

print(get_neighboorhood_info("2nd & John Apartments, 200, 2nd Avenue West, Uptown, Belltown, Seattle, King County, Washington, 98119, United States"))