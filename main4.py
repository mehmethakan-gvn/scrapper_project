'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import pandas as pd
from trendyol4 import islemler3
from amazon4 import islemler33
import mysql.connector
from datetime import date

class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"
        self.layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=10)
        
        self.search_input = TextInput(hint_text='Ürün Adı Girin', size_hint_y=None, height=100)
        self.layout.add_widget(self.search_input)
        
        search_button = Button(text='Ara', size_hint_y=None, height=90)
        search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(search_button)
        
        self.results_layout = GridLayout(cols=1, size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.results_layout)
        self.layout.add_widget(scroll_view)
        
        return self.layout

    
    def on_search_button_click(self, instance):
        search_query = self.search_input.text
        results = self.islemler(search_query)
        self.results_layout.clear_widgets()
        if results:
            for result in results:
                product_label = Label(text=f"Ürünün Adı: {result['product']}", bold=True, size_hint_y=None, height=50)
                self.results_layout.add_widget(product_label)

                if not result['sellers']:
                    self.results_layout.add_widget(Label(text="Fiyat bilgisi bulunamadı", size_hint_y=None, height=30))
                else:
                    for seller_info in result['sellers']:
                        seller_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                        
                        seller_label = Label(text=f"{seller_info['seller']}", size_hint_x=0.5, halign='center', valign='middle')
                        price_label = Label(text=f"{seller_info['price']}", size_hint_x=0.5, halign='center', valign='middle')
                        
                        seller_label.bind(size=seller_label.setter('text_size'))  
                        price_label.bind(size=price_label.setter('text_size'))  
                        
                        seller_layout.add_widget(seller_label)
                        seller_layout.add_widget(price_label)
                        
                        self.results_layout.add_widget(seller_layout)
                
                self.results_layout.add_widget(Label(text="", size_hint_y=None, height=20)) 
                self.results_layout.add_widget(Label(text="", size_hint_y=None, height=20))
        else:
            self.results_layout.add_widget(Label(text="Sonuç bulunamadı", size_hint_y=None, height=40))

    def connect_to_database(db):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Mehmet_1450*Hakanmysql',
                database=db
            )
            return connection
        except mysql.connector.Error as err:
            print(f"Veritabanı bağlantı hatası: {err}")
            return None

    def create_table_if_not_exists(cursor, name):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(255) UNIQUE,
            trendyol_min VARCHAR(255),
            amazon_min VARCHAR(255),
            tarih DATE
        )
        """
        cursor.execute(create_table_query)

    def create_table_if_not_exists2(cursor, name):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            trendyol_min VARCHAR(255),
            amazon_min VARCHAR(255),
            tarih DATE
        )
        """
        cursor.execute(create_table_query)

    def insert_or_update_data(cursor, product_name, trendyol_min, amazon_min, tarih):
        insert_query = """
        INSERT INTO products (product_name, trendyol_min, amazon_min, tarih)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            trendyol_min = VALUES(trendyol_min),
            amazon_min = VALUES(amazon_min),
            tarih = VALUES(tarih)
        """
        cursor.execute(insert_query, (product_name, trendyol_min, amazon_min, tarih))

    def insert_new_row(name, cursor, trendyol_min, amazon_min, tarih):
        insert_query = f"""
        INSERT INTO `{name}` (trendyol_min, amazon_min, tarih)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (trendyol_min, amazon_min, tarih))

    def check_product_in_database(cursor, product_name):
        select_query = "SELECT product_name, trendyol_min, amazon_min, tarih FROM products WHERE product_name = %s"
        cursor.execute(select_query, (product_name,))
        return cursor.fetchone()

    def print_all_rows(cursor, table_name):
        select_query = f"SELECT * FROM `{table_name}`"
        cursor.execute(select_query)
        results = cursor.fetchall()

        if results:
            print(f"{table_name} tablosundaki tüm satırlar:\n")
            for row in results:
                print(row)
        else:
            print(f"{table_name} tablosunda veri bulunamadı.")

    def uygulama(search_query, cursor, cursor2, search_query2):
        print(f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n")
            
        tarih = date.today()

        print("Trendyol çalışıyor: \n\n")
        trendyol_price = islemler3(search_query=search_query)

        print("\n\nAmazon çalışıyor: \n\n")
        amazon_price = islemler33(search_query=search_query)

        insert_or_update_data(cursor, search_query, trendyol_price, amazon_price, tarih)
        insert_new_row(search_query2, cursor2, trendyol_price, amazon_price, tarih)
        print(f"'{search_query}' ürünü için veritabanına yeni veri eklendi.")

    def main():
        df = pd.DataFrame(columns=['Satıcı', 'Fiyat'])
        pd.set_option('display.colheader_justify', 'left')

        connection = connect_to_database("trendyol_veriler")
        if connection is None:
            return

        cursor = connection.cursor()
        create_table_if_not_exists(cursor, "products")

        search_query = input("Aranacak ürün adını girin: ")
        search_query2 = search_query.replace(" ", "_")

        cursor2 = connection.cursor()
        create_table_if_not_exists2(cursor2, search_query2)

        product_data = check_product_in_database(cursor, search_query)

        if product_data:
            print(f"\n{product_data[0]} veritabanında bulundu:")
            print(f"Trendyol Fiyatı: {product_data[1]}")
            print(f"Amazon Fiyatı: {product_data[2]}")
            print(f"Tarih: {product_data[3]}\n")

            cevap = input("Verileri güncellemek için tekrar arama yapmak ister misiniz (evet ya da hayır giriniz): ")
            if cevap == "evet":
                uygulama(search_query, cursor, cursor2,search_query2)
        else:
            uygulama(search_query, cursor, cursor2, search_query2)

        print("\nFiyat geçmişi: ")
        print_all_rows(cursor2, search_query2)

        print("\nProgram kapanıyor...\n")
        connection.commit()
        cursor.close()
        cursor2.close()
        connection.close()

if __name__ == "__main__":
    main()

    '''

'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"
        self.layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=10)
        
        self.search_input = TextInput(hint_text='Ürün Adı Girin', size_hint_y=None, height=100)
        self.layout.add_widget(self.search_input)
        
        search_button = Button(text='Ara', size_hint_y=None, height=90)
        search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(search_button)
        
        self.results_layout = GridLayout(cols=1, size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.results_layout)
        self.layout.add_widget(scroll_view)
        
        return self.layout

    def on_search_button_click(self, instance):
        search_query = self.search_input.text
        results = self.search_database(search_query)

        if not results:
            results = self.web_search(search_query)
            self.save_to_database(results)

        self.display_results(results)

    def search_database(self, search_query):
        # Burada veritabanını kontrol eden kod olacak
        # Eğer veritabanında ürün varsa, bu fonksiyon sonuçları döndürür
        # Örnek veri:
        return []  # Eğer veritabanında veri yoksa boş bir liste döndürür

    def web_search(self, search_query):
        # Burada Trendyol ve Amazon'dan arama yapacak kodu ekleyin
        # islemler3 ve islemler33 fonksiyonlarını çağırarak
        # Örnek sonuç:
        return [
            {
                "product": search_query,
                "sellers": [
                    {"seller": "Satıcı 1", "price": "100 TL"},
                    {"seller": "Satıcı 2", "price": "105 TL"}
                ]
            }
        ]

    def save_to_database(self, results):
        # Bu fonksiyon, sonuçları veritabanına kaydetmek için kullanılacak
        pass

    def display_results(self, results):
        self.results_layout.clear_widgets()
        if results:
            for result in results:
                product_label = Label(text=f"Ürünün Adı: {result['product']}", bold=True, size_hint_y=None, height=50)
                self.results_layout.add_widget(product_label)

                if not result['sellers']:
                    self.results_layout.add_widget(Label(text="Fiyat bilgisi bulunamadı", size_hint_y=None, height=30))
                else:
                    for seller_info in result['sellers']:
                        seller_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                        
                        seller_label = Label(text=f"{seller_info['seller']}", size_hint_x=0.5, halign='center', valign='middle')
                        price_label = Label(text=f"{seller_info['price']}", size_hint_x=0.5, halign='center', valign='middle')
                        
                        seller_label.bind(size=seller_label.setter('text_size'))  
                        price_label.bind(size=price_label.setter('text_size'))  
                        
                        seller_layout.add_widget(seller_label)
                        seller_layout.add_widget(price_label)
                        
                        self.results_layout.add_widget(seller_layout)
                
                self.results_layout.add_widget(Label(text="", size_hint_y=None, height=20)) 
            
            self.add_action_buttons()  # Add buttons below the results
        else:
            self.results_layout.add_widget(Label(text="Sonuç bulunamadı", size_hint_y=None, height=40))

    def add_action_buttons(self):
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        retry_button = Button(text="Yeniden Ara")
        retry_button.bind(on_release=self.on_retry_button_click)
        
        history_button = Button(text="Fiyat Geçmişi")
        history_button.bind(on_release=self.on_history_button_click)
        
        close_button = Button(text="Kapat")
        close_button.bind(on_release=self.on_close_button_click)
        
        button_layout.add_widget(retry_button)
        button_layout.add_widget(history_button)
        button_layout.add_widget(close_button)
        
        self.results_layout.add_widget(button_layout)

    def on_retry_button_click(self, instance):
        self.results_layout.clear_widgets()
        self.search_input.text = ""

    def on_history_button_click(self, instance):
        # Implement functionality to display price history
        pass

    def on_close_button_click(self, instance):
        App.get_running_app().stop()

    


if __name__ == "__main__":
    TrendyolApp().run()

'''

'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
import pandas as pd
from trendyol4 import islemler3
from amazon4 import islemler33
import mysql.connector
from datetime import date

def connect_to_database(db):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mehmet_1450*Hakanmysql',
            database=db
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def create_table_if_not_exists(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE,
        trendyol_min VARCHAR(255),
        amazon_min VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def create_table_if_not_exists2(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        trendyol_min VARCHAR(255),
        amazon_min VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def insert_or_update_data(cursor, product_name, trendyol_min, amazon_min, tarih):
    insert_query = """
    INSERT INTO products (product_name, trendyol_min, amazon_min, tarih)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        trendyol_min = VALUES(trendyol_min),
        amazon_min = VALUES(amazon_min),
        tarih = VALUES(tarih)
    """
    cursor.execute(insert_query, (product_name, trendyol_min, amazon_min, tarih))

def insert_new_row(name, cursor, trendyol_min, amazon_min, tarih):
    insert_query = f"""
    INSERT INTO `{name}` (trendyol_min, amazon_min, tarih)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (trendyol_min, amazon_min, tarih))

