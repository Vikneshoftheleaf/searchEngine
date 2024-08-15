import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import json
import os

def extract_domain_name(url):
    # Parse the URL to get the netloc (domain with TLD)
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Remove 'www.' if it exists
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Split the domain by '.' and take the first part (before TLD)
    domain_name = domain.split('.')[0]
    
    return domain_name

# Function to scrape title, meta description, and all heading tags from a webpage
def scrape_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = soup.title.string if soup.title else "No title found"
    
    # Extract meta description
    meta_description = ""
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta:
        meta_description = meta.get('content', "No meta description found")
    else:
        meta_description = "No meta description found"
    
    # Extract all heading tags
    headings = {}
    for i in range(1, 7):
        tag = f'h{i}'
        headings[tag] = [heading.get_text(strip=True) for heading in soup.find_all(tag)]

    icon_link = soup.find('link', rel=lambda value: value and 'icon' in value.lower())
        
        # If a favicon is found, resolve the full URL
    if icon_link and icon_link.get('href'):
        favicon_url = urljoin(url, icon_link['href'])
    else:
        favicon_url = False
    
    return {
        'domain': extract_domain_name(url),
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "headings": headings,
        "icon": favicon_url
    }

# Function to crawl a webpage starting from the seed URL
def crawl(seed_url, max_pages=10, output_file="crawled_data.json"):
    visited = set()
    queue = deque([seed_url])
    crawled_data = []

    while queue and len(crawled_data) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        
        visited.add(url)
        print(f"Crawling: {url}")
        
        page_data = scrape_webpage(url)
        if page_data:
            crawled_data.append(page_data)
            # Append data to JSON file
            append_to_json_file(page_data, output_file)
        
        # Parse the page to find all <a> tags and enqueue their URLs
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(url, a_tag['href'])
            if urlparse(link).netloc == urlparse(seed_url).netloc and link not in visited:
                queue.append(link)
    
    return crawled_data

# Function to append data to a JSON file
def append_to_json_file(data, file_path):
    # Check if file exists
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)  # Create an empty list in the file if it doesn't exist

    # Read existing data
    with open(file_path, 'r') as f:
        existing_data = json.load(f)

    # Append new data
    existing_data.append(data)

    # Write updated data back to the file
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=4)

    print(f"Appended data to {file_path}")

# Seed URL to start crawling
seed_url = ["https://google.com"]

for i in seed_url:
    crawl(i, max_pages=10, output_file="crawled_data.json")

# Crawl the website and append data to JSON
