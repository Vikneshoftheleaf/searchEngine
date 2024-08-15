import json
from collections import defaultdict

# Step 1: Load JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Step 2: Create an index for the data
def create_index(data):
    index = defaultdict(list)
    
    for i, entry in enumerate(data):
        url = entry.get("url")
        title = entry.get("title")
        first_heading = entry["headings"]["h1"][0] if entry["headings"]["h1"] else None
        
        # Index by URL
        if url:
            index["url"].append((url, i))
        
        # Index by Title
        if title:
            index["title"].append((title, i))
        
        # Index by first H1 heading
        if first_heading:
            index["first_heading"].append((first_heading, i))
    
    return index

# Step 3: Search the index
def search_index(query):
    key = "title"
    results = []
    for item, i in index[key]:
        if item and query.lower() in item.lower():
            results.append(data[i])
    return results

# Step 4: Example usage

# File path to the JSON file
file_path = "crawled_data.json"  # Replace with your file path

# Load the JSON data
data = load_json(file_path)

# Create an index
index = create_index(data)

# Example queries
#query_url = "https://chillfeast.vercel.app/about"
#query_title = "chillfeast"
#query_heading = "About Us"

"""

# Search by URL
results_by_url = search_index(query_url, index, "url")
print("Results by URL:", results_by_url)


# Search by First Heading in H1
results_by_heading = search_index(query_heading, index, "first_heading")
print("Results by First Heading:", results_by_heading)


# Search by Title
results_by_title = search_index(query_title, index, "title")
print("Results by Title:", results_by_title)
    """
