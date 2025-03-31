import time
import requests
from bs4 import BeautifulSoup
import re
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapi")

def get_neighborhood_info(address: str) -> dict:
    """
    Retrieves neighborhood metrics by generating a link and scraping details.
    """
    details = get_neighborhood_details(address)
    return details

def get_neighborhood_details(address: str) -> dict:
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
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/85.0.4183.121 Safari/537.36"
            )
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
                cat_text = category_name.text.strip()
                grade_text = grade_element.text.strip() if grade_element else "N/A"
                info[cat_text] = grade_text

        subcategories = soup.find_all("div", class_="widget-indiv-entry")
        for subcategory in subcategories:
            subcategory_name = subcategory.find("b")
            if subcategory_name:
                sub_text = subcategory_name.text.strip()
                sub_number = subcategory_name.next_sibling
                if sub_number and isinstance(sub_number, str):
                    sub_number = re.sub(r"\s+", " ", sub_number).strip(" ()")
                else:
                    sub_number = "N/A"
                grade_element = subcategory.find("i")
                grade_text = grade_element.text.strip() if grade_element else "N/A"
                info[sub_text] = f"({sub_number}) {grade_text}".replace("\n", "").strip()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching neighborhood data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in get_neighborhood_details: {e}")

    return info

def generate_link(address: str) -> str:
    """
    Generates the final URL for the neighborhood information by geocoding the address
    and then scraping a preliminary page to extract a link.
    """
    location = geolocator.geocode(address)
    if not location:
        raise Exception("Location not found for the provided address.")
    split_address = address.split(",")
    print("Full Location:", location.address)
    addr_url = split_address[0].replace(" ", "+")
    city = split_address[1].strip().lower() if len(split_address) > 1 else ""
    state = split_address[2].strip()[:2].lower() if len(split_address) > 2 else ""
    pre_url = (
        f"https://www.areavibes.com/search-results/?st={state}&ct={city}zip=&addr={addr_url}"
        f"&ll={location.latitude}+{location.longitude}"
    )
    time.sleep(3)

    response = None
    for attempt in range(3):
        try:
            response = requests.get(pre_url, timeout=10)
            if response.status_code == 200:
                break
        except requests.RequestException as e:
            print(f"Web scraping attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    if not response or response.status_code != 200:
        raise Exception("Failed to retrieve the preliminary webpage after multiple attempts.")

    soup = BeautifulSoup(response.text, "html.parser")
    element = soup.find("a", class_="pri")

    if element:
        href = element.get("href")
        print("Found href:", href)
        final_url = f"https://www.areavibes.com{href}"
        print(f"Neighborhood URL: {final_url}")
        return final_url
    else:
        print("No element found with class 'pri'.")
        print("No neighborhood URL available.")
        return None
