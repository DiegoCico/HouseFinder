import time
import requests
from bs4 import BeautifulSoup
import re

def get_property_info(url_full: str, get_neighborhood_info_func) -> dict:
    """
    Scrapes rental property details from a given URL.
    The URL string can contain an extra part (separated by a space)
    to indicate the desired room choice.
    
    The get_neighborhood_info_func parameter is a callable that accepts
    an address string and returns a dictionary of neighborhood metrics.
    """
    info = {}
    url = url_full.split()[0]
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/85.0.4183.121 Safari/537.36"
            )
        }
        # Try up to 3 times in case of rate limiting
        for attempt in range(3):
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                print(f"Rate limit hit. Retrying in {2**attempt} seconds...")
                time.sleep(2**attempt)
            else:
                response.raise_for_status()
                html_content = response.text

                split_url = url_full.split()
                choice = " ".join(split_url[1:]) if len(split_url) > 1 else None
                if choice:
                    print("Room choice specified:", choice)
                else:
                    print("No room choice provided.")

                # RENTAL DETAILS
                info["Building Name"] = get_name(html_content)
                info["Address"] = get_address(html_content)
                room_info = get_room_info_bs(html_content, choice)
                info["Room Title"] = room_info["Room Title"]
                info["Bed/Baths"] = room_info["Bed/Baths"]
                info["Price"] = room_info["Price"]
                info["Sqft"] = room_info["Sqft"]
                info["Availability"] = room_info["Availability"]

                amenities = get_amenities(html_content)
                info.update(amenities)

                # NEIGHBORHOOD DETAILS using the provided function
                neighborhood = get_neighborhood_info_func(info["Address"])
                info.update(neighborhood)

                print("Final combined info:")
                print(info)
                return info
        print("Max retries reached.")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred in get_property_info: {e}")
        return {}

def get_room_info_bs(html_content: str, choice: str) -> dict:
    """
    Extracts room information from the HTML content using BeautifulSoup.
    If a specific room choice is provided, it returns data only for that room.
    """
    info = {
        "Room Title": "None",
        "Bed/Baths": "None",
        "Price": "None",
        "Sqft": "None",
        "Availability": "None"
    }

    if not choice:
        return info

    soup = BeautifulSoup(html_content, "html.parser")
    elements = soup.find_all("div", class_="floorPlanInfo")

    if not elements:
        print("No floorPlanInfo elements found.")
        return info

    for element in elements:
        name_elem = element.find("div", class_="name")
        details = element.find("div", class_="details")
        price = element.find("div", class_="price")
        available_count = element.find("div", class_="availableCount")

        if name_elem:
            room_name = name_elem.text.strip()
            print(f"Found Room Title: {room_name}")
            if room_name != choice:
                continue

        info["Room Title"] = room_name if name_elem else "None"
        info["Bed/Baths"] = (
            details.text.split("·")[0].strip()
            if details and "·" in details.text else "None"
        )
        info["Sqft"] = (
            details.text.split("·")[2].strip().replace("Sqft.", "").strip()
            if details and "·" in details.text else "None"
        )
        info["Price"] = price.text.strip() if price else "None"
        info["Availability"] = (
            available_count.text.strip() if available_count else "None"
        )
        break

    return info

def get_name(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.find("h1", class_="property-header")
    return element.text.strip() if element else "Name not found"

def get_address(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.find("h2", class_="full-address")
    return element.text.strip() if element else "Address not found"

def get_amenities(html_content: str) -> dict:
    """
    Extracts amenities (pets, parking, lease terms, etc.) from the HTML.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    print("Retrieving amenities...")

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
            amenities["Cat Rent"] = pet_rent.text if pet_rent else None
        if pet_type and "Dogs welcome" in pet_type.text:
            amenities["Dogs Allowed"] = True
            amenities["Dog Rent"] = pet_rent.text if pet_rent else None

    parking_block = soup.find("div", class_="ParkingTypeBlock")
    if parking_block:
        parking_rows = parking_block.find_all("div", class_="table-row")
        for row in parking_rows:
            label = row.find("span", class_="table-label")
            value = row.find("div", class_="table-value")
            if label and value:
                if "Type" in label.text:
                    amenities["Parking Type"] = value.text
                elif "Parking fee" in label.text:
                    amenities["Parking Fee"] = value.text
                elif "Assigned" in label.text:
                    amenities["Assigned Parking"] = value.text

        ev_parking_fee = parking_block.find("p", class_="comment")
        if ev_parking_fee and "EV Spots Available" in ev_parking_fee.text:
            amenities["EV Parking Fee"] = ev_parking_fee.text.split("for ")[-1]

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

    print("Amenities retrieved:")
    print(amenities)
    return amenities
