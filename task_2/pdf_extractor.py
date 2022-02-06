"""
Python version: python3.8

Description: This script downloads Google Sheet from given URL and scrapes text content
    from each pdf whose url is given in the sheet.

    In case of pdfs directly downloadable, pdfplumber python package is used to extract
    text content from the pdf.

    In case of links directing archive.org, the script scrapes URL of readymade text file
    from the HTML, and then extracts pure text content from that file.

Technical description: The script uses basic scraper stack - python-requests + bs4.
    Alternatively Scrapy + Playwright + rotating proxies may be used.

    To extract text from pdf, pdfplumber is used. Other packages like pandas and json
    are used for reading writing purposes.

Author: edusanketdk@gmail.com
"""

from bs4 import BeautifulSoup
from io import BytesIO
import pandas as pd
import regex as re
import pdfplumber
import requests
import json
import time


# accepts any Google Sheet url and downloads into a pandas dataframe
def download_sheet(url):
    url = url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(url, header=None, usecols=[0])
    df.columns = ["links"]
    return df


# accepts a application/pdf response and saves content to a pdf file locally
def download_pdf(response):
    with open('file.pdf', 'wb') as f:
        f.write(response.content)


# accepts a application/text response and saves content to a text file locally
def download_txt(response):
    with open('file.txt', 'wb') as f:
        f.write(response.content)


# called when URL does not link to a downloadable pdf file
# scrapes URL of a plain text file from the HTML. The file contains readymade text from the pdf
def locate_txt(response):
    soup = BeautifulSoup(response.content, "html.parser")
    domain = "https://" + re.findall('https?://([A-Za-z_0-9.-]+).*', response.url)[0]
    for i in soup.find_all('a', href=True):
        if '.txt' in i['href']:
            return requests.get(domain + i['href'].replace("/stream/", "/download/"))


# extracts text content from pdf file using pdfplumber
def read_pdf():
    text = ''
    with pdfplumber.open(r'file.pdf') as pdf:
        mypage = pdf.pages[len(pdf.pages)//2]
        text += mypage.extract_text()

    text = text.replace("\n", " ").replace("\t", " ")
    return text


# extracts text content from txt file
def read_txt():
    with open(r'file.txt', encoding="utf8") as txt:
        text = txt.read()

    text = text.replace("\n", " ").replace("\t", " ")
    return text


# downloading Google Sheet from given URL to pandas dataframe
print("script is staring...")
url = "https://docs.google.com/spreadsheets/d/1I7hziCQGd0uKzh4RMnZtpkTspaE-1_bIL0FcGU_Y1DU/edit#gid=1169510777"
df = download_sheet(url)
print("downloaded google sheet...")


# iterates over all URLs given in the sheet
# if URL links to a downloadable pdf file, then downloads the file and reads text using pdfplumber
# else locates and downloads txt file, and reads text
# saves the page-url, pdf-url and content to a list of dictionaries
output = []
for link in df.links:
    time.sleep(1)
    cur_op = {"page-url": link}
    print(f"scraping text from {link}...")

    response = requests.get(link)
    if response.headers.get('content-type') == "application/pdf":
        cur_op["pdf-url"] = link
        download_pdf(response)
        cur_op["pdf-content"] = read_pdf()
    else:
        locate_response = locate_txt(response)
        cur_op["pdf-url"] = locate_response.url
        download_txt(locate_response)
        cur_op["pdf-content"] = read_txt()

    output.append(cur_op)


# the list of dictionaries is converted into JSON and saved to a file
with open("pdf_extract.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False)
print("script is completed!")