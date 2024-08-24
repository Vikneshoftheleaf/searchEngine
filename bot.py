import re
import html
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time
import os

seed_url = "https://en.wikipedia.org/wiki/Main_Page"
visited_urls_file = "visited_urls.json"
url_queue_file = "url_queue.json"
max_urls = 1000  # Maximum number of URLs to crawl

def extract_domain_name(url):
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    
    # Handle cases with subdomains and multiple TLDs (e.g., en.wiki.org)
    if len(domain_parts) > 2:
        # For domains like en.wiki.org, return 'wiki'
        return domain_parts[-2]
    else:
        # For domains like example.com, return 'example'
        return domain_parts[0]


def clean_text(text):
    if text:
        # Remove newlines and carriage returns
        text = text.replace('\n', ' ').replace('\r', ' ')
        # Decode HTML entities (e.g., &amp; becomes &)
        text = html.unescape(text)
        # Remove URL encoding (e.g., %20 becomes a space)
        text = re.sub(r'%[0-9A-Fa-f]{2}', lambda x: chr(int(x.group(0)[1:], 16)), text)
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return default

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

visited_urls = load_json(visited_urls_file, [])
url_queue = load_json(url_queue_file, [seed_url])

def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".rstrip('/')

def is_url_allowed(robots_url, url):
    try:
        response = requests.get(robots_url, timeout=5)
        if response.status_code == 200:
            robots_txt = response.text
            return True  # Logic to parse robots.txt can be added here
        else:
            return True  # Assume allowed if robots.txt is not found
    except requests.RequestException:
        return True  # Assume allowed if fetching robots.txt fails

while url_queue and len(visited_urls) < max_urls:
    current_url = url_queue.pop(0)
    if any(item['url'] == current_url for item in visited_urls):
        continue
    
    try:
        parsed_url = urlparse(current_url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        # Check if the current URL is allowed by robots.txt
        if is_url_allowed(robots_url, current_url):
            response = requests.get(current_url, timeout=10)
            if response.status_code == 200:
                print(f"Crawling: {current_url}")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract and clean title
                title = clean_text(soup.title.string) if soup.title else 'No title found'

                # Extract and clean meta description
                meta_description = 'No meta description found'
                meta_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_tag and 'content' in meta_tag.attrs:
                    meta_description = clean_text(meta_tag['content'])
                
                # Extract and clean favicon link
                favicon = 'No favicon found'
                icon_link = soup.find('link', rel=lambda x: x and 'icon' in x)
                if icon_link and 'href' in icon_link.attrs:
                    favicon = urljoin(current_url, clean_text(icon_link['href']))
                
                # Extract and clean first image
                first_image = 'No image found'
                img_tag = soup.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    first_image = urljoin(current_url, clean_text(img_tag['src']))

                # Extract and clean headings
                headings = {
                    'h1': [clean_text(h1.get_text(strip=True)) for h1 in soup.find_all('h1')],
                    'h2': [clean_text(h2.get_text(strip=True)) for h2 in soup.find_all('h2')],
                    'h3': [clean_text(h3.get_text(strip=True)) for h3 in soup.find_all('h3')],
                    'h4': [clean_text(h4.get_text(strip=True)) for h4 in soup.find_all('h4')],
                    'h5': [clean_text(h5.get_text(strip=True)) for h5 in soup.find_all('h5')],
                    'h6': [clean_text(h6.get_text(strip=True)) for h6 in soup.find_all('h6')]
                }

                # Store cleaned crawled data
                crawled_data = {
                    'domain': extract_domain_name(current_url),
                    'url': current_url,
                    'title': title,
                    'meta_description': meta_description,
                    'favicon': favicon,
                    'first_image': first_image,
                    'headings': headings
                }
                visited_urls.append(crawled_data)
                
                # Extract and normalize links for next crawl
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(current_url, link['href'])
                    normalized_url = normalize_url(next_url)
                    # Add next_url to queue if not already visited or in queue
                    if normalized_url not in [item['url'] for item in visited_urls] and normalized_url not in url_queue:
                        url_queue.append(normalized_url)
                        
                # Save the current state periodically (every 10 URLs)
                if len(visited_urls) % 10 == 0:
                    save_json(visited_urls_file, visited_urls)
                    save_json(url_queue_file, url_queue)

            time.sleep(0.5)  # Rate limiting: 1-second delay between requests

    except requests.RequestException as e:
        print(f"Failed to crawl {current_url}: {e}")

# Final save at the end
save_json(visited_urls_file, visited_urls)
save_json(url_queue_file, url_queue)