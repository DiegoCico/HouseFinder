import time
import requests
from bs4 import BeautifulSoup
from retrive_neighboorhood import get_neighboorhood_info
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_info(url_full: str) -> dict:
    info = {}
    url = url_full.split()[0]
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

                # file_name = "exported_html.txt"
                # with open(file_name, "w", encoding="utf-8") as file:
                #     file.write(html_content)

                split_url = url_full.split()
                choice = None
                if len(split_url) > 1:
                    choice = " ".join(split_url[1:])
                    print(choice)
                else:
                    print("No choice")

                print(split_url)

                # RENTAL
                info["Building Name"] = get_name(html_content)
                info["Address"] = get_address(html_content)
                room_info = get_room_info(html_content, choice)
                info["Room Title"] = room_info["Room Title"]
                info["Bed/Baths"] = room_info["Bed/Baths"]
                info["Price"] = room_info["Price"]
                info["Sqft"] = room_info["Sqft"]
                info["Availability"] = room_info["Availability"]
                ammendities = get_amenities(html_content)
                info.update(ammendities)

                # NEIGHBOORHOOD
                neighboorhood = get_neighboorhood_info(info["Address"])
                info.update(neighboorhood)
                
                print("NEIGHBOORHOOD")
                print(neighboorhood)
                print("FINAL")
                return info
        print("Max retries reached.")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {}

# def get_room_info(url_full: str, choice: str) -> dict:
    """
    Extracts room information from a given URL, handling expandable sections and parsing content.
    
    :param url_full: Full URL of the webpage.
    :param choice: Specific room choice to filter for.
    :return: Dictionary containing room information.
    """
    info = {
        "Room Title": "None",
        "Bed/Baths": "None",
        "Price": "None",
        "Sqft": "None",
        "Availability": "None"
    }

    # Set up Selenium WebDriver (no path to chromedriver needed if in PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # For systems without GPU
    options.add_argument("--no-sandbox")  # Recommended for headless mode
    driver = webdriver.Chrome(options=options)

    try:
        # Load the webpage
        url = url_full.split()[0]
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Check for the expandable button and click it
        try:
            expandable_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ExpandableLink--expanded"))
            )
            if expandable_button:
                print("Found expandable button. Clicking it...")
                driver.execute_script("arguments[0].click();", expandable_button)
                time.sleep(2)  # Allow time for content to load
        except Exception as e:
            print("Expandable button not found or not clickable:", e)

        # Get the updated HTML content
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all room elements
        elements = soup.find_all("div", class_="floorPlanInfo")

        if not elements:
            print("No floorPlanInfo elements found.")
            return info

        # Parse room details
        for element in elements:
            name_and_sash = element.find("div", class_="name")
            details = element.find("div", class_="details")
            price = element.find("div", class_="price")
            available_count = element.find("div", class_="availableCount")

            if name_and_sash:
                room_name = name_and_sash.text.strip()
                print(f"Found Room Title: {room_name}")
                if room_name != choice:
                    continue

            # Populate the info dictionary
            info["Room Title"] = room_name if name_and_sash else "None"
            info["Bed/Baths"] = details.text.split("·")[0].strip() if details and "·" in details.text else "None"
            info["Sqft"] = details.text.split("·")[2].strip().replace("Sqft.", "").strip() if details and "·" in details.text else "None"
            info["Price"] = price.text.strip() if price else "None"
            info["Availability"] = available_count.text.strip() if available_count else "None"
            break  # Exit once the correct room is found

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the browser session

    return info

def get_room_info(html_content: str, choice: str) -> dict:
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
    # Adjusted to match the exact class hierarchy
    elements = soup.find_all("div", class_="floorPlanInfo")
    
    if not elements:
        print("No floorPlanInfo elements found.")
        return info

    for element in elements:
        print("FLOOR ELEMENT")
        print(element)

        name_and_sash = element.find("div", class_="name")
        details = element.find("div", class_="details")
        price = element.find("div", class_="price")
        available_count = element.find("div", class_="availableCount")

        if name_and_sash:
            room_name = name_and_sash.text.strip()
            print(f"Found Room Title: {room_name}")
            if room_name != choice:
                continue

        info["Room Title"] = room_name if name_and_sash else "None"
        info["Bed/Baths"] = details.text.split("·")[0].strip() if details and "·" in details.text else "None"
        info["Sqft"] = details.text.split("·")[2].strip().replace("Sqft.", "").strip() if details and "·" in details.text else "None"
        info["Price"] = price.text.strip() if price else "None"
        info["Availability"] = available_count.text.strip() if available_count else "None"
        break  

    return info

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

def get_amenities(html_content: str) -> dict:
    """
    Extracts the amenities of the property from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    print("getting Amendities")
    
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
            label = row.find("spam", class_="table-label")
            value = row.find("div", class_="table-value")
            if label.text.strip() == "Term type":
                amenities["Lease Term"] = value
            elif label.text.strip() == "Application fee":
                amenities["Application fee"] = value

    print("All Amendities Received:")
    print(amenities)
    return amenities


# print(get_info("https://www.redfin.com/WA/Seattle/The-LeeAnn/apartment/171922517"))
# print(get_info("https://github.com/yurahriaziev/student-tutor-space/commits/main/"))
print(get_info("https://www.redfin.com/WA/Seattle/2nd-and-John/apartment/145726232 1x1+D D"))