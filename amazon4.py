
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time
import fuzzy
import unidecode
from sentence_transformers import SentenceTransformer, util

def normalizeWord(word):
    return unidecode.unidecode(word)    #convert our code with respect to the ASCII code 

def getSoundex(word):
    soundex = fuzzy.Soundex(4)
    normalizedWord = normalizeWord(word)      #set our word to the normalized word
    return soundex(normalizedWord)

def soundexSimilarity(soundex1, soundex2):
    if soundex1 == soundex2:            #check our name is similiar to the our search quary
        return True
    elif soundex1[:30] == soundex2[:30]:  # control first 30 cases
        return True
    else:
        return False

def extractName(newName, names):
    if newName not in names:
        names.append(newName)        #clean out our name list 
        return True
    return False

def containsAllQueryWords(productName, queryWords):
    productName = productName.lower()                     #check if the quary word is in the found word
    return all(word in productName for word in queryWords)

def operations33(searchQuery):

    #start chrome web driver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")     #disable notifications
    service = Service("/Users/mehmethakanguven/Desktop/Visual_Studio/chromedriver")     #enter webdriver locaiton
    #options.add_argument('--headless')  
    #options.add_argument('--disable-gpu')      #for our webdriver work at background
    #options.add_argument('--no-sandbox')
    #huoptions.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    targetSoundex = getSoundex(searchQuery)  #set our target word
    
    try:
        driver.get('https://www.amazon.com.tr/')      #enter the target link 

        try:
            searchBox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'twotabsearchtextbox'))
            )   #fint search box
            searchBox.send_keys(searchQuery)      #enter our search quary
            searchBox.send_keys(Keys.RETURN)       #press enter
        except Exception as e:
            print("Arama kutusu bulunamadı veya bir hata oluştu:", e)

        time.sleep(5)   #wait for the page
        
        #take the source of the page and start processing it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'lxml')    
        products = soup.find_all("div", attrs={"class": "s-main-slot"})
        nameSave = "a"      #create a variable for temp name 
        searchQuery = searchQuery.lower()   #make all cases lower
        names = []      #list for names
        minPriceInfo = 99999999     #SET FIRST PRICE 
        queryWords = searchQuery.split()  # Split the search quary
        minimumURL = ""

        procductCount = 0           #create the count variables
        maxProcductNumber = 10  

        for product in products:
            if procductCount >= maxProcductNumber:      #check the count
                break

            #find the top placed products
            productLink = product.find("div", class_= "a-section a-spacing-none")
            productLinks = productLink.find_all("a", attrs={"class": "a-link-normal"})
            
            for a_tag in productLinks:
                ourURL = a_tag.get("href")      #get the link
                if ourURL:
                    try:   
                        detail = requests.get(ourURL)       #get new page source code and start processing
                        detailSoup = BeautifulSoup(detail.text, "html.parser")

                        title = detailSoup.find(id='productTitle')  #find the products name 
                        if title:
                            titleText = title.get_text(strip=True)
                        else:
                            titleText = "Ürün ismi bulunamadı"

                        #fint the products price
                        price = detailSoup.find('span', {'class': 'a-price-whole'})
                        if price:
                            priceText = price.get_text(strip=True)
                        else:
                            price = detailSoup.find('span', {'class': 'a-price'})
                            if price:
                                priceText = price.get_text(strip=True)
                            else:
                                priceText = "Fiyat bulunamadı"
                        
                        if priceText != "Fiyat bulunamadı":
                            priceText = priceText.replace(",", ".") + " TL"  #organize the price value
                        
                        #check all possibilities and if OK, continue
                        if titleText != nameSave and extractName(titleText, names) and priceText != "Fiyat bulunamadı":
                            productNameLower = titleText.lower()
                            if soundexSimilarity(getSoundex(titleText), targetSoundex):    #check similarity
                                print(f"Ürün İsmi: {titleText}")        #print prices
                                print(f"Ürün Fiyatı: {priceText}\n")
                                priceText = priceText.replace(" TL", "").replace(",", ".")  #organize the price value
                                priceText = float(priceText)
                                if priceText <= minPriceInfo:
                                    minPriceInfo = priceText
                                    minimumURL = titleText       #set new minimum price and URL

                                isimUnutma = titleText
                        #set the name 
                        if isimUnutma != "Ürün ismi bulunamadı":
                            isimUnutma = titleText  
                       
                    except Exception as e:
                        continue

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".s-main-slot"))
        )   #enter main products class

        procductCount = 0           #create the count variables
        maxProcductNumber = 10  

        while procductCount < maxProcductNumber:
            #get new page source code and start processing
            soup = BeautifulSoup(driver.page_source, 'lxml')
            products = soup.find("div", class_="s-main-slot")
            productLinks = products.find_all("a", attrs={"class": "a-link-normal"})

            for a_tag in productLinks:
                semiLink = a_tag.get("href")    #fint the products link
                if semiLink and procductCount < maxProcductNumber:
                    newLink = "https://www.amazon.com.tr/" + semiLink   #create a useful link
                    try:
                        detail = requests.get(newLink)  #get new pages source code and start processing
                        detailSoup = BeautifulSoup(detail.text, "html.parser")
                        
                        #find product name
                        title = detailSoup.find(id='productTitle')
                        if title:
                            titleText = title.get_text(strip=True)
                        else:
                            titleText = "Ürün ismi bulunamadı"

                        #find product price
                        price = detailSoup.find('span', {'class': 'a-price-whole'})
                        if price:
                            priceText = price.get_text(strip=True)
                        else:
                            price = detailSoup.find('span', {'class': 'a-price'})
                            if price:
                                priceText = price.get_text(strip=True)
                            else:
                                priceText = "Fiyat bulunamadı"
                            
                        if priceText != "Fiyat bulunamadı":
                            priceText = priceText.replace(",", "") + " TL"  #organize the price value

                        #check all possibilities and if OK, continue
                        if titleText != "Ürün ismi bulunamadı" and extractName(titleText, names):
                            product_name_lower = titleText.lower()
                            query_embedding = model.encode(searchQuery, convert_to_tensor=True)
                            product_embeddings = model.encode(titleText, convert_to_tensor=True)
                            cosine_score = util.pytorch_cos_sim(query_embedding, product_embeddings)
                            if soundexSimilarity(getSoundex(titleText), targetSoundex) and cosine_score.item() >=  0.70:     #check similarity
                                print(f"Ürün İsmi: {titleText}")
                                print(f"Ürün Fiyatı: {priceText}\n")
                                priceText = priceText.replace(" TL", "").replace(",", ".")  #organize the price value
                                priceText = float(priceText)
                                if priceText <= minPriceInfo:
                                    minPriceInfo = priceText
                                    minimumURL = titleText        #set new minimum price and URL
                                procductCount += 1
                        
                    except Exception as e:
                        print(f"Detay sayfasına erişim başarısız: {e}")

            if procductCount >= maxProcductNumber:
                break       #check the count values
        
        driver.quit()       #close the webdriver
    except Exception as e:
        print("Hata oluştu:", e)
    finally:
        if minPriceInfo == 999999999:
            return 0                  #return the minimum price and if there is no price return 0  
        else:
            return minPriceInfo, minimumURL