def check_product_in_database(cursor, product_name):
    select_query = "SELECT product_name, trendyol_min, amazon_min, tarih FROM products WHERE product_name = %s"
    cursor.execute(select_query, (product_name,))
    return cursor.fetchone()

def print_all_rows(cursor, table_name):
    select_query = f"SELECT * FROM `{table_name}`"
    cursor.execute(select_query)
    results = cursor.fetchall()

    if results:
        print(f"{table_name} tablosundaki tüm satırlar:\n")
        for row in results:
            print(row)
    else:
        print(f"{table_name} tablosunda veri bulunamadı.")

class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"
        return self.build_interface()

    def build_interface(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Arama kutusu
        self.search_input = TextInput(hint_text="Aramak istediğiniz ürünü girin", size_hint=(1, None), height=40)
        self.layout.add_widget(self.search_input)
        
        # Arama butonu
        self.search_button = Button(text="Ara", size_hint=(1, None), height=50)
        self.search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(self.search_button)

        # Sonuçları göstermek için Label
        self.result_label = Label(text="", halign="left", valign="top", size_hint=(1, 1))
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        return self.layout

    def on_search_button_click(self, instance):
        search_query = self.search_input.text.strip()
        
        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            create_table_if_not_exists(cursor, "products")

            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")
            create_table_if_not_exists2(cursor2, search_query2)

            product_data = check_product_in_database(cursor, search_query)

            if product_data:
                self.result_label.text = f"{product_data[0]} veritabanında bulundu:\n" \
                                         f"Trendyol Fiyatı: {product_data[1]}\n" \
                                         f"Amazon Fiyatı: {product_data[2]}\n" \
                                         f"Tarih: {product_data[3]}"
                self.show_buttons(search_query, cursor, cursor2, search_query2)
            else:
                self.result_label.text = f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n"
                self.uygulama(search_query, cursor, cursor2, search_query2)

            connection.commit()
            cursor.close()
            cursor2.close()
            connection.close()

    def uygulama(self, search_query, cursor, cursor2, search_query2):
        tarih = date.today()

        self.result_label.text += "Trendyol çalışıyor...\n"
        trendyol_price = islemler3(search_query=search_query)

        self.result_label.text += "Amazon çalışıyor...\n"
        amazon_price = islemler33(search_query=search_query)

        insert_or_update_data(cursor, search_query, trendyol_price, amazon_price, tarih)
        insert_new_row(search_query2, cursor2, trendyol_price, amazon_price, tarih)
        
        self.result_label.text += f"'{search_query}' ürünü için veritabanına yeni veri eklendi.\n"
        self.show_buttons(search_query, cursor, cursor2, search_query2)

    def show_buttons(self, search_query, cursor, cursor2, search_query2):
        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)

        self.new_search_button = Button(text="Yeniden Ara")
        self.new_search_button.bind(on_release=lambda x: self.uygulama(search_query, cursor, cursor2, search_query2))
        self.button_layout.add_widget(self.new_search_button)

        self.price_history_button = Button(text="Fiyat Geçmişi")
        self.price_history_button.bind(on_release=lambda x: self.show_price_history(cursor2, search_query2))
        self.button_layout.add_widget(self.price_history_button)

        self.close_button = Button(text="Kapat")
        self.close_button.bind(on_release=lambda x: self.stop())
        self.button_layout.add_widget(self.close_button)

        self.layout.add_widget(self.button_layout)

    def show_price_history(self, cursor2, search_query2):
        price_history = ""
        select_query = f"SELECT * FROM `{search_query2}`"
        cursor2.execute(select_query)
        results = cursor2.fetchall()

        if results:
            for row in results:
                price_history += f"Trendyol: {row[1]}, Amazon: {row[2]}, Tarih: {row[3]}\n"
        else:
            price_history = "Fiyat geçmişi bulunamadı."
        
        self.result_label.text = price_history

