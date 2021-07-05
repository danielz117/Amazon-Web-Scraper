import csv
import re
import string
import time
import webbrowser
from urllib.parse import ParseResultBytes
from bs4 import BeautifulSoup
from selenium import webdriver

def get_url(search_term):
    template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term = search_term.replace(' ', '+')
    return template.format(search_term)

def extract_record(item):
    try:
        atag = item.h2.a
        description = atag.text.strip()
        url = 'https://www.amazon.com' + atag.get('href')
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
        price = price[1:]
        rating = item.i.text
        if (rating == ''):
            return False
        rating = rating[:3]
        review_count = item.find('span', 'a-size-base').text
        review_count = review_count.replace(",","")
        if (review_count.isdigit()):
            pass
        else:
            return False
        #regnumber = re.findall(r'[0-9],[0-9]|[0-9]', review_count)
        #print(regnumber)
        #if regnumber.search(review_count):
        #    print(review_count)
        #    pass
        #else:
        #    return False
        value = (float(rating)*float(review_count))/(float(price.replace(',',''))*.20)
        global numb
        result = (value, description, price, rating, review_count, url)
        return result
    except AttributeError:
        return False

records = []
input = input('What are you shopping for? ')
url = get_url(input)
driver = webdriver.Chrome(r'C:\Users\danie\Documents\chromedriver.exe')
current_url = list(url)
for page in range(1,21):
    string_url =""
    for element in current_url: 
        string_url += str(element)
    driver.get(string_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = soup.find_all('div', {'data-component-type': 's-search-result'})

    for item in results:
        stuff = extract_record(item)
        if (stuff != False):
            records.append(stuff)

    if (page == 1):
        nextButton = driver.find_element_by_partial_link_text('Next')
        nextButton.click()
        current_url = list(driver.current_url)
    
    current_url[28+len(input)+5] = page+1

sorted_records = sorted(records, reverse=True, key=lambda x: x[0])
with open('results.csv', 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Value', 'Description', 'Price', 'Rating', 'ReviewCount', 'Url'])
    writer.writerows(sorted_records)

driver.close()

for i in range(5):
    webbrowser.open(sorted_records[i][5])
