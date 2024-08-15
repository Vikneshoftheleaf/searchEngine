# firebase_config.py

import firebase_admin
from firebase_admin import credentials, firestore
import scrapy
from scrapy.crawler import CrawlerProcess
import time
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin


def initialize_firestore():
    # Initialize Firebase Admin SDK using the JSON file
    cred = credentials.Certificate('firebaseConfig.json')
    firebase_admin.initialize_app(cred)

    # Initialize Firestore client
    db = firestore.client()
    return db


# crawl.py

# crawl_one_page.py


  # simple_crawl.py

import requests
from bs4 import BeautifulSoup
def crawl_and_store(url):
    # Send a request to the URL
    response = requests.get(url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the title and content
    title = soup.title.string if soup.title else 'No title'
    content = ' '.join(p.get_text() for p in soup.find_all('p'))
    icon_link = soup.find('link', rel=lambda value: value and 'icon' in value.lower())
        
        # If a favicon is found, resolve the full URL
    if icon_link and icon_link.get('href'):
        favicon_url = urljoin(url, icon_link['href'])
    
    # Initialize Firestore
    db = initialize_firestore()
    
    # Prepare data to be stored
    data = {
        'url': url,
        'title': title,
        'content': content,
        'icon': favicon_url
    }
    
    # Store data in Firestore
    db.collection('web_crawl').add(data)
    print(f"Data from {url} stored in Firestore.")

if __name__ == "__main__":
    seed_url = "https://chillfeast.vercel.app"  # Replace with your target URL
    crawl_and_store(seed_url)


"""
class ContinuousCrawler(scrapy.Spider):
    name = 'continuous_crawler'

    def __init__(self, seed_url, *args, **kwargs):
        super(ContinuousCrawler, self).__init__(*args, **kwargs)
        self.start_urls = [seed_url]
        self.db = initialize_firestore()

    def parse(self, response):
        # Extract and follow all links on the page
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, self.parse)

        # Prepare data to be stored
        data = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'content': ' '.join(response.css('p::text').getall()),
            'timestamp': time.time()
        }

        # Store data in Firestore
        self.db.collection('web_crawl').add(data)

        # Log the URL that was crawled
        self.logger.info(f"Crawled: {response.url}")

def run_crawler(seed_url):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    })

    # Crawl continuously
    while True:
        process.crawl(ContinuousCrawler, seed_url=seed_url)
        process.start(stop_after_crawl=False)  # Stop the process after one round of crawling
        time.sleep(10)  # Delay before restarting the crawl (adjust as needed)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        seed_url = sys.argv[1]
        run_crawler(seed_url)
    else:
        print("Please provide a seed URL.")

"""