if __name__ == '__main__':
    TrendyolApp().run()

'''

'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
import pandas as pd
from trendyol4 import islemler3
from amazon4 import islemler33
import mysql.connector
from datetime import date

def connect_to_database(db):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mehmet_1450*Hakanmysql',
            database=db
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def create_table_if_not_exists(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE,
        trendyol_min VARCHAR(255),
        amazon_min VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def create_table_if_not_exists2(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        trendyol_min VARCHAR(255),
        amazon_min VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def insert_or_update_data(cursor, product_name, trendyol_min, amazon_min, tarih):
    insert_query = """
    INSERT INTO products (product_name, trendyol_min, amazon_min, tarih)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        trendyol_min = VALUES(trendyol_min),
        amazon_min = VALUES(amazon_min),
        tarih = VALUES(tarih)
    """
    cursor.execute(insert_query, (product_name, trendyol_min, amazon_min, tarih))

def insert_new_row(name, cursor, trendyol_min, amazon_min, tarih):
    insert_query = f"""
    INSERT INTO `{name}` (trendyol_min, amazon_min, tarih)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (trendyol_min, amazon_min, tarih))

def check_product_in_database(cursor, product_name):
    select_query = "SELECT product_name, trendyol_min, amazon_min, tarih FROM products WHERE product_name = %s"
    cursor.execute(select_query, (product_name,))
    return cursor.fetchone()

class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"
        return self.build_interface()

    def build_interface(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Arama kutusu
        self.search_input = TextInput(hint_text="Aramak istediğiniz ürünü girin", size_hint=(1, None), height=40)
        self.layout.add_widget(self.search_input)
        
        # Arama butonu
        self.search_button = Button(text="Ara", size_hint=(1, None), height=50)
        self.search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(self.search_button)

        # Sonuçları göstermek için Label
        self.result_label = Label(text="", halign="left", valign="top", size_hint=(1, 1))
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        return self.layout

    def on_search_button_click(self, instance):
        search_query = self.search_input.text.strip()
        
        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            create_table_if_not_exists(cursor, "products")

            search_query2 = search_query.replace(" ", "_")
            create_table_if_not_exists2(cursor, search_query2)

            product_data = check_product_in_database(cursor, search_query)

            if product_data:
                self.result_label.text = f"{product_data[0]} veritabanında bulundu:\n" \
                                         f"Trendyol Fiyatı: {product_data[1]}\n" \
                                         f"Amazon Fiyatı: {product_data[2]}\n" \
                                         f"Tarih: {product_data[3]}"
                connection.commit()
                cursor.close()
                connection.close()

                self.show_buttons(search_query, search_query2)
            else:
                self.result_label.text = f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n"
                self.uygulama(search_query, search_query2)

                connection.commit()
                cursor.close()
                connection.close()

    def uygulama(self, search_query, search_query2):
        tarih = date.today()

        connection = connect_to_database("trendyol_veriler")
        cursor = connection.cursor()

        self.result_label.text += "Trendyol çalışıyor...\n"
        trendyol_price = islemler3(search_query=search_query)

        self.result_label.text += "Amazon çalışıyor...\n"
        amazon_price = islemler33(search_query=search_query)

        insert_or_update_data(cursor, search_query, trendyol_price, amazon_price, tarih)
        insert_new_row(search_query2, cursor, trendyol_price, amazon_price, tarih)
        
        self.result_label.text += f"'{search_query}' ürünü için veritabanına yeni veri eklendi.\n"

        connection.commit()
        cursor.close()
        connection.close()

        self.show_buttons(search_query, search_query2)

    def show_buttons(self, search_query, search_query2):
        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)

        self.new_search_button = Button(text="Yeniden Ara")
        self.new_search_button.bind(on_release=lambda x: self.uygulama(search_query, search_query2))
        self.button_layout.add_widget(self.new_search_button)

        self.price_history_button = Button(text="Fiyat Geçmişi")
        self.price_history_button.bind(on_release=lambda x: self.show_price_history(search_query2))
        self.button_layout.add_widget(self.price_history_button)

        self.close_button = Button(text="Kapat")
        self.close_button.bind(on_release=lambda x: self.stop())
        self.button_layout.add_widget(self.close_button)

        self.layout.add_widget(self.button_layout)

    def show_price_history(self, search_query2):
        price_history = ""
        connection = connect_to_database("trendyol_veriler")
        cursor = connection.cursor()

        select_query = f"SELECT * FROM `{search_query2}`"
        cursor.execute(select_query)
        results = cursor.fetchall()

        if results:
            for row in results:
                price_history += f"Trendyol: {row[1]}, Amazon: {row[2]}, Tarih: {row[3]}\n"
        else:
            price_history = "Fiyat geçmişi bulunamadı."
        
        self.result_label.text = price_history

        cursor.close()
        connection.close()

if __name__ == '__main__':
    TrendyolApp().run()

'''

