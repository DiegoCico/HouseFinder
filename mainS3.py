# main.py

from s3_storage import S3Storage

def main():
    # Create an instance of the storage handler
    storage = S3Storage()

    # Example data (this could be your scraped property/neighborhood info)
    data = {
        "Building Name": "The Example Tower",
        "Address": "123 Example Street, Sample City, ST 00000",
        "Room Info": {
            "Room Title": "1x1 Deluxe",
            "Bed/Baths": "1 Bed / 1 Bath",
            "Price": "$1200",
            "Sqft": "750",
            "Availability": "Now"
        },
        "Amenities": {
            "Cats Allowed": True,
            "Dogs Allowed": False,
            "Parking Fee": "$100"
        },
        "Neighborhood": {
            "Livability": "85/100",
            "Commute": "Good",
            "Schools": "Average"
        }
    }
    
    # Key (filename) to store the data in S3
    key = "property_info.json"

    # --- STORE (ADD/UPDATE) DATA ---
    storage.store_data(data, key)

    # --- RETRIEVE DATA ---
    retrieved_data = storage.retrieve_data(key)
    print("Retrieved Data:")
    print(retrieved_data)

    # --- LIST FILES ---
    print("\nListing files in the bucket:")
    storage.list_files()

    # --- DELETE DATA ---
    # Uncomment the following line to delete the stored data from S3.
    # storage.delete_file(key)

if __name__ == "__main__":
    main()
