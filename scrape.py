import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from dotenv import load_dotenv
import os

# Pulls in ScrapeOps API Key from .env file
load_dotenv()
API_KEY = os.getenv("SCRAPEOPS_API_KEY")
KEYWORDS = "_nkw=" + os.getenv("KEYWORDS").replace(" ", "+")
BUY_IT_NOW = "LH_BIN=" + os.getenv("BUY_IT_NOW")
PRICE_MIN = "_udlo" + os.getenv("PRICE_MIN")
PRICE_MAX = "_udhi=" + os.getenv("PRICE_MAX")
ITEM_CONDITION = "LH_ItemCondition=" + os.getenv("ITEM_CONDITION").replace(",", "|")
EXTRA_FILTERS = os.getenv("EXTRA_FILTERS")

# Sends the GET request with Cloudflare bypass
def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'bypass': 'cloudflare'}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

# Make a GET request to the URL
response = requests.get(get_scrapeops_url( \
    f"https://www.ebay.com/sch/i.html?{KEYWORDS}" + \
    f"&{BUY_IT_NOW}&{PRICE_MIN}&{PRICE_MAX}" + \
    f"&{ITEM_CONDITION}&{EXTRA_FILTERS}"))

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, "html.parser")

# Find all the listings on the page
listings = soup.find_all("li", class_="s-item s-item__pl-on-bottom")

# Loop through each listing
for listing in listings:

    # Finds the link of the listing
    link = listing.find("a", class_="s-item__link")["href"]

    # Finds the title of the listing
    title = listing.find("span", role="heading")
    if title is None or title.text == "Shop on eBay":
        continue
    else:
        title = title.text

    # Finds the price of the listing
    price = listing.find("span", class_="s-item__price")
    if price is None:
        continue
    else:
        price = price.text

    # Prints the title, price, and link
    print(f"Title: {title} | Price: {price} \nURL: {link} \n\n")