'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import mysql.connector
from datetime import date
from trendyol4 import operations3
from amazon4 import operations33
from n11 import operaitons333

def connect_to_database(db):
    try:        #connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mehmet_1450*Hakanmysql',
            database=db
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def create_table_if_not_exists(cursor, name):   #create table if not exists
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE,
        trendyol_min VARCHAR(255),
        amazon_min VARCHAR(255),
        n11_min VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def create_table_if_not_exists2(cursor, name):  #create table if not exists
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        trendyol_min VARCHAR(255),
        amazon_min VARCHAR(255),
        n11_min VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def insert_or_update_data(cursor, product_name, trendyol_min, amazon_min, n11_min, tarih):
    insert_query = """      
    INSERT INTO products (product_name, trendyol_min, amazon_min, tarih)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        trendyol_min = VALUES(trendyol_min),
        amazon_min = VALUES(amazon_min),
        n11_min = VALUES(n11_min)
        tarih = VALUES(tarih)
    """     #insert or update data
    cursor.execute(insert_query, (product_name, trendyol_min, amazon_min, n11_min, tarih))

def insert_new_row(name, cursor, trendyol_min, amazon_min, n11_min, tarih):
    insert_query = f"""
    INSERT INTO `{name}` (trendyol_min, amazon_min, n11_min, tarih)
    VALUES (%s, %s, %s, %s)
    """     #add new row into the products table
    cursor.execute(insert_query, (trendyol_min, amazon_min, n11_min, tarih))

def check_product_in_database(cursor, product_name):    #check product in database
    select_query = "SELECT product_name, trendyol_min, amazon_min, tarih FROM products WHERE product_name = %s"
    cursor.execute(select_query, (product_name,))
    return cursor.fetchone()

class TrendyolApp(App):     #main class for kivy interface
    def build(self):
        self.title = "Ürün Arama"       #set the self
        return self.build_interface()

    def build_interface(self): #add main buttons and set what they do
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search box
        self.search_input = TextInput(hint_text="Aramak istediğiniz ürünü girin", size_hint=(1, None), height=40)
        self.layout.add_widget(self.search_input)

        # Search button
        self.search_button = Button(text="Ara", size_hint=(1, None), height=50)
        self.search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(self.search_button)

        # Label to show results
        self.result_label = Label(text="", halign="left", valign="top", size_hint=(1, 1))
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        # A horizontal layout to keep the buttons stable
        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)

        # Redial button
        self.new_search_button = Button(text="Yeniden Ara")
        self.new_search_button.bind(on_release=self.on_new_search_button_click)
        self.button_layout.add_widget(self.new_search_button)

        # Price History button
        self.price_history_button = Button(text="Fiyat Geçmişi")
        self.price_history_button.bind(on_release=self.on_price_history_button_click)
        self.button_layout.add_widget(self.price_history_button)

        # close button
        self.close_button = Button(text="Kapat")
        self.close_button.bind(on_release=lambda x: self.stop())
        self.button_layout.add_widget(self.close_button)

        #Add buttons to main layout
        self.layout.add_widget(self.button_layout)

        return self.layout

    def on_search_button_click(self, instance): 
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")        #connect to the database
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()    #start connection
            create_table_if_not_exists(cursor, "products")  #create table

            cursor2 = connection.cursor()   #start connection
            search_query2 = search_query.replace(" ", "_")  #organize the search quary
            create_table_if_not_exists2(cursor2, search_query2) #create table

            product_data = check_product_in_database(cursor, search_query)  #check the product is avaible at the database

            if product_data:    #get the datas
                self.result_label.text = f"{product_data[0]} veritabanında bulundu:\n" \
                                         f"Trendyol Fiyatı: {product_data[1]}\n" \
                                         f"Amazon Fiyatı: {product_data[2]}\n" \
                                         f"N11 Fiyatı: {product_data[3]}\n" \
                                         f"Tarih: {product_data[4]}"
            else:
                self.result_label.text = f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n"
                self.uygulama(search_query, cursor, cursor2, search_query2) #start scapping if there is no datas

            connection.commit()
            cursor.close()          #commit the changes and close the cursors and connection
            cursor2.close()
            connection.close()

    def application(self, search_query, cursor, cursor2, search_query2):    #main scrapping modules
        tarih = date.today()    #get date

        self.result_label.text += "Trendyol çalışıyor...\n"
        trendyol_price = operations3(searchQuery=search_query)  #enter trendyol scrapper

        self.result_label.text += "Amazon çalışıyor...\n"
        amazon_price = operations33(searchQuery=search_query)   #enter amazon scrapper

        #add new row at product table and price history table
        insert_or_update_data(cursor, search_query, trendyol_price, amazon_price, tarih)
        insert_new_row(search_query2, cursor2, trendyol_price, amazon_price, tarih)
        
        #print feedback message
        self.result_label.text += f"'{search_query}' ürünü için veritabanına yeni veri eklendi.\n"

    def on_new_search_button_click(self, instance):     #enter main scrapper functions
        search_query = self.search_input.text.strip()   #organize the search quary

        if search_query:
            connection = connect_to_database("trendyol_veriler")    #connect to database
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()        #connect the cursors
            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")      #organize the search quary

            self.application(search_query, cursor, cursor2, search_query2)  #enter main scrapper functions

            connection.commit()
            cursor.close()      #commit the values and close the cursors
            cursor2.close()
            connection.close()

    def on_price_history_button_click(self, instance):      #What to do when click on the price history button
        search_query = self.search_input.text.strip()
        if search_query:
            connection = connect_to_database("trendyol_veriler")    #connect the database
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor2 = connection.cursor()                   #connect the cursor 
            search_query2 = search_query.replace(" ", "_")  #organize the search quary

            price_history = ""
            select_query = f"SELECT * FROM `{search_query2}`"   #get the price history
            cursor2.execute(select_query)
            results = cursor2.fetchall()

            if results:
                for row in results:
                    #organize the price history
                    price_history += f"Trendyol: {row[1]}, Amazon: {row[2]}, Tarih: {row[3]}\n"
            else:
                price_history = "Fiyat geçmişi bulunamadı."

            self.result_label.text = price_history

            cursor2.close()     #close the cursors and the connection
            connection.close()

