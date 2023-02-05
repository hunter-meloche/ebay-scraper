# ebay-scraper
A web scraper for finding good deals on eBay written in python

## How To Use
You need to make a .env file in the directory with an API key from https://scrapeops.io/. 
This is needed to bypass Cloudflare and signing up gets you 1000 free requests with no credit card. 
This is what the .env file should have inside of it:

SCRAPEOPS_API_KEY=xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx

As it is, the code searches for "Buy It Now" RTX 3080s under $500. All you need to do is replace the url in scrape.py:

response = requests.get(get_scrapeops_url("https://www.ebay.com/sch/i.html?_from=R40&_nkw=rtx+3080+-amd&_sacat=0&LH_TitleDesc=0&Memory%2520Size=10%2520GB&_fsrp=1&LH_BIN=1&LH_ItemCondition=1000%7C1500%7C2500%7C3000&_udhi=500&LH_PrefLoc=2&_udlo=300&rt=nc&Chipset%252FGPU%2520Model=NVIDIA%2520GeForce%2520RTX%25203080&_dcat=27386"))

Be sure to install the requirements first:

pip install -r requirements.txt
