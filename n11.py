'''
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from thefuzz import fuzz
from sentence_transformers import SentenceTransformer, util

def operations333(search_query):
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service("/Users/mehmethakanguven/Desktop/Visual_Studio/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    try:
        driver.get('https://www.n11.com/')  # Masaüstü siteyi kullan

        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Ürün, kategori, marka ara"]'))
            )
            search_box.click()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
        except Exception as e:
            print("Arama kutusu bulunamadı veya bir hata oluştu:", e)
            return None

        minPrice = float('inf')  # Başlangıçta sonsuz büyük bir değer
        minPriceInfo = None
        minPriceLink = None

        # Sayfanın tamamen yüklendiğinden emin ol
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//li[@class="column "]'))
        )
        html_source = driver.page_source  # Sayfanın HTML kaynağını alın

        # BeautifulSoup kullanarak sayfa kaynağını parse edin
        soup = BeautifulSoup(html_source, 'html.parser')
        urunler = soup.find_all('li', class_='column')

        if not urunler:
            print("Ürünler bulunamadı.")
        else:
            for urun in urunler:
                try:
                    product_name = urun.find('h3', class_='productName').text.strip()
                    product_price = urun.find('div', class_='priceContainer').text.strip()
                    product_link = urun.find('a', class_='plink')['href']  # Ürün linkini al
                    
                    # thefuzz kullanarak benzerlik kontrolü yap
                    similarity = fuzz.partial_token_sort_ratio(search_query.lower(), product_name.lower())
                    query_embedding = model.encode(search_query, convert_to_tensor=True)
                    product_embeddings = model.encode(product_name, convert_to_tensor=True)
                    cosine_score = util.pytorch_cos_sim(query_embedding, product_embeddings)
                    if similarity >= 71 and cosine_score.item() >= 0.70:  # Eşik değerini ihtiyaca göre ayarlayabilirsiniz
                        print(f"Ürün: {product_name}, Fiyat: {product_price}, Link: {product_link}")
                        
                        # Fiyatı doğru şekilde ayıklayın
                        priceText = re.sub(r'[^\d,\.]', '', product_price)  # Hem nokta hem virgülü al
                        
                        # Eğer fiyat virgüllü bir şekilde ayrılmışsa (örn: 1.177,50 TL), sadece en son virgülü nokta ile değiştir
                        if priceText.count(',') > 1:
                            priceText = priceText.replace('.', '').replace(',', '.')
                        else:
                            priceText = priceText.replace(',', '.')

                        priceFloat = float(priceText)  # Stringi float'a çevir

                        if priceFloat < minPrice:  # Yeni minimum fiyatı ayarla
                            minPrice = priceFloat
                            minPriceInfo = priceFloat  
                            minPriceLink = product_name  # Minimum fiyatlı ürünün adını al
                    else:
                        print(f"Alakasız ürün bulundu: {product_name} (Benzerlik: {similarity}%)")
                except Exception as e:
                    print(f"Ürün veya fiyat bilgisi alınırken hata oluştu: {e}")

    except Exception as e:
        print("Hata oluştu:", e)

    finally:
        driver.quit()
        return minPriceInfo, minPriceLink  # Minimum fiyatı ve ürün adını döndür
'''

#liblaries
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from thefuzz import fuzz
from sentence_transformers import SentenceTransformer, util

def operations333(search_query):
    #connect to the webdriver, set options and start model for sentence_transformers
    options = Options()
    options.add_argument("--disable-notifications") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service("/Users/mehmethakanguven/Desktop/Visual_Studio/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    try:
        driver.get('https://www.n11.com/')  # enter the link here

        try:    #find the search box, click it, enter the search query and press enter
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Ürün, kategori, marka ara"]'))
            )
            search_box.click()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
        except Exception as e:
            print("Arama kutusu bulunamadı veya bir hata oluştu:", e)
            return None

        minPrice = float('inf')  # Infinitely great value in the beginning
        minPriceInfo = None
        minPriceLink = None

        # wait fot the page and find the relevant place
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//li[@class="column "]'))
        )
        html_source = driver.page_source  # get the HTML source of the page

        # Parse page source using BeautifulSoup
        soup = BeautifulSoup(html_source, 'html.parser')
        urunler = soup.find_all('li', class_='column')

        if not urunler:
            print("Ürünler bulunamadı.")
        else:
            for urun in urunler:
                try:
                    product_name = urun.find('h3', class_='productName').text.strip()
                    product_price = urun.find('div', class_='priceContainer').text.strip()
                    product_link = urun.find('a', class_='plink')['href']  #get the products link
                    
                    # control the similarty with thefuzz and sentence_transformers liblaries
                    similarity = fuzz.partial_token_sort_ratio(search_query.lower(), product_name.lower())
                    query_embedding = model.encode(search_query, convert_to_tensor=True)
                    product_embeddings = model.encode(product_name, convert_to_tensor=True)
                    cosine_score = util.pytorch_cos_sim(query_embedding, product_embeddings)
                    if similarity >= 71 and cosine_score.item() >= 0.70:  # set threshold value (this can be set later)
                        # get the price of product 
                        priceText = product_price.split()[0]  # organize the price of product
                        priceText = re.sub(r'[^\d,]', '', priceText)  # organize the price of product
                        priceText = priceText.replace(',', '.')  # organize the price of product

                        print(f"Ürün: {product_name}, Fiyat: {priceText}, Link: {product_link}")

                        priceFloat = float(priceText)  # convert string to float

                        if priceFloat < minPrice:  # set new minimum price
                            minPrice = priceFloat
                            minPriceInfo = priceFloat  
                            minPriceLink = product_name  # get minimum price and product name
                    else:   #this operation will delete and here for control
                        print(f"Alakasız ürün bulundu: {product_name} (Benzerlik: {similarity}%)")
                except Exception as e:
                    print(f"Ürün veya fiyat bilgisi alınırken hata oluştu: {e}")

    except Exception as e:
        print("Hata oluştu:", e)

    finally:
        driver.quit()
        return minPriceInfo, minPriceLink  # return the minimum price and the name of the product