if __name__ == '__main__':
    TrendyolApp().run()         #start main program

    '''

'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import mysql.connector
from datetime import date
from trendyol4 import operations3
from amazon4 import operations33
from n11 import operations333  # N11 için eklenen kısım

def connect_to_database(db):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mehmet_1450*Hakanmysql',
            database=db
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def create_table_if_not_exists(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(255),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(255),
        n11_min VARCHAR(255),  # N11 sütunu eklendi
        n11_link VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def create_table_if_not_exists2(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(255),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(255),
        n11_min VARCHAR(255),  # N11 sütunu eklendi
        n11_link VARCHAR(255),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def insert_or_update_data(cursor, product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih):
    insert_query = """      
    INSERT INTO products (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        trendyol_min = VALUES(trendyol_min),
        amazon_min = VALUES(amazon_min),
        n11_min = VALUES(n11_min),  # N11 güncellemesi eklendi
        tarih = VALUES(tarih)
    """  
    cursor.execute(insert_query, (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih))

def insert_new_row(name, cursor, trendyol_min, amazon_min, n11_min, tarih):
    insert_query = f"""
    INSERT INTO `{name}` (trendyol_min, amazon_min, n11_min, tarih)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_query, (trendyol_min, amazon_min, n11_min, tarih))

def check_product_in_database(cursor, product_name):
    select_query = "SELECT product_name, trendyol_min, amazon_min, n11_min, tarih FROM products WHERE product_name = %s"
    cursor.execute(select_query, (product_name,))
    return cursor.fetchone()

class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"
        return self.build_interface()

    def build_interface(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.search_input = TextInput(hint_text="Aramak istediğiniz ürünü girin", size_hint=(1, None), height=60)
        self.layout.add_widget(self.search_input)

        self.search_button = Button(text="Ara", size_hint=(1, None), height=50)
        self.search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(self.search_button)

        self.result_label = Label(text="", halign="left", valign="top", size_hint=(1, 1))
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)

        self.new_search_button = Button(text="Yeniden Ara")
        self.new_search_button.bind(on_release=self.on_new_search_button_click)
        self.button_layout.add_widget(self.new_search_button)

        self.price_history_button = Button(text="Fiyat Geçmişi")
        self.price_history_button.bind(on_release=self.on_price_history_button_click)
        self.button_layout.add_widget(self.price_history_button)

        self.close_button = Button(text="Kapat")
        self.close_button.bind(on_release=lambda x: self.stop())
        self.button_layout.add_widget(self.close_button)

        self.layout.add_widget(self.button_layout)

        return self.layout

    def on_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            create_table_if_not_exists(cursor, "products")

            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")
            create_table_if_not_exists2(cursor2, search_query2)

            product_data = check_product_in_database(cursor, search_query)

            if product_data:
                self.result_label.text = f"{product_data[0]} veritabanında bulundu:\n" \
                                         f"Trendyol Fiyatı: {product_data[1]}\n" \
                                         f"Amazon Fiyatı: {product_data[2]}\n" \
                                         f"N11 Fiyatı: {product_data[3]}\n" \
                                         f"Tarih: {product_data[4]}"
            else:
                self.result_label.text = f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n"
                self.application(search_query, cursor, cursor2, search_query2)

            connection.commit()
            cursor.close()
            cursor2.close()
            connection.close()

    def application(self, search_query, cursor, cursor2, search_query2):
        tarih = date.today()

        self.result_label.text += "Trendyol çalışıyor...\n"
        trendyol_price = operations3(searchQuery=search_query)

        self.result_label.text += "Amazon çalışıyor...\n"
        amazon_price = operations33(searchQuery=search_query)

        self.result_label.text += "N11 çalışıyor...\n"
        n11_price = operations333(search_query=search_query)  # N11 işlemi eklendi

        insert_or_update_data(cursor, search_query, trendyol_price, amazon_price, n11_price, tarih)
        insert_new_row(search_query2, cursor2, trendyol_price, amazon_price, n11_price, tarih)
        
        self.result_label.text += f"'{search_query}' ürünü için veritabanına yeni veri eklendi.\n"

    def on_new_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")

            self.application(search_query, cursor, cursor2, search_query2)

            connection.commit()
            cursor.close()
            cursor2.close()
            connection.close()

    def on_price_history_button_click(self, instance):
        search_query = self.search_input.text.strip()
        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")

            price_history = ""
            select_query = f"SELECT * FROM `{search_query2}`"
            cursor2.execute(select_query)
            results = cursor2.fetchall()

            if results:
                for row in results:
                    price_history += f"Trendyol: {row[1]}, Amazon: {row[2]}, N11: {row[3]}, Tarih: {row[4]}\n"
                self.result_label.text = price_history
            else:
                self.result_label.text = "Fiyat geçmişi bulunamadı."

            cursor2.close()
            connection.close()

if __name__ == '__main__':
    TrendyolApp().run()
'''

'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
import mysql.connector
from datetime import date
from trendyol4 import operations3
from amazon4 import operations33
from n11 import operations333

