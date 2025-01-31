# property_scraper.py

import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PropertyScraper:
    """
    Scrapes property details from a given URL.

    Attributes:
        url_full (str): The URL (with optional room choice appended after a space).
        room_choice (str): Specific room details to filter for.
        use_selenium (bool): Whether to load the page with Selenium (e.g., to click on expandable elements).
    """

    def __init__(self, url_full: str, use_selenium: bool = False):
        # The URL may include extra info (e.g., room choice) after a space.
        parts = url_full.split()
        self.url = parts[0]
        self.room_choice = " ".join(parts[1:]) if len(parts) > 1 else None
        self.use_selenium = use_selenium
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/85.0.4183.121 Safari/537.36"
            )
        }

    def get_property_info(self) -> dict:
        """
        Retrieves property information including name, address, room details, and amenities.
        """
        info = {}
        html_content = self._fetch_html()
        if not html_content:
            return {}

        # Extract property details
        info["Building Name"] = self._get_name(html_content)
        info["Address"] = self._get_address(html_content)
        room_info = self._get_room_info(html_content)
        info.update(room_info)
        amenities = self._get_amenities(html_content)
        info.update(amenities)
        return info

    def _fetch_html(self) -> str:
        """Fetches HTML content using either Requests or Selenium."""
        if self.use_selenium:
            return self._fetch_html_selenium()
        else:
            return self._fetch_html_requests()

    def _fetch_html_requests(self) -> str:
        """Fetches HTML using the requests library (with retry logic)."""
        for attempt in range(3):
            try:
                response = requests.get(self.url, headers=self.headers)
                if response.status_code == 429:
                    print(f"Rate limit hit. Retrying in {2**attempt} seconds...")
                    time.sleep(2**attempt)
                else:
                    response.raise_for_status()
                    return response.text
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2**attempt)
        print("Max retries reached for requests.")
        return ""

    def _fetch_html_selenium(self) -> str:
        """Fetches HTML using Selenium (e.g., to handle dynamically loaded content)."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(self.url)
            wait = WebDriverWait(driver, 10)
            try:
                # Try to find and click an expandable element if present.
                expandable_button = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ExpandableLink--expanded"))
                )
                if expandable_button:
                    print("Found expandable button. Clicking it...")
                    driver.execute_script("arguments[0].click();", expandable_button)
                    time.sleep(2)  # Allow time for content to load
            except Exception as e:
                print("Expandable button not found or not clickable:", e)
            return driver.page_source
        except Exception as e:
            print("Error fetching page with Selenium:", e)
            return ""
        finally:
            driver.quit()

    def _get_name(self, html: str) -> str:
        """Parses the property name."""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h1", class_="property-header")
        return element.text.strip() if element else "Name not found"

    def _get_address(self, html: str) -> str:
        """Parses the property address."""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h2", class_="full-address")
        return element.text.strip() if element else "Address not found"

    def _get_room_info(self, html: str) -> dict:
        """
        Parses the room (floor plan) details if a room choice was provided.
        """
        info = {
            "Room Title": "None",
            "Bed/Baths": "None",
            "Price": "None",
            "Sqft": "None",
            "Availability": "None"
        }
        if not self.room_choice:
            return info

        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all("div", class_="floorPlanInfo")
        if not elements:
            print("No floorPlanInfo elements found.")
            return info

        for element in elements:
            name_div = element.find("div", class_="name")
            if name_div:
                room_name = name_div.text.strip()
                print(f"Found Room Title: {room_name}")
                if room_name != self.room_choice:
                    continue
            else:
                continue

            details = element.find("div", class_="details")
            price = element.find("div", class_="price")
            available_count = element.find("div", class_="availableCount")

            info["Room Title"] = room_name
            if details and "·" in details.text:
                parts = details.text.split("·")
                if len(parts) >= 3:
                    info["Bed/Baths"] = parts[0].strip()
                    info["Sqft"] = parts[2].strip().replace("Sqft.", "").strip()
            info["Price"] = price.text.strip() if price else "None"
            info["Availability"] = available_count.text.strip() if available_count else "None"
            break  # Stop after finding the matching room

        return info

    def _get_amenities(self, html: str) -> dict:
        """Parses the amenities data from the page."""
        soup = BeautifulSoup(html, "html.parser")
        amenities = {
            "Cats Allowed": False,
            "Dogs Allowed": False,
            "Cat Rent": None,
            "Dog Rent": None,
            "Parking Type": None,
            "Parking Fee": None,
            "Assigned Parking": None,
            "EV Parking Fee": None,
            "Lease Term": None,
            "Application fee": None
        }

        pets_blocks = soup.find_all("div", class_="PetsBlock")
        for pet_block in pets_blocks:
            pet_type = pet_block.find("h3")
            pet_rent = pet_block.find("div", class_="table-value")
            if pet_type and "Cats welcome" in pet_type.text:
                amenities["Cats Allowed"] = True
                amenities["Cat Rent"] = pet_rent.text.strip() if pet_rent else None
            if pet_type and "Dogs welcome" in pet_type.text:
                amenities["Dogs Allowed"] = True
                amenities["Dog Rent"] = pet_rent.text.strip() if pet_rent else None

        parking_block = soup.find("div", class_="ParkingTypeBlock")
        if parking_block:
            parking_rows = parking_block.find_all("div", class_="table-row")
            for row in parking_rows:
                label = row.find("span", class_="table-label")
                value = row.find("div", class_="table-value")
                if label and value:
                    if "Type" in label.text:
                        amenities["Parking Type"] = value.text.strip()
                    elif "Parking fee" in label.text:
                        amenities["Parking Fee"] = value.text.strip()
                    elif "Assigned" in label.text:
                        amenities["Assigned Parking"] = value.text.strip()

            ev_parking_fee = parking_block.find("p", class_="comment")
            if ev_parking_fee and "EV Spots Available" in ev_parking_fee.text:
                amenities["EV Parking Fee"] = ev_parking_fee.text.split("for ")[-1].strip()

        lease_term = soup.find("div", class_="LeaseTermBlock")
        if lease_term:
            lease_rows = lease_term.find_all("div", class_="table-row")
            for row in lease_rows:
                label = row.find("span", class_="table-label")
                value = row.find("div", class_="table-value")
                if label and value:
                    key = label.text.strip()
                    val = value.text.strip()
                    if key == "Term type":
                        amenities["Lease Term"] = val
                    elif key == "Application fee":
                        amenities["Application fee"] = val

        return amenities
