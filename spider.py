import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os

seed_url = "https://chillfeast.vercel.app"
visited_urls_file = "visited_urls.json"
url_queue_file = "url_queue.json"
max_urls = 1000  # Maximum number of URLs to crawl

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

while url_queue and len(visited_urls) < max_urls:
    current_url = url_queue.pop(0)
    if any(item['url'] == current_url for item in visited_urls):
        continue
    
    try:
        response = requests.get(current_url, timeout=10)
        if response.status_code == 200:
            print(f"Crawling: {current_url}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else 'No title found'

            # Extract meta description
            meta_description = 'No meta description found'
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and 'content' in meta_tag.attrs:
                meta_description = meta_tag['content']
            
            # Extract favicon link
            favicon = 'No favicon found'
            icon_link = soup.find('link', rel=lambda value: value and 'icon' in value.lower())
            #icon_link = soup.find('link', rel=lambda x: x and 'icon' in x)
            if icon_link and 'href' in icon_link.attrs:
                favicon = urljoin(current_url, icon_link['href'])
            
            # Extract first image
            first_image = 'No image found'
            img_tag = soup.find('img')
            if img_tag and 'src' in img_tag.attrs:
                first_image = urljoin(current_url, img_tag['src'])

            # Extract all headings
            headings = {
                'h1': [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
                'h2': [h2.get_text(strip=True) for h2 in soup.find_all('h2')],
                'h3': [h3.get_text(strip=True) for h3 in soup.find_all('h3')],
                'h4': [h4.get_text(strip=True) for h4 in soup.find_all('h4')],
                'h5': [h5.get_text(strip=True) for h5 in soup.find_all('h5')],
                'h6': [h6.get_text(strip=True) for h6 in soup.find_all('h6')]
            }

            # Store crawled data
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
                if not any(item['url'] == normalized_url for item in visited_urls) and normalized_url not in url_queue:
                    url_queue.append(normalized_url)
                    
            # Save the current state periodically (every 10 URLs)
            if len(visited_urls) % 10 == 0:
                save_json(visited_urls_file, visited_urls)
                save_json(url_queue_file, url_queue)

        time.sleep(1)  # Rate limiting: 1-second delay between requests
        
    except requests.RequestException as e:
        print(f"Failed to crawl {current_url}: {e}")

# Final save at the end
save_json(visited_urls_file, visited_urls)
save_json(url_queue_file, url_queue)
