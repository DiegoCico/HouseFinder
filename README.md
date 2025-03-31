# 🏡 House Finder: Real Estate Data Scraper & Semantic Search Engine with AWS Integration

This project is an end-to-end real estate intelligence system that combines web scraping, semantic search, and AWS cloud architecture. It supports both **cloud-based workflows (S3, EC2, IAM)** and **local semantic search**, enabling complete data engineering and information retrieval pipelines.

---

## 🚀 Features

- 🔍 **Property Scraper**: Scrapes real estate listings from Redfin.
- 🏘️ **Neighborhood Scraper**: Extracts neighborhood metadata including amenities, safety, and school ratings.
- ☁️ **AWS Integration**: Uses **S3** for storage, **EC2** for scalable compute, and **IAM** for secure access control.
- 🧠 **Semantic Search**: Find neighborhoods matching natural language queries.
- 📁 **Modular Architecture**: Split between `AWS/` for cloud-based processing and `SemanticSearchLocal/` for local querying.

---

## 📁 Project Structure

```
.
├── AWS/
│   ├── Diagram.png                # Architecture diagram
│   ├── exported_html.txt          # HTML snapshot
│   ├── main.py                    # Main orchestrator for scraping
│   ├── mainS3.py                  # Uploading scraped data to AWS S3
│   ├── neighborhood_scraper.py    # Neighborhood info scraper
│   ├── property_scraper.py        # Redfin property scraper
│   ├── s3_cli.py                  # Command-line S3 uploader
│   ├── s3_storage.py              # Upload/download helpers for S3
│   ├── test.py / test.txt         # Sample test files
│   ├── README.md / requirements.txt
├── SemanticSearchLocal/
│   ├── main.py                    # Runs local semantic search
│   ├── neighborhood_scraper.py
│   ├── property_scraper.py
│   ├── semantic_search.py         # Embedding and querying logic
├── url.txt                        # List of Redfin property URLs to track — system will auto-monitor them
├── exported_data.csv              # Final output CSV combining property + neighborhood data
├── .gitignore
```

---

## ⚙️ Backend Pipeline (Scraping + Cloud Upload)

Located in the `AWS/` directory:

- `property_scraper.py`: Crawls Redfin listings.
- `neighborhood_scraper.py`: Extracts contextual neighborhood data.
- `main.py`: Orchestrates scraping routines.
- `mainS3.py`: Handles JSON export and S3 uploading.
- `s3_storage.py`: Wraps AWS S3 upload/download logic.
- `s3_cli.py`: CLI to interact with AWS cloud.

**Infrastructure**: Use EC2 for deployment, IAM for access roles, and S3 for persistent storage.

---

## 🧠 Frontend Process (Local Semantic Search)

Located in the `SemanticSearchLocal/` directory:

- Uses `sentence-transformers` for embedding neighborhood descriptions.
- Stores vectors and matches user input using cosine similarity.
- Easily extendable to UI or web frontends.

### Example:
```python
from semantic_search import SemanticSearch
search = SemanticSearch("exported_data.json")
print(search.query("Quiet areas with good coffee and parks"))
```

---

## ☁️ AWS Integration

- AWS credentials must be configured locally.
- JSON data can be pushed or pulled from S3 buckets.
- EC2 is recommended for long-running or scalable batch jobs.
- IAM roles should be configured to restrict S3 access securely.

---

## 🛠️ Setup & Installation

### Clone the repo
```bash
git clone https://github.com/your-username/HouseFinder.git
cd HouseFinder
```

### Install dependencies
```bash
pip install -r requirements.txt
```

Typical dependencies:
```text
requests
beautifulsoup4
boto3
sentence-transformers
scikit-learn
```

---

## 🔢 Sample Usage

### Run full scraping pipeline:
```bash
python AWS/main.py
```

### Upload to S3:
```bash
python AWS/mainS3.py
```

### Run local semantic search:
To run semantic search locally, first execute the data scraping step with:
```bash
python SemanticSearchLocal/main.py
```
Then, launch the semantic search engine with:
```bash
python SemanticSearchLocal/semantic_search.py
```
```bash
python SemanticSearchLocal/main.py
```

---

## 📊 Example Output

The system exports all collected and enriched data into a structured CSV format for downstream use.

### CSV Sample Format:
```
Building Name,Address,Room Title,Bed/Baths,Price,Sqft,Availability,Cats Allowed,Dogs Allowed,Cat Rent,Dog Rent,Parking Type,Parking Fee,Assigned Parking,EV Parking Fee,Lease Term,Application fee,Livability,Amenities,Commute,Cost Of Living,Crime,Employment,Health,Housing,Schools,Ratings,amenities,commute,cost of living,crime,employment,health,housing,schools,ratings,Coffee,Entertainment,Food and Drink,Fitness,Groceries,Parks,Shops,Public Transit Stops,Workers Taking Public Transit,Cost of Living,Tax Rates,Property Crime,Violent Crime,Med. Household Income,Unemployment Rate,Health & Safety,Air Quality,Home Price,Home Appreciation Rate,Home Affordability,School Test Scores,High School Grad. Rates,Elementary Schools,High Schools,User Reviews,User Surveys
2nd and John,"200 2nd Ave W,Seattle, WA 98119",None,None,None,None,None,True,True,$40/mo,$50/mo,Garage Lot,$200/mo,Yes,$275 per Month,"2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 month",$14,68/100,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,A+,A+,F,F,A+,A+,B,A+,F,(26) A+,(24) A+,(36) A+,(7) A+,(5) A+,(12) A+,(27) A+,(38) A+,() A+,(N/A) F,() A+,(N/A) F,() F,(N/A) A+,() B-,(6) A+,(N/A) C-,(N/A) A+,(N/A) A+,(N/A) F,(N/A) B-,(N/A) A+,(1) B-,(1) B-,(0),(2) F
```

---

## 📜 License

MIT License

