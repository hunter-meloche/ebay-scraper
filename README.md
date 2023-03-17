# ebay-scraper
An AWS Lambda web scraper for analyzing item listings on eBay written in Python.

## Disclaimer
This is not to be used for commercial purposes or harm eBay. This project is for educational purposes only and not intended to be used in any way to break eBay or Cloudflare's Terms of Service agreements. Web scraping publicly available information is legal where I live, but check your own local laws.

## Example Usage
This is an event-driven function. You can feed it test events within the Lamda function's UI or you can use EventBridge to schedule or have events programtically triggered. Below is an example event:

This example event will perform a search for an RTX 3080 under $500. Any new listings its found are stored in a PostgreSQL RDS database for future analysis.
```
{
  "KEYWORDS": "RTX 3080",
  "BUY_IT_NOW": "1",
  "PRICE_MIN": "200",
  "PRICE_MAX": "500",
  "ITEM_CONDITION": "1000,1500,1750,2000,2010,2020,2030,2500,2750,3000,4000,5000,6000",
  "EXTRA_FILTERS": "Memory%2520Size=10%2520GB&Chipset%252FGPU%2520Model=NVIDIA%2520GeForce%2520RTX%25203080"
}
```
[Item condition code reference](https://developer.ebay.com/devzone/finding/callref/enums/conditionIdList.html)

## Setup
You need a [ScrapeOps API key](https://scrapeops.io/). Store your API key in AWS Secrets Manager under the key name "dev/ebay-scraper-tf/SCRAPEOPS_API_KEY".

You can use [infra-ebay-scraper](https://github.com/hunter-meloche/infra-ebay-scraper) to automate the rest of this process. If you wish to do the rest manually, continue reading.

Run build.sh and upload the produced function.zip file to a Python 3.9 x86 Lambda function. Credit to https://github.com/jkehler/awslambda-psycopg2 for the Lambda-compatible version of psycopg2.

You must also create a PostgreSQL RDS databse and store the connection info in AWS Secrets Manager under the key name "dev/ebay-scraper-tf/postgres". The RDS needs the following database name, "ebay_listings" and a table within it called, "listings". The listings table columns can be created with the following SQL script.
```
-- Table: public.listings

CREATE TABLE IF NOT EXISTS public.listings
(
    "listingId" bigint NOT NULL,
    "listingName" text COLLATE pg_catalog."default" NOT NULL,
    "totalPrice" numeric NOT NULL,
    "itemPrice" numeric NOT NULL,
    "shippingPrice" numeric NOT NULL,
    "sellerScore" numeric NOT NULL,
    "sellerPercent" numeric NOT NULL,
    link text COLLATE pg_catalog."default" NOT NULL,
    keywords text COLLATE pg_catalog."default" NOT NULL,
    "buyItNow" boolean,
    "priceMin" numeric,
    "priceMax" numeric,
    "itemCondition" text COLLATE pg_catalog."default",
    "extraFilters" text COLLATE pg_catalog."default",
    "dateTime" timestamp with time zone NOT NULL,
    ignore boolean DEFAULT false,
    "ignoreReason" text COLLATE pg_catalog."default",
    CONSTRAINT listings_pkey PRIMARY KEY ("listingId")
)
```
