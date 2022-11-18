import requests
from bs4 import BeautifulSoup
import lxml
import re
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

FORM_URL = "https://forms.gle/M3fQxcqb8E2meNVs7"
ZILLOW_URL = "https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3Anull%2C%22mapBounds%22%3A%7B%22west%22%3A-122.69219435644531%2C%22east%22%3A-122.17446364355469%2C%22south%22%3A37.703343724016136%2C%22north%22%3A37.847169233586946%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A11%7D"

headers_data = {
    "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

response = requests.get(headers=headers_data,url=ZILLOW_URL)
zillow_web_page = response.text

soup = BeautifulSoup(zillow_web_page, "lxml")
listings = soup.find_all(class_="property-card-link")
prices = soup.find_all(class_="hRqIYX")

listing_links = []
listing_address = []
listing_prices = []

for listing in listings:
    #Links
    specific_link = listing.get('href')
    print(specific_link)
    if specific_link not in listing_links:
        if not re.search("^h",specific_link):
            #change the link to add https://zillow.com to beginning
            new_link = "https://zillow.com" + specific_link
            specific_link = new_link
            print(new_link)
        listing_links.append(specific_link)


    #address
    try:
        specific_address = listing.find("address").text
        listing_address.append(specific_address)
        print(specific_address)
    except AttributeError:
        print("No address for this link")

for price in prices:
    # price
    try:
        specific_price = price.find("span").text
        if specific_price.split("+")[0] != specific_price:
            specific_price = specific_price.split("+")[0]
        else:
            specific_price = specific_price.split("/")[0]
        listing_prices.append(specific_price)
        print(specific_price)

    except AttributeError:
        print("no price")

print(listings)
print(listing_links)
print(listing_address)
print(listing_prices)

for index in range(0, len(listing_links)-1):
    #Fill google form with fetched data
    chrome_driver_path = r"C:\Users\vodde\Desktop\Work Stuf\Dev Stuff\chromedriver.exe"
    chrome_options = Options()
    chrome_options.add_experimental_option("detach",True)
    driver = webdriver.Chrome(service=Service(executable_path=chrome_driver_path), options= chrome_options)

    time.sleep(1)
    driver.get("https://docs.google.com/forms/d/e/1FAIpQLSfk60VmIMky4FwNUs-zo7oQ2UTV3ThRIb5XYVaAW7XSqhXxFw/viewform")
    driver.maximize_window()

    #Address
    q1= driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input")
    q1.send_keys(listing_address[index])
    #Price
    q2 = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
    q2.send_keys(listing_prices[index])
    #Link
    q3 = driver.find_element(By.XPATH,"//*[@id='mG61Hd']/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input")
    q3.send_keys(listing_links[index])

    send_button = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[3]/div[1]/div[1]/div/span/span")
    send_button.click()

    time.sleep(2)
    driver.close()
