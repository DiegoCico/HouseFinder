import pyzill
import json
property_url="https://www.zillow.com/apartments/kissimmee-fl/the-nexus-at-overbrook/9DSWrh/"
proxy_url = pyzill.parse_proxy("47.251.122.81","8888","None","None")
data = pyzill.get_from_deparment_url(property_url,proxy_url)
jsondata = json.dumps(data)
f = open("details.json", "w")
f.write(jsondata)
f.close()