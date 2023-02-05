import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("SCRAPEOPS_API_KEY")

def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'bypass': 'cloudflare'}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

# Make a request to the URL
response = requests.get(get_scrapeops_url("https://www.ebay.com/sch/i.html?_from=R40&_nkw=rtx+3080+-amd&_sacat=0&LH_TitleDesc=0&Memory%2520Size=10%2520GB&_fsrp=1&LH_BIN=1&LH_ItemCondition=1000%7C1500%7C2500%7C3000&_udhi=500&LH_PrefLoc=2&_udlo=300&rt=nc&Chipset%252FGPU%2520Model=NVIDIA%2520GeForce%2520RTX%25203080&_dcat=27386"))

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, "html.parser")

# Find all the listings on the page
listings = soup.find_all("li", class_="s-item s-item__pl-on-bottom")

# Loop through each listing
for listing in listings:

    link = listing.find("a", class_="s-item__link")["href"]

    # Find the title of the listing
    title = listing.find("span", role="heading")
    if title is None or title.text == "Shop on eBay":
        continue
    else:
        title = title.text

    # Find the price of the listing
    price = listing.find("span", class_="s-item__price")
    if price is None:
        continue
    else:
        price = price.text

    # Print the title and price
    print(f"Title: {title} | Price: {price} \nURL: {link} \n\n")
