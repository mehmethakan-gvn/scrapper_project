
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import fuzzy
import unidecode

def normalize_word(word):
    return unidecode.unidecode(word)

def get_soundex(word):
    soundex = fuzzy.Soundex(4)
    normalized_word = normalize_word(word)
    return soundex(normalized_word)

def soundex_similarity(soundex1, soundex2):
    if soundex1 == soundex2:
        return True
    elif soundex1[:30] == soundex2[:30]:  # İlk 30 karakteri kontrol et
        return True
    else:
        return False

def isim_ayikla(new_name, isimler):
    if new_name not in isimler:
        isimler.append(new_name)
        return True
    return False

def contains_all_query_words(product_name, query_words):
    product_name = product_name.lower()
    return all(word in product_name for word in query_words)

def islemler33(search_query):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    service = Service("/Users/mehmethakanguven/Desktop/Visual_Studio/chromedriver")
    #options.add_argument('--headless')  
    #options.add_argument('--disable-gpu')
    #options.add_argument('--no-sandbox')
    #huoptions.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)

    target_soundex = get_soundex(search_query)
    
    try:
        driver.get('https://www.amazon.com.tr/')  

        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'twotabsearchtextbox'))
            )
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
        except Exception as e:
            print("Arama kutusu bulunamadı veya bir hata oluştu:", e)

        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        urunler = soup.find_all("div", attrs={"class": "s-main-slot"})
        isim_unutma = "a"
        search_query = search_query.lower()
        df = pd.DataFrame(columns=['Ürün Adı', 'Fiyat'])
        isimler = []
        min_price_info = 99999999
        search_query = search_query.lower()
        query_words = search_query.split()  # Arama kelimelerini ayırıyoruz

        urun_sayaci = 0
        max_urun_sayisi = 10  

        for urun in urunler:
            if urun_sayaci >= max_urun_sayisi:
                break
            
            urun_link = urun.find("div", class_= "a-section a-spacing-none")
            #print(urun_link)
            urun_linkleri = urun_link.find_all("a", attrs={"class": "a-link-normal"})
            
            for a_tag in urun_linkleri:
                link_devam = a_tag.get("href")
                if link_devam:
                    try:
                        detay = requests.get(link_devam)
                        #print(detay)
                        #print(link_devam)
                        detay_soup = BeautifulSoup(detay.text, "html.parser")

                        title = detay_soup.find(id='productTitle')
                        if title:
                            title_text = title.get_text(strip=True)
                        else:
                            title_text = "Ürün ismi bulunamadı"

                        price = detay_soup.find('span', {'class': 'a-price-whole'})
                        if price:
                            price_text = price.get_text(strip=True)
                        else:
                            price = detay_soup.find('span', {'class': 'a-price'})
                            if price:
                                price_text = price.get_text(strip=True)
                            else:
                                price_text = "Fiyat bulunamadı"
                        
                        if price_text != "Fiyat bulunamadı":
                            price_text = price_text.replace(",", ".") + " TL"  
                        
                        if title_text != isim_unutma and isim_ayikla(title_text, isimler) and price_text != "Fiyat bulunamadı":
                            product_name_lower = title_text.lower()
                            if soundex_similarity(get_soundex(title_text), target_soundex):
                                print(f"Ürün İsmi: {title_text}")
                                print(f"Ürün Fiyatı: {price_text}\n")
                                price_text = price_text.replace(" TL", "").replace(",", ".")
                                price_text = float(price_text)
                                if price_text <= min_price_info:
                                    min_price_info = price_text

                                isim_unutma = title_text

                        if isim_unutma != "Ürün ismi bulunamadı":
                            isim_unutma = title_text
                       
                    except Exception as e:
                        continue

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".s-main-slot"))
        )

        urun_sayaci = 0
        max_urun_sayisi = 5 

        while urun_sayaci < max_urun_sayisi:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            urunler = soup.find("div", class_="s-main-slot")
            urun_linkleri = urunler.find_all("a", attrs={"class": "a-link-normal"})

            for a_tag in urun_linkleri:
                link_devam = a_tag.get("href")
                if link_devam and urun_sayaci < max_urun_sayisi:
                    link_ekle = "https://www.amazon.com.tr/" + link_devam
                    try:
                        detay = requests.get(link_ekle)
                        #print(link_ekle)
                        #print(detay)
                        detay_soup = BeautifulSoup(detay.text, "html.parser")

                        title = detay_soup.find(id='productTitle')
                        if title:
                            title_text = title.get_text(strip=True)
                        else:
                            title_text = "Ürün ismi bulunamadı"

                        price = detay_soup.find('span', {'class': 'a-price-whole'})
                        if price:
                            price_text = price.get_text(strip=True)
                        else:
                            price = detay_soup.find('span', {'class': 'a-price'})
                            if price:
                                price_text = price.get_text(strip=True)
                            else:
                                price_text = "Fiyat bulunamadı"
                            
                        if price_text != "Fiyat bulunamadı":
                            price_text = price_text.replace(",", "") + " TL"  
                        if title_text != "Ürün ismi bulunamadı" and isim_ayikla(title_text, isimler):
                            product_name_lower = title_text.lower()
                            if soundex_similarity(get_soundex(title_text), target_soundex):
                                print(f"Ürün İsmi: {title_text}")
                                print(f"Ürün Fiyatı: {price_text}\n")
                                price_text = price_text.replace(" TL", "").replace(",", ".")
                                price_text = float(price_text)
                                if price_text <= min_price_info:
                                    min_price_info = price_text
                                urun_sayaci += 1
                        
                    except Exception as e:
                        print(f"Detay sayfasına erişim başarısız: {e}")

            if urun_sayaci >= max_urun_sayisi:
                break
        
        driver.quit()
    except Exception as e:
        print("Hata oluştu:", e)
    finally:
        if min_price_info == 999999999:
            return 0
        else:
            return min_price_info