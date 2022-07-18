import smtplib
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

def main_function():
    product_list_path =''
    log_file_path = ''
    prod_name = pd.read_csv(product_list_path,sep=';')
    prod_url = prod_name.url
    log_file = pd.read_csv(log_file_path,sep=';')
    now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')

    for x, url in enumerate(prod_url):
        page = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(page.content, features="html.parser")

        title = soup.find(id='productTitle')[0].get_text().strip()
# Find the price of product
        try:
            price = float(soup.find(id='priceblock_ourprice').get_text().replace('.', '').replace('€', '').replace(',', '.').strip())
        except:
            try:
                price = float(soup.find(id='priceblock_saleprice').get_text().replace('.', '').replace('$', '').replace(',', '').strip())
            except:
                price = ''
# Check for availability
        try:
            soup.select('#availability .a-color-state')[0].get_text().strip()
            stock = 'Out of Stock'
        except:
            try:
                soup.select('#availability .a-color-price')[0].get_text().strip()
                stock = 'Out of Stock'
            except:
                stock = 'Available'
# Compare with the set price
        try:
            if price < prod_name.price[x]:
                print('the price of '+ title +'  is below the given price')
                send_mail(title , price , url)
        except:
            pass
# Add data to the log_file to keep the track of the price   
        log = {'date':now,'url':url,'price':price,'availability':stock}
        log_file.append(log)

def send_mail(title,price,link):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    
    server.login('SENDER EMAIL ID' , 'PASSWORD')

    body = f'Price alert !! \nThe price of ----{title}---- is {price} !!!\ncheck the link{link}'

    server.send_message(
        'SENDER ID (FROM ID)',
        'RECEIVER ID (TO ID)',
        body
    )
    print('EMAIL SEND SUCCESSFULLY !! ')
    server.quit()
    
while True:
    main_function()
    # sleep for 6 hrs
    time.sleep(60*60*6)
