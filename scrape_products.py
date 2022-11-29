from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep
from math import ceil
import json


URL = 'https://www.systembolaget.se/sortiment/?sortiment=Fast%20sortiment'
FILE_NAME = 'fast_sortiment.json'


def compute_vol(text: str):
    if " a " in text.replace("à", "a"):
        nr, vol = text.replace("à", "a").split(" a ")
        nr = nr.strip(" åpoiuytrewqäölkjhgfdsasmnbvcxz.,")
        vol = vol.strip()
        return str(int(nr) * int(vol))
    return text

def seperate_vol_apv(text: str):
    for i, char in enumerate(text):
        if char.isnumeric():
            break
    vol_apv = text[i:].split("ml")
    for i, element in enumerate(vol_apv):
        vol_apv[i] = element.strip(" %").replace(',','.')
    vol_apv[0] = compute_vol(vol_apv[0])
    return vol_apv

def format_price(text: str):
    return text.replace(":",".").replace(" ","").strip(" .-*")

def compute_apk(vol_apv: str, price: str):
    vol, apv = seperate_vol_apv(vol_apv)
    price = format_price(price)
    apk = 0.01 * float(vol) * float(apv) / float(price)
    return f"{apk:.2f}"
  
def main():
    products=[]
    added=[]
    
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=chrome_options)
    driver.get(URL)
    driver.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div/section/div/div/div[4]/div/div[2]/a").click()
    driver.find_element(By.XPATH, "//*[@id='modalId']/div[2]/div/button[2]").click()

    soup = BeautifulSoup(driver.page_source, features="html.parser")
    products_num = int(soup.find(attrs={'class':'css-je2jg5 enp2lf70'}).text[:-10])
    
    print(f"Searching for {products_num} products")

    for _ in range(ceil(products_num / 30)):
        sleep(0.05)
        try:
            driver.find_element(By.XPATH, "//*[@id='__next']/main/div[2]/div[2]/div/div[2]/div[2]/div/div[5]/a").click()
        except NoSuchElementException:
            break

    WebDriverWait(driver, 600).until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'a[href^="/produkt"]')) >= products_num)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    driver.quit()
    
    for a in soup.find_all('a', attrs={'class':'css-1rtgr4w enuzix00'}):
        name = a.find(attrs={'class':"css-w9tb7l e3wog7r1"})
        artnum = a.find(attrs={'class':'css-10vqt1w e3wog7r1'}) 
        tags = a.find(attrs={'class':'css-4ijttz enp2lf70'})
        vol_apv = a.find(attrs={'class':'css-5aqtg5 e3whs8q0'}) 
        price = a.find(attrs={'class':'css-1kvpmze enp2lf70'}) 
        
        product = {
            "Name": name.text,
            "ArticleNumber": artnum.text[3:],
            "Tags": tags.text,
            "Volume": seperate_vol_apv(vol_apv.text)[0],
            "AlcoholPerVolume": seperate_vol_apv(vol_apv.text)[1],
            "Price": format_price(price.text),
            "AlcoholPerKrona": compute_apk(vol_apv.text, price.text)
        }
        
        product_id = f"{product['ArticleNumber']} {product['Volume']} {product['Price']}"
        if product_id not in added:
            products.append(product)
            added.append(product_id)  
        
    with open(FILE_NAME, "w") as outfile:
        json.dump(products, outfile)
        
    print(f"Found {len(products)} products")

if __name__ == '__main__':
    main()
