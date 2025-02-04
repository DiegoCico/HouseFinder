# main.py

from property_scraper import PropertyScraper
from neighborhood_scraper import NeighborhoodScraper


def main():
    # Example URL string: the first token is the property URL,
    # and any tokens after (separated by spaces) indicate a room choice.
    url_full = "https://www.redfin.com/WA/Seattle/2nd-and-John/apartment/145726232 1x1+D"

    # Initialize the property scraper.
    # Set use_selenium=True if you expect dynamic content that requests cannot fetch.
    property_scraper = PropertyScraper(url_full, use_selenium=False)
    property_info = property_scraper.get_property_info()

    print("----- PROPERTY INFO -----")
    for key, value in property_info.items():
        print(f"{key}: {value}")

    # If a valid address was found, fetch neighborhood information.
    address = property_info.get("Address")
    if address and "Address not found" not in address:
        neighborhood_scraper = NeighborhoodScraper(address)
        neighborhood_info = neighborhood_scraper.get_neighborhood_info()

        print("\n----- NEIGHBORHOOD INFO -----")
        for key, value in neighborhood_info.items():
            print(f"{key}: {value}")
    else:
        print("No valid address found; skipping neighborhood lookup.")


if __name__ == "__main__":
    main()
