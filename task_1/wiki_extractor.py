"""
Python version: python3.8

Description: This script can scrape first N pages and their first pargraphs from wikipedia
    given a search keyword, and output the data into a JSON file.

Technical description: The script uses basic scraper stack - python-requests + bs4.
    Alternatively Scrapy + Playwright + rotating proxies may be used but that would have
    made the code complicated, since arguments have to be passed.

Author: edusanketdk@gmail.com
"""

from bs4 import BeautifulSoup
import requests
import json
import sys
import time

# receiving the CLI arguments, irrespective of the order
args = sys.argv[1:]
args = dict([i.replace("--", "").replace('"', "").split("=") for i in args])
keyword, num_urls, output = args["keyword"], int(args["num_urls"]), args["output"]
print("script is starting...")


# making the request and receiving the html data into a BeautifulSoup
url = f"https://en.wikipedia.org/w/index.php?title=Special:Search&limit={num_urls}&offset=0&ns0=1&search={keyword}"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")


# scraping page urls from result headings into a list
pages = soup.find_all("div", {"class": "mw-search-result-heading"})
pages = [div.find('a')['href'] for div in pages]
pages = ["https://en.wikipedia.org" + i for i in pages]
print("scraped list of search results...")


# making request to each page url iteratively and scraping best fit paragraph into a list of dictionaries
output_list = []
for url in pages:
    time.sleep(1)
    print(f"scraping paragraph from {url}...")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    for i in soup.find_all('p'):
        text = i.getText().replace("\n", "").replace("\t", "")
        if len(text) > 20: break

    output_list.append({
        "url": url,
        "paragraph": text
    })


# converting the list of dictionaries to JSON and storing in a file
with open(output, "w", encoding="utf-8") as f:
    json.dump(output_list, f, ensure_ascii=False)
print("script is completed!")
