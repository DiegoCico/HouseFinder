import csv
from property_scraper import get_property_info
from neighborhood_scraper import get_neighborhood_info

def main():
    # Read URLs from url.txt (each URL on a new line)
    try:
        with open("url.txt", "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # If url.txt doesn't exist, create it with a default URL
        urls = ["https://www.redfin.com/WA/Seattle/2nd-and-John/apartment/145726232 1x1+D D"]
        with open("url.txt", "w", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")
        print("url.txt not found. A default URL has been added.")

    all_data = []
    for url in urls:
        print(f"\nProcessing URL: {url}")
        data = get_property_info(url, get_neighborhood_info)
        if data:
            all_data.append(data)

    # Save the scraped data to a CSV file
    if all_data:
        keys = all_data[0].keys()
        with open("exported_data.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_data)
        print("\nData has been saved to 'exported_data.csv'.")
    else:
        print("No data was scraped to save.")

    # Write (or re-write) the URLs into url.txt to ensure they are stored locally
    with open("url.txt", "w", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")
    print("The URLs have been saved to 'url.txt'.")

if __name__ == "__main__":
    main()
