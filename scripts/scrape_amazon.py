import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random

def scrape_amazon(search_query):
    base_url = "https://www.amazon.ca/s?k="
    query = search_query.replace(" ", "+")
    url = base_url + query
    
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US, en;q=0.5"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Failed to fetch the page. Status code:", response.status_code)
            return []

        soup = BeautifulSoup(response.content, "lxml")
        product_list = []
        
        for item in soup.find_all("div", {"data-component-type": "s-search-result"}):
            name = item.h2.text if item.h2 else "N/A"
            link = item.h2.a["href"] if item.h2 and item.h2.a else "N/A"
            full_link = "https://www.amazon.ca" + link
            price_whole = item.find("span", {"class": "a-price-whole"})
            price_fraction = item.find("span", {"class": "a-price-fraction"})
            price = None
            if price_whole and price_fraction:
                price = f"{price_whole.text.strip()}.{price_fraction.text.strip()}"
            rating = item.find("span", {"class": "a-icon-alt"})
            rating = rating.text.split(" ")[0] if rating else "N/A"
            product_list.append({
                "Name": name,
                "Price": price,
                "URL": full_link,
                "Rating": rating
            })
        
        time.sleep(random.uniform(2, 5))  # Add a delay between requests
        return product_list

    except Exception as e:
        print("Error occurred:", str(e))
        return []

if __name__ == "__main__":
    search_query = input("Enter a product to search on Amazon: ")
    results = scrape_amazon(search_query)
    if results:
        for product in results[:5]:  # Print the first 5 results
            print(product)
    else:
        print("No results found.")
