import requests
from bs4 import BeautifulSoup

def get_zillow_info(url: str) -> dict:
    """
    Fetches the HTML content of a Zillow listing and extracts information.
    
    Args:
        url (str): The URL of the listing.

    Returns:
        dict: A dictionary with extracted information.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        html_content = response.text
        print(html_content)
        return {
            "name": get_name(html_content),
            "address": get_address(html_content),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return {"name": "Error", "address": "Error"}

def get_name(html_content: str) -> str:
    """
    Extracts the name of the property from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.find("h1", class_="Text-c11n-8-101-4__sc-aiai24-0 BuildingInfo__BuildingName-d8oth5-0 gtFYdd ghrkIg")  # Replace with the correct class
    return element.text.strip() if element else "Name not found"

def get_address(html_content: str) -> str:
    """
    Extracts the address of the property from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.find("h2", class_="Text-c11n-8-101-4__sc-aiai24-0 BuildingInfo__BuildingAddress-d8oth5-1 eLbtxG exdbaQ")  # Replace with the correct class
    return element.text.strip() if element else "Address not found"

# Example usage
if __name__ == "__main__":
    url = "https://www.zillow.com/apartments/seattle-wa/premiere-on-pine/5XjMfs/"  # Update with a real URL
    info = get_zillow_info(url)
    print(info)