def connect_to_database(db):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mehmet_1450*Hakanmysql',
            database=db
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def create_table_if_not_exists(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(2000),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(2000),
        n11_min VARCHAR(255),
        n11_link VARCHAR(2000),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def create_table_if_not_exists2(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(2000),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(2000),
        n11_min VARCHAR(255),
        n11_link VARCHAR(2000),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def insert_or_update_data(cursor, product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih):
    insert_query = """      
    INSERT INTO products (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        trendyol_min = VALUES(trendyol_min),
        trendyol_link = VALUES(trendyol_link),
        amazon_min = VALUES(amazon_min),
        amazon_link = VALUES(amazon_link),
        n11_min = VALUES(n11_min),
        n11_link = VALUES(n11_link),
        tarih = VALUES(tarih)
    """  
    cursor.execute(insert_query, (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih))

def insert_new_row(name, cursor, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih):
    insert_query = f"""
    INSERT INTO `{name}` (trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih))

def check_product_in_database(cursor, product_name):
    select_query = "SELECT product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih FROM products WHERE product_name = %s"
    cursor.execute(select_query, (product_name,))
    return cursor.fetchone()

class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"
        return self.build_interface()

    def build_interface(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.search_input = TextInput(hint_text="Aramak istediğiniz ürünü girin", size_hint=(1, None), height=50)
        self.layout.add_widget(self.search_input)

        self.search_button = Button(text="Ara", size_hint=(1, None), height=50)
        self.search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(self.search_button)

        self.result_label = Label(text="", halign="left", valign="top", size_hint=(1, 1))
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.result_label = Label(text="", halign="left", valign="top", size_hint_y=None, text_size=(self.width, None))
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.scroll_view.add_widget(self.result_label)
        self.layout.add_widget(self.scroll_view)

        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)

        self.new_search_button = Button(text="Yeniden Ara")
        self.new_search_button.bind(on_release=self.on_new_search_button_click)
        self.button_layout.add_widget(self.new_search_button)

        self.price_history_button = Button(text="Fiyat Geçmişi")
        self.price_history_button.bind(on_release=self.on_price_history_button_click)
        self.button_layout.add_widget(self.price_history_button)

        self.close_button = Button(text="Kapat")
        self.close_button.bind(on_release=lambda x: self.stop())
        self.button_layout.add_widget(self.close_button)

        self.layout.add_widget(self.button_layout)

        return self.layout

    def on_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            create_table_if_not_exists(cursor, "products")

            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")
            create_table_if_not_exists2(cursor2, search_query2)

            product_data = check_product_in_database(cursor, search_query)

            if product_data:
                self.result_label.text = f"{product_data[0]} veritabanında bulundu:\n" \
                                         f"Trendyol Fiyatı: {product_data[1]}, Link: {product_data[2]}\n\n" \
                                         f"Amazon Fiyatı: {product_data[3]}, Link: {product_data[4]}\n\n" \
                                         f"N11 Fiyatı: {product_data[5]}, Link: {product_data[6]}\n\n" \
                                         f"Tarih: {product_data[7]}\n\n\n"
            else:
                self.result_label.text = f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n"
                self.application(search_query, cursor, cursor2, search_query2)

            connection.commit()
            cursor.close()
            cursor2.close()
            connection.close()

    def application(self, search_query, cursor, cursor2, search_query2):
        tarih = date.today()

        self.result_label.text += "Trendyol çalışıyor...\n"
        trendyol_price, trendyol_link = operations3(searchQuery=search_query)  # Linkleri de döndürecek şekilde güncellendi

        self.result_label.text += "Amazon çalışıyor...\n"
        amazon_price, amazon_link = operations33(searchQuery=search_query)    # Linkleri de döndürecek şekilde güncellendi

        self.result_label.text += "N11 çalışıyor...\n"
        n11_price, n11_link = operations333(search_query=search_query)        # Linkleri de döndürecek şekilde güncellendi

        insert_or_update_data(cursor, search_query, trendyol_price, trendyol_link, amazon_price, amazon_link, n11_price, n11_link, tarih)
        insert_new_row(search_query2, cursor2, trendyol_price, trendyol_link, amazon_price, amazon_link, n11_price, n11_link, tarih)
        
        self.result_label.text += f"'{search_query}' ürünü için veritabanına yeni veri eklendi.\n"

    def on_new_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")

            self.application(search_query, cursor, cursor2, search_query2)

            connection.commit()
            cursor.close()
            cursor2.close()
            connection.close()

    def on_price_history_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            search_query2 = search_query.replace(" ", "_")

            try:
                select_query = f"SELECT trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih FROM `{search_query2}` ORDER BY tarih"
                cursor.execute(select_query)
                rows = cursor.fetchall()

                if rows:
                    result_text = f"{search_query} için fiyat geçmişi:\n"
                    for row in rows:
                        result_text += f"Trendyol: {row[0]} TL,\n Link: {row[1]},\n\n Amazon: {row[2]} TL,\n Link: {row[3]},\n\n N11: {row[4]} TL,\n Link: {row[5]},\n\n Arama Tarihi: {row[6]}\n"
                    self.result_label.text = result_text
                else:
                    self.result_label.text = f"{search_query} için fiyat geçmişi bulunamadı."

            except mysql.connector.Error as err:
                self.result_label.text = f"Fiyat geçmişi sorgu hatası: {err}"
            finally:
                cursor.close()
                connection.close()

if __name__ == "__main__":
    TrendyolApp().run()

'''

'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
import mysql.connector
from datetime import date
from trendyol4 import operations3
from amazon4 import operations33
from n11 import operations333

def connect_to_database(db):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mehmet_1450*Hakanmysql',
            database=db
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def create_table_if_not_exists(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(2000),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(2000),
        n11_min VARCHAR(255),
        n11_link VARCHAR(2000),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def create_table_if_not_exists2(cursor, name):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(2000),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(2000),
        n11_min VARCHAR(255),
        n11_link VARCHAR(2000),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

def insert_or_update_data(cursor, product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih):
    insert_query = """      
    INSERT INTO products (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        trendyol_min = VALUES(trendyol_min),
        trendyol_link = VALUES(trendyol_link),
        amazon_min = VALUES(amazon_min),
        amazon_link = VALUES(amazon_link),
        n11_min = VALUES(n11_min),
        n11_link = VALUES(n11_link),
        tarih = VALUES(tarih)
    """  
    cursor.execute(insert_query, (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih))

def insert_new_row(name, cursor, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih):
    insert_query = f"""
    INSERT INTO `{name}` (trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih))

def check_product_in_database(cursor, product_name):
    select_query = "SELECT product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih FROM products WHERE product_name = %s"
    cursor.execute(select_query, (product_name,))
    return cursor.fetchone()

class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"
        return self.build_interface()

    def build_interface(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.search_input = TextInput(hint_text="Aramak istediğiniz ürünü girin", size_hint=(1, None), height=60)
        self.layout.add_widget(self.search_input)

        self.search_button = Button(text="Ara", size_hint=(1, None), height=50)
        self.search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(self.search_button)

        # ScrollView ekleyerek yatay ve dikey kaydırmayı sağlıyoruz
        self.scroll_view = ScrollView(size_hint=(1, 1), bar_width=10)
        self.scroll_content = BoxLayout(orientation='vertical', size_hint_x=None, width=1000)
        self.scroll_view.add_widget(self.scroll_content)

        self.result_label = Label(text="", size_hint_x=None, width=1000, halign="left", valign="top")
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.scroll_content.add_widget(self.result_label)

        self.layout.add_widget(self.scroll_view)

        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)

        self.new_search_button = Button(text="Yeniden Ara")
        self.new_search_button.bind(on_release=self.on_new_search_button_click)
        self.button_layout.add_widget(self.new_search_button)

        self.price_history_button = Button(text="Fiyat Geçmişi")
        self.price_history_button.bind(on_release=self.on_price_history_button_click)
        self.button_layout.add_widget(self.price_history_button)

        self.close_button = Button(text="Kapat")
        self.close_button.bind(on_release=lambda x: self.stop())
        self.button_layout.add_widget(self.close_button)

        self.layout.add_widget(self.button_layout)

        return self.layout

    def on_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            create_table_if_not_exists(cursor, "products")

            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")
            create_table_if_not_exists2(cursor2, search_query2)

            product_data = check_product_in_database(cursor, search_query)

            if product_data:
                self.result_label.text = f"{product_data[0]} veritabanında bulundu:\n" \
                                         f"Trendyol Fiyatı: {product_data[1]}, Link: {product_data[2]}\n\n" \
                                         f"Amazon Fiyatı: {product_data[3]}, Link: {product_data[4]}\n\n" \
                                         f"N11 Fiyatı: {product_data[5]}, Link: {product_data[6]}\n\n" \
                                         f"Tarih: {product_data[7]}\n\n\n"
            else:
                self.result_label.text = f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n"
                self.application(search_query, cursor, cursor2, search_query2)

            connection.commit()
            cursor.close()
            cursor2.close()
            connection.close()

    def application(self, search_query, cursor, cursor2, search_query2):
        tarih = date.today()

        self.result_label.text += "Trendyol çalışıyor...\n"
        trendyol_price, trendyol_link = operations3(searchQuery=search_query)

        self.result_label.text += "Amazon çalışıyor...\n"
        amazon_price, amazon_link = operations33(searchQuery=search_query)

        self.result_label.text += "N11 çalışıyor...\n"
        n11_price, n11_link = operations333(search_query=search_query)

        insert_or_update_data(cursor, search_query, trendyol_price, trendyol_link, amazon_price, amazon_link, n11_price, n11_link, tarih)
        insert_new_row(search_query2, cursor2, trendyol_price, trendyol_link, amazon_price, amazon_link, n11_price, n11_link, tarih)
        
        self.result_label.text += f"'{search_query}' ürünü için veritabanına yeni veri eklendi.\n"

    def on_new_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            self.result_label.text = f"\n'{search_query}' için yeniden arama yapılıyor...\n"
            self.on_search_button_click(instance)

    def on_price_history_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()
            search_query2 = search_query.replace(" ", "_")
            self.result_label.text += f"'{search_query}' için fiyat geçmişi:\n"

            select_query = f"SELECT * FROM `{search_query2}` ORDER BY tarih DESC"
            cursor.execute(select_query)
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    self.result_label.text += f"Trendyol Fiyatı: {row[1]}, Link: {row[2]}\n" \
                                              f"Amazon Fiyatı: {row[3]}, Link: {row[4]}\n" \
                                              f"N11 Fiyatı: {row[5]}, Link: {row[6]}\n" \
                                              f"Tarih: {row[7]}\n\n"
            else:
                self.result_label.text += "Fiyat geçmişi bulunamadı.\n"

            cursor.close()
            connection.close()

if __name__ == '__main__':
    TrendyolApp().run()
'''


#liblaries here
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
import mysql.connector
from datetime import date
from trendyol4 import operations3
from amazon4 import operations33
from n11 import operations333

#connect to your database
def connect_to_database(db):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mehmet_1450*Hakanmysql',  
            database=db
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

#create main (products) tablo in your database
def create_table_if_not_exists(cursor, name):   
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(2000),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(2000),
        n11_min VARCHAR(255),
        n11_link VARCHAR(2000),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

#create table for price history and past scrapping results
def create_table_if_not_exists2(cursor, name): 
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        trendyol_min VARCHAR(255),
        trendyol_link VARCHAR(2000),
        amazon_min VARCHAR(255),
        amazon_link VARCHAR(2000),
        n11_min VARCHAR(255),
        n11_link VARCHAR(2000),
        tarih DATE
    )
    """
    cursor.execute(create_table_query)

#save new data in the products table and update if product exists 
def insert_or_update_data(cursor, product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih):
    insert_query = """      
    INSERT INTO products (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        trendyol_min = VALUES(trendyol_min),
        trendyol_link = VALUES(trendyol_link),
        amazon_min = VALUES(amazon_min),
        amazon_link = VALUES(amazon_link),
        n11_min = VALUES(n11_min),
        n11_link = VALUES(n11_link),
        tarih = VALUES(tarih)
    """  
    cursor.execute(insert_query, (product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih))

#save new data in the price history table
def insert_new_row(name, cursor, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih):
    insert_query = f"""
    INSERT INTO `{name}` (trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih))

#check the search query is already in the table and if so, get the values
def check_product_in_database(cursor, product_name):
    select_query = "SELECT product_name, trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih FROM products WHERE product_name = %s"
    cursor.execute(select_query, (product_name,))
    return cursor.fetchone()

#main class for kivy application
class TrendyolApp(App):
    def build(self):
        self.title = "Ürün Arama"   #create self 
        return self.build_interface()

    def build_interface(self):
        #The purpose of the following definitions is to create the buttons in the interface, 
        #determine their position and size, and activate scroll operations
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.search_input = TextInput(hint_text="Aramak istediğiniz ürünü girin", size_hint=(1, None), height=60)
        self.layout.add_widget(self.search_input)

        self.search_button = Button(text="Ara", size_hint=(1, None), height=50)
        self.search_button.bind(on_release=self.on_search_button_click)
        self.layout.add_widget(self.search_button)

        self.result_label = Label(text="", halign="left", valign="top", size_hint=(1, None), height=2000)
        self.result_label.bind(size=self.result_label.setter('text_size'))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.result_label)
        self.layout.add_widget(scroll_view)

        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)

        self.new_search_button = Button(text="Yeniden Ara")
        self.new_search_button.bind(on_release=self.on_new_search_button_click)
        self.button_layout.add_widget(self.new_search_button)

        self.price_history_button = Button(text="Fiyat Geçmişi")
        self.price_history_button.bind(on_release=self.on_price_history_button_click)
        self.button_layout.add_widget(self.price_history_button)

        self.close_button = Button(text="Kapat")
        self.close_button.bind(on_release=lambda x: self.stop())
        self.button_layout.add_widget(self.close_button)

        self.layout.add_widget(self.button_layout)

        return self.layout

    #main function for the operations when ueer click 'search' button. If the data is avaible in products table, get the values and print. 
    #If not, activate the scrapper liblaries and search values on the internet
    def on_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")    #connect to database
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()                        #conncet to database and create the the table
            create_table_if_not_exists(cursor, "products")

            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")       #conncet to database and create the second table
            create_table_if_not_exists2(cursor2, search_query2)

            product_data = check_product_in_database(cursor, search_query)  #get values on the database if exists

            if product_data:    #print datas
                self.result_label.text = f"{product_data[0]} veritabanında bulundu:\n" \
                                         f"Trendyol Fiyatı: {product_data[1]}, Adı: {product_data[2]}\n\n" \
                                         f"Amazon Fiyatı: {product_data[3]}, Adı: {product_data[4]}\n\n" \
                                         f"N11 Fiyatı: {product_data[5]}, Adı: {product_data[6]}\n\n" \
                                         f"Tarih: {product_data[7]}\n\n\n"
            else:
                self.result_label.text = f"\n{search_query} veritabanında bulunamadı. Şimdi arama yapılıyor...\n"
                self.application(search_query, cursor, cursor2, search_query2)  #start scrapping functions

            connection.commit()
            cursor.close()
            cursor2.close()
            connection.close()

    #main function for scrapping operations 
    def application(self, search_query, cursor, cursor2, search_query2):
        tarih = date.today()    #get operations date

        self.result_label.text += "Trendyol çalışıyor...\n" 
        trendyol_price, trendyol_link = operations3(searchQuery=search_query)  # start trendyol scrapper

        self.result_label.text += "Amazon çalışıyor...\n"
        amazon_price, amazon_link = operations33(searchQuery=search_query)    #start amazon scrapper

        self.result_label.text += "N11 çalışıyor...\n"
        n11_price, n11_link = operations333(search_query=search_query)        # start n11 scrapper

        #insert datas onto the tables
        insert_or_update_data(cursor, search_query, trendyol_price, trendyol_link, amazon_price, amazon_link, n11_price, n11_link, tarih)
        insert_new_row(search_query2, cursor2, trendyol_price, trendyol_link, amazon_price, amazon_link, n11_price, n11_link, tarih)
        
        self.result_label.text += f"'{search_query}' ürünü için veritabanına yeni veri eklendi.\n"

    #function of when the user click 'yeniden ara'
    def on_new_search_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")    #connect the database
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()        #conncet the cursor
            cursor2 = connection.cursor()
            search_query2 = search_query.replace(" ", "_")

            self.application(search_query, cursor, cursor2, search_query2)

            connection.commit()
            cursor.close()          #commit the changes and close connection
            cursor2.close()
            connection.close()

    #function of show price history and past scrapping results
    def on_price_history_button_click(self, instance):
        search_query = self.search_input.text.strip()

        if search_query:
            connection = connect_to_database("trendyol_veriler")    #connect to the database
            if connection is None:
                self.result_label.text = "Veritabanı bağlantısı başarısız oldu."
                return

            cursor = connection.cursor()        #connect cursor
            search_query2 = search_query.replace(" ", "_")

            try:
                select_query = f"SELECT trendyol_min, trendyol_link, amazon_min, amazon_link, n11_min, n11_link, tarih FROM `{search_query2}` ORDER BY tarih"
                cursor.execute(select_query)    #select the relevant table
                rows = cursor.fetchall()

                if rows:
                    result_text = f"{search_query} için fiyat geçmişi:\n"
                    for row in rows:        #pull the results and save it
                        result_text += f"Trendyol: {row[0]} TL,\n Adı: {row[1]},\n\n Amazon: {row[2]} TL,\n Adı: {row[3]},\n\n N11: {row[4]} TL,\n Adı: {row[5]},\n\n Arama Tarihi: {row[6]}\n"
                    self.result_label.text = result_text
                else:
                    self.result_label.text = f"{search_query} için fiyat geçmişi bulunamadı."

            except mysql.connector.Error as err:
                self.result_label.text = f"Fiyat geçmişi sorgu hatası: {err}"
            finally:
                cursor.close()      #close the connection
                connection.close()

if __name__ == "__main__":
    TrendyolApp().run()