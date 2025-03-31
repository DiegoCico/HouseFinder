import time
import requests
import re
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


class NeighborhoodScraper:
    """
    Scrapes neighborhood statistics based on a provided address.
    (This example uses Areavibes to retrieve data such as livability, amenities, and more.)
    """

    def __init__(self, address: str):
        self.address = address
        self.geolocator = Nominatim(user_agent="geoapi")
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/85.0.4183.121 Safari/537.36"
            )
        }

    def generate_link(self) -> str:
        """
        Generates a URL to fetch neighborhood details based on the address.
        """
        location = self.geolocator.geocode(self.address)
        if not location:
            raise Exception("Could not geocode the address.")

        split_address = self.address.split(",")
        if len(split_address) < 3:
            raise Exception("Address format is incorrect. Expected at least 'Street, City, State,...'")

        addr_url = split_address[0].replace(" ", "+")
        city = split_address[1].strip().lower()
        state = split_address[2].strip()[:2].lower()
        pre_url = (
            f"https://www.areavibes.com/search-results/?st={state}&ct={city}"
            f"zip=&addr={addr_url}&ll={location.latitude}+{location.longitude}"
        )
        time.sleep(3)  

        response = None
        for attempt in range(3):
            try:
                response = requests.get(pre_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    break
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)
        if not response or response.status_code != 200:
            raise Exception("Failed to retrieve the neighborhood search page after multiple attempts.")

        soup = BeautifulSoup(response.text, "html.parser")
        element = soup.find("a", class_="pri")
        if element:
            href = element.get("href")
            url = f"https://www.areavibes.com{href}"
            print(f"Generated neighborhood URL: {url}")
            return url
        else:
            print("No neighborhood URL found.")
            return None

    def get_neighborhood_info(self) -> dict:
        """
        Fetches and parses neighborhood information from the generated URL.
        """
        url = self.generate_link()
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
        if not url:
            return info

        try:
            response = requests.get(url, headers=self.headers)
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
                subcat_name = subcategory.find("b")
                if subcat_name:
                    subcat_text = subcat_name.text.strip()
                    subcat_number = subcat_name.next_sibling
                    if subcat_number and isinstance(subcat_number, str):
                        subcat_number = re.sub(r"\s+", " ", subcat_number).strip(" ()")
                    else:
                        subcat_number = "N/A"
                    grade_element = subcategory.find("i")
                    grade_text = grade_element.text.strip() if grade_element else "N/A"
                    info[subcat_text] = f"({subcat_number}) {grade_text}".replace("\n", "").strip()

        except Exception as e:
            print(f"Error fetching neighborhood info: {e}")

        return info
