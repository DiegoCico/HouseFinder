import time
import requests
from bs4 import BeautifulSoup
from retrive_neighboorhood import get_neighboorhood_info

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

                # NEIGHBOORHOOD
                neighboorhood = get_neighboorhood_info(info["Address"])
                
                print("NEIGHBOORHOOD")
                print(neighboorhood)
                print("Stats")
                return info
        print("Max retries reached.")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {}

def get_room_info(html_content: str, choice: str) -> dict:
    info = {
        "Room Title": "None",
        "Bed/Baths": "None",
        "Price": "None",
        "Sqft": "None",
        "Availability": "None"
    }
    
    if choice is None:
        return info
    
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.find("div", class_="floorPlanInfo")
    
    if not element:
        return info  
    
    for floor in element.find_all("div", recursive=False): 
        print(floor.text)
        name_and_sash = floor.find("div", class_="nameAndSash")  
        details = floor.find("div", class_="details")
        price = floor.find("div", class_="price")
        available_count = floor.find("div", class_="availableCount")
        
        if not name_and_sash or name_and_sash.text.strip() != choice:
            continue
        
        info["Room Title"] = name_and_sash.text.strip()
        info["Bed/Baths"] = details.text.split("·")[0].strip() if details else "None"
        info["Sqft"] = details.text.split("·")[1].strip() if details and "·" in details.text else "None"
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



# print(get_info("https://www.redfin.com/WA/Seattle/The-LeeAnn/apartment/171922517"))
# print(get_info("https://github.com/yurahriaziev/student-tutor-space/commits/main/"))
print(get_info("https://www.redfin.com/WA/Seattle/2nd-and-John/apartment/145726232 1x1+D A"))