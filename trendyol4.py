

import fuzzy
import re
import time
import pandas as pd
import requests
import unidecode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from thefuzz import fuzz


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

def contains_all_query_words(product_name, query_words):
    product_name = product_name.lower()
    return all(word in product_name for word in query_words)

def islemler3(search_query):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    service = Service("/Users/mehmethakanguven/Desktop/Visual_Studio/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    target_soundex = get_soundex(search_query)

    try:
        driver.get('https://www.trendyol.com/')

        try:
            accept_cookies_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
            )
            accept_cookies_button.click()
        except Exception as e:
            print("Çerez kabul butonu bulunamadı veya bir hata oluştu:", e)

        try:
            search_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Aradığınız ürün, kategori veya markayı yazınız"]'))
            )
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
        except Exception as e:
            print("Arama kutusu bulunamadı veya bir hata oluştu:", e)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        r = requests.get(driver.current_url)
        time.sleep(5)

        soup = BeautifulSoup(r.content, 'lxml')
        urunler = soup.find_all("div", attrs={"class": "with-campaign-view"})
        min_price = 999999999
        min_price_info = ""
        min_seller_info = ""
        search_query = search_query.lower()
        query_words = search_query.split()  # Arama kelimelerini ayırıyoruz
        j = 0

        for urun in urunler:
            urun_linkleri = urun.find_all("div", attrs={"class": "p-card-chldrn-cntnr"})
            for link in urun_linkleri:
                a_tag = link.find("a")
                if a_tag:
                    link_devam = a_tag.get("href")
                    link_ekle = "http://trendyol.com" + link_devam
                    detay = requests.get(link_ekle)
                    detay_soup = BeautifulSoup(detay.content, "lxml")
                    df = pd.DataFrame(columns=['Satıcı', 'Fiyat'])

                    product_name = detay_soup.find("h1", class_="pr-new-br").get_text(strip=True)
                    product_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', product_name)
                    product_name_lower = product_name.lower()

                    # Hem soundex hem de kelime eşleşmesini kontrol ediyoruz
                    if fuzz.partial_token_sort_ratio(product_name,search_query) >= 43:
                        print("\n\nÜrünün Adı: " + product_name)
                        min_price = 999999999
                        min_price_info = ""

                        ana_fiyat_icin = detay_soup.find("div", class_="pr-bx-nm with-org-prc")
                        if ana_fiyat_icin:
                            fiyat_span = ana_fiyat_icin.find("span", class_="prc-dsc")
                            if fiyat_span:
                                fiyat_text = fiyat_span.get_text(strip=True)
                                fiyat_text = re.sub(r'[^\d,]', '', fiyat_text)
                                fiyat_text = fiyat_text.replace(',', '.')
                                try:
                                    fiyat_float = float(fiyat_text)
                                    df.loc[len(df)] = ["Sayfa Fiyatı", fiyat_text + " TL"]

                                    if fiyat_float < min_price:
                                        min_price = fiyat_float
                                        min_price_info = fiyat_float
                                        min_seller_info = "Sayfa Fiyatı"

                                except ValueError:
                                    print(f"Fiyat dönüştürülemedi: {fiyat_text}")
                            else:
                                print("Fiyat bilgisi bulunamadı.")
                                j += 1
                        else:
                            print("Fiyat bölümü bulunamadı.")
                            j += 1

                        seller_info = detay_soup.find_all("div", class_="seller-container")
                        for seller in seller_info:
                            seller_name = seller.find("a")
                            if seller_name:
                                seller_name_text = seller_name.get("title")
                                price_tag = seller.find_next("span", class_="prc-dsc")
                                if price_tag:
                                    price = price_tag.get_text(strip=True)
                                    price = re.sub(r'[^\d,]', '', price).replace(',', '.')
                                    try:
                                        price_float = float(price)
                                        if price_float < min_price:
                                            min_price = price_float
                                            min_price_info = price_float
                                            min_seller_info = seller_name_text
                                        df.loc[len(df)] = [seller_name_text, price + " TL"]

                                    except ValueError:
                                        print(f"Fiyat dönüştürülemedi: {price}")

                        if j == 0:
                            df.loc[len(df)] = ["En ucuz satıcı ve fiyatı", min_price_info]
                            df = df.map(lambda x: str(x).ljust(30))
                            print("\n", df, "\n")

                        min_price = 999999999
                        j = 0

        driver.quit()
    except Exception as e:
        print("Hata oluştu:", e)
    finally:
        if min_price_info == 999999999:
            return 0
        else:
            #min_price_info = '{:,.0f}'.format(min_price_info)
            #min_price_info = min_price_info.replace(',', '.')
            return min_price_info
