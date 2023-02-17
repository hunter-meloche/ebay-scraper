import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import os
import boto3
import json

def lambda_handler(event,context):
    # Pulls eBay search variables from environment variables
    KEYWORDS = "_nkw=" + os.environ['KEYWORDS'].replace(" ", "+")
    BUY_IT_NOW = "LH_BIN=" + os.environ['BUY_IT_NOW']
    PRICE_MIN = "_udlo" + os.environ['PRICE_MIN']
    PRICE_MAX = "_udhi=" + os.environ['PRICE_MAX']
    ITEM_CONDITION = "LH_ItemCondition=" + os.environ['ITEM_CONDITION'].replace(",", "|")
    EXTRA_FILTERS = os.environ['EXTRA_FILTERS']

    # Create a Secrets Manager client
    secret_name = "dev/ebayScraper/SCRAPEOPS_API_KEY"
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    # Get the ScrapeOps API key from Secrets Manager
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response["SecretString"]
    API_KEY = json.loads(secret)["SCRAPEOPS_API_KEY"]

    # Sends the GET request with Cloudflare bypass
    def get_scrapeops_url(url):
        payload = {'api_key': API_KEY, 'url': url, 'bypass': 'cloudflare'}
        proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
        print(f"{proxy_url}")
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