import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import boto3
import json
import psycopg2
import re
from datetime import datetime

def lambda_handler(event,context):

    # Pulls eBay search variables from event variables
    KEYWORDS = event['KEYWORDS'].replace(" ", "+")
    urlKeywords = "_nkw=" + KEYWORDS
    BUY_IT_NOW = event['BUY_IT_NOW']
    urlBuyItNow = "LH_BIN=" + BUY_IT_NOW
    PRICE_MIN = event['PRICE_MIN']
    urlPriceMin = "_udlo=" + PRICE_MIN
    PRICE_MAX = event['PRICE_MAX']
    urlPriceMax = "_udhi=" + PRICE_MAX
    ITEM_CONDITION = event['ITEM_CONDITION'].replace(",", "|")
    urlItemCondition = "LH_ItemCondition=" + ITEM_CONDITION
    EXTRA_FILTERS = event['EXTRA_FILTERS']

    # Construct URL with search variables
    url = f"https://www.ebay.com/sch/i.html?{urlKeywords}" + \
          f"&{urlBuyItNow}&{urlPriceMin}&{urlPriceMax}" + \
          f"&{urlItemCondition}&{EXTRA_FILTERS}"
    print(f"Search URL:\n{url}\n\n")

    # Create a Secrets Manager client
    region_name = "us-east-1"
    session = boto3.session.Session()
    secrets_client = session.client(service_name='secretsmanager', \
        region_name=region_name)

    # Get the ScrapeOps API key from Secrets Manager
    get_secret_value_response = secrets_client.get_secret_value(\
        SecretId="dev/ebay-scraper-tf/SCRAPEOPS_API_KEY")
    secrets_dict = json.loads(get_secret_value_response["SecretString"])
    API_KEY = secrets_dict["SCRAPEOPS_API_KEY"]

    # Get the RDS instance endpoint and credentials from Secrets Manager
    get_secret_value_response = secrets_client.get_secret_value(\
        SecretId="dev/ebay-scraper-tf/postgres")
    secrets_dict = json.loads(get_secret_value_response['SecretString'])
    db_host = secrets_dict['host']
    db_user = secrets_dict['username']
    db_password = secrets_dict['password']

    # connect to the database
    try:
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database="ebay_listings"
        )
    except (psycopg2.DatabaseError) as error:
        print("Error while connecting to PostgreSQL database:", error)

    # Define the SQL query to insert data into the table
    insert_query = """INSERT INTO listings 
        ("listingId", "listingName", "totalPrice", "itemPrice", "shippingPrice", 
        "sellerScore", sellerPercent", "link", "keywords", "buyItNow", 
        "priceMin", "priceMax", "itemCondition", "extraFilters", "dateTime") 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # Create cursor object to insert into DB
    cursor = conn.cursor()

    # Sends the GET request with Cloudflare bypass
    def get_scrapeops_url(url):
        payload = {'api_key': API_KEY, 'url': url, 'bypass': 'cloudflare'}
        proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
        return proxy_url

    # Make a GET request to the URL
    response = requests.get(get_scrapeops_url(url))

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
        itemPrice = listing.find("span", class_="s-item__price")
        if itemPrice:
            itemPrice = itemPrice.text.replace("$", "")
        else:
            Print("Unable to find item price ofr this listing; skipping")
            continue

        # Finds shipping price of the listing
        shipping = listing.find("span", class_="s-item__shipping s-item__logisticsCost")
        if shipping: # Case for regular shipping
            if shipping.text == "Free shipping":
                shippingPrice = 0
            else:
                shippingMatch = re.search(r"\$(\d+(?:\.\d{1,2})?)", shipping.text)
                if shippingMatch:
                    shippingPrice = shippingMatch.group(1)
                else:
                    print("Unable to find shipping info for listing; skipping")
                    continue
        else:
            shipping = listing.find("span", class_="s-item__dynamic s-item__freeXDays")
            if shipping: # Case for free+fast shipping
                shippingPrice = 0
            else:
                print("Unable to find shipping info for listing; skipping")
                continue

        # Finds seller rating
        sellerInfo = listing.find("span", class_="s-item__seller-info-text")
        sellerMatch = re.search(r"\((\d+)\) (\d+(\.\d+)?)%", sellerInfo.text)
        if sellerMatch:
            sellerScore = int(sellerMatch.group(1))
            sellerPercent = float(sellerMatch.group(2))
        else:
            print("Unable to find seller info for listing; skipping")
            continue

        # Generates primary key from listing ID in link
        listingMatch = re.search(r"/(\d+)\?", link)
        if listingMatch:
            listingId = listingMatch.group(1)
            print(listingId)
        else:
            print("Unable to find listing ID in link; skipping")
            continue

        # Generates a timestamp for when the listing was found
        timestamp = datetime.now()

        # Calculates total price by adding shipping cost to item price
        totalPrice = itemPrice + shippingPrice

        # Compiles the listing data to be inserted to the database
        entry = (int(listingId), title, totalPrice, itemPrice, shippingPrice, \
            sellerScore, sellerPercent, link, KEYWORDS, bool(int(BUY_IT_NOW)), \
            PRICE_MIN, PRICE_MAX, ITEM_CONDITION, EXTRA_FILTERS, timestamp)

        # Inserts a new entry for this listing into the database
        try:
            cursor.execute(insert_query, entry)
        except (Exception, psycopg2.Error) as error:
            print(f"Error inserting data into PostgreSQL table: {error}\n\n")
            conn.rollback()
            continue
        else:
            conn.commit()

        # Prints the title, price, and link for logging
        print(f"Title: {title} | Price: {price} \nURL: {link} \n\n")

    # Closes the DB connection if it is still open
    if (conn):
        cursor.close()
        conn.close()
        print("PostgreSQL connection is closed")
