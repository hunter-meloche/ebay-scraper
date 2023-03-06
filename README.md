# ebay-scraper
An AWS Lambda web scraper for finding good deals on eBay written in Python.

## Example Usage
Every hour, a search for an RTX 3080 under $500 is performed. Any new listings are stored in a PostgreSQL RDS database for future analysis.

## Setup
You need to install the dependencies into the lambda directory inside of the repo.
```
pip install -r requirements.txt --target=lambda
```
You also need to manually install psycopg2 into the same lambda directory. Simply copy and paste the psycopg2-3.9 directory inside of the lambda directory. https://github.com/jkehler/awslambda-psycopg2

Zip the contents of the lambda directory and upload the zip file to a Python 3.9 Lambda function.

You also need a [ScrapeOps API key](https://scrapeops.io/) to bypass Cloudflare. Store your API key in AWS Secrets Manager under the key name "dev/ebayScraper/SCRAPEOPS_API_KEY".

You must also create a PostgreSQL RDS databse and store the connection info in Secrets Manager under the key name "dev/ebay-scraper/postgres". The RDS needs the following database name, "ebay_listings" and a table within it called, "listings". The listings table columns can be created with the following pgAdmin4 CREATE script.
```
CREATE TABLE IF NOT EXISTS public.listings
(
    "itemId" bigint NOT NULL,
    "listingName" text COLLATE pg_catalog."default" NOT NULL,
    price numeric NOT NULL,
    link text COLLATE pg_catalog."default" NOT NULL,
    keywords text COLLATE pg_catalog."default" NOT NULL,
    "buyItNow" boolean,
    "priceMin" numeric,
    "priceMax" numeric,
    "itemCondition" text COLLATE pg_catalog."default",
    "extraFilters" text COLLATE pg_catalog."default",
    "dateTime" timestamp with time zone NOT NULL,
    CONSTRAINT listings_pkey PRIMARY KEY ("itemId")
)
```

## Events
This is an event-driven function. You can feed it test events within the Lamda function's UI or you can use EventBridge to schedule or have events programtically triggered. Below is an example event:
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

