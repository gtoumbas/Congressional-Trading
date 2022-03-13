
import re
import requests
import time
import json
import sys 

from datetime import date, timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from data_types import Member, Trade

NUM_PAGES_AT_50 = 908

def extract_ct_json(trade_html, driver, file):
    # Getting num_shares
    details_link = trade_html.find(class_="button hoverable button-default button--size-s")['href']
    details_link = "https://www.capitoltrades.com/" + details_link 
    details_page = requests.get(details_link, timeout=(3.05, 27))

    soup = BeautifulSoup(details_page.content, 'html.parser')

    test = soup.find(id="__NEXT_DATA__")
    info = json.loads(test.getText())
    info = info["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["data"]
    return info


def collect_ct_trades_json(end_page, filename, startpage=0):
    bar = tqdm(range(startpage+1, end_page+1))
    num_trades = 0;
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    if startpage > 0:     
        with open(f"check_pg_{startpage}.json") as f:
            data = json.load(f)
    else:
        data = []
    count = 0
    num_errors = 0  

    for page_num in bar:

        try: 
            driver.get(f"https://www.capitoltrades.com/trades?page={page_num}&pageSize=50")
        except: 
            print(f"Error on Page {page_num}")
            time.sleep(200)
            continue
        delay = 100 # seconds
        try:
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'q-tr')))
        except TimeoutException:
            print("Loading took too much time!")
        
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, 'html.parser')
        
        # break_var = False
        try:
            trades = soup.find_all("tr", class_="q-tr")
            trades.pop(0)
        except:
            print("empty list for some reason")
            print(f"Error on Page {page_num}")
            time.sleep(200)
            continue
        # print(len(trades))
        for t in trades:
            try: 
                trade = extract_ct_json(t, driver, f)
            except:
                num_errors += 1
                continue
            data.append(trade)
            count += 1

            # if count > 2:
            #     break_var = True
            #     break
            bar.set_description(f"Trades: {count}, Errors: {num_errors}")


        if page_num % 50 == 0:
            with open(f'check_pg_{page_num}.json', 'w') as outfile:
                json.dump(data, outfile)

            # if break_var: break
    with open(filename, "a") as f:
        f.write(json.dumps(data)) 
        # print(sys.getsizeof(data))
    driver.quit()


collect_ct_trades_json(NUM_PAGES_AT_50, "capitol_trades.json", startpage=250)


