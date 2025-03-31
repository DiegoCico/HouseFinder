import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

def index_properties(csv_file: str, model_name="all-MiniLM-L6-v2"):
    """
    Loads property data from a CSV file, cleans missing values, creates a combined text
    description for each property, computes embeddings using SentenceTransformer, and
    indexes them using FAISS.
    """
    # Load CSV data and fill missing values with "N/A"
    df = pd.read_csv(csv_file)
    df.fillna("N/A", inplace=True)
    
    # Create a text description for each property
    docs = []
    for index, row in df.iterrows():
        doc = (
            f"Building Name: {row['Building Name']}. "
            f"Address: {row['Address']}. "
            f"Room: {row['Room Title']}. "
            f"Bed/Baths: {row['Bed/Baths']}. "
            f"Price: {row['Price']}. "
            f"Sqft: {row['Sqft']}. "
            f"Livability: {row['Livability']}. "
            f"Amenities: {row['Amenities']}."
        )
        docs.append(doc)
    
    # Compute embeddings using a free SentenceTransformer model (local processing)
    model = SentenceTransformer(model_name)
    embeddings = model.encode(docs, convert_to_numpy=True)
    
    # Build a FAISS index using L2 (Euclidean) distance
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    return index, embeddings, df, docs, model

def search_properties(query: str, index, df, model, top_k: int = 5):
    """
    Computes the embedding for a search query, retrieves the top_k closest property documents,
    and returns the matching rows with their similarity distances.
    """
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    results = df.iloc[indices[0]].copy()
    results['distance'] = distances[0]
    return results

def display_results(results, distance_threshold=1e+10):
    """
    Displays search results in a user-friendly format.
    Only properties with a distance below the threshold (i.e. good matches) are shown.
    """
    if results.empty:
        print("No results found.")
        return
    
    # Filter out results with extremely high distances
    filtered = results[results['distance'] < distance_threshold]
    if filtered.empty:
        print("No good matches found.")
        return
    
    for i, row in filtered.iterrows():
        print("\n" + "-" * 50)
        print(f"Building Name: {row['Building Name']}")
        print(f"Address:       {row['Address']}")
        print(f"Room Title:    {row['Room Title']}")
        print(f"Price:         {row['Price']}")
        print(f"Sqft:          {row['Sqft']}")
        print(f"Livability:    {row['Livability']}")
        print(f"Distance:      {row['distance']:.2f}")
        print("-" * 50)

def main():
    csv_file = "exported_data.csv"  # Ensure your scraper updates this CSV file
    print("Indexing properties from CSV (running locally)...")
    index, embeddings, df, docs, model = index_properties(csv_file)
    
    while True:
        query = input("\nEnter search query (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        results = search_properties(query, index, df, model)
        print("\nSearch Results:")
        display_results(results)
        
if __name__ == "__main__":
    main()
