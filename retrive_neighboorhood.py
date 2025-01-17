from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapi")


def generate_link(address: str) -> str: 
    location = geolocator.geocode(address)
    split_address = address.split(",")
    print("Full Location:", location.address)
    addr_url = split_address[0].replace(" ", "+")
    city = split_address[1].strip().lower()
    state = split_address[2].strip()[:2].lower()
    return "work"