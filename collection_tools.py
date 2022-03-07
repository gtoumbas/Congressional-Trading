
import re
import requests

from datetime import date, timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm

from data_types import Member, Trade

# print(trade.find(class_="q-field company-ticker").getText())

def extract_ct(trade_html):
    #TODO collect state / total earnings data
    # Name 
    fname = trade_html.find(class_="q-field firstName").getText()
    lname = trade_html.find(class_="q-field lastName").getText()
    name = fname + " " + lname
    # Chamber
    regex = re.compile('.*q-field chamber.*')
    chamber = trade_html.find("span", {"class" : regex}).getText()

    # Party
    if trade_html.find(class_="q-field party party--democrat"): party = "dem"
    elif trade_html.find(class_="q-field party party--republican"): party = "rep"
    else: party = "ind"

    # Date
    date_element = trade_html.find(class_="q-data-cell tx-date")
    trade_date = date_element.find(class_="q-field format--date-iso").find('time').getText()
    trade_date = date.fromisoformat(trade_date) - timedelta(days=1) # Not sure why i have to do this
    
    # Delay in Days
    regex = re.compile('.*q-value reporting-gap.*')
    delay = trade_html.find("div", {"class" : regex}).getText()

    # Ticker 
    ticker = trade_html.find(class_="q-field company-ticker").getText().split(":")[0]
    
    # Stock Price 
    stock_price = float(trade_html.find(class_="q-field trade-price").getText())

    # Getting num_shares
    details_link = trade_html.find(class_="button hoverable button-default button--size-s")['href']
    details_link = "https://www.capitoltrades.com/" + details_link 
    details_page = requests.get(details_link)
    soup = BeautifulSoup(details_page.content, 'html.parser')
    trade_info = soup.find(class_="q-data-cell filing-date flavour--labelled-value")
    num_shares = trade_info.find(class_="q-value").getText()
    num_shares = "".join(num_shares.split())

    # Buy / Sell
    regex = re.compile('.*q-field tx-type.*')
    kind = trade_html.find("span", {"class": regex}).getText()

    # Creating DB objects

    member, created = Member.get_or_create(name=name, party=party, chamber=chamber)
    if created:
        member.save()

    trade, created = Trade.get_or_create(member=member, num_shares=num_shares, share_price=stock_price,
                        stock=ticker, date=trade_date, delay=delay, kind=kind)
    if created:
        trade.save()

def collect_ct_trades(num_pages):
    bar = tqdm(range(1, num_pages+1))
    num_trades = 0;
    for page_num in bar:
        payload = {'page': page_num, 'pageSize': 50}
        ct_trades = f"https://www.capitoltrades.com/trades"
        capitol_trades = requests.get(ct_trades, params=payload)

        soup = BeautifulSoup(capitol_trades.content, 'html.parser')

        trades = soup.find_all("tr", class_="q-tr")
        trades.pop(0)

        for t in trades:
            extract_ct(t)
            num_trades += 1
            bar.set_description(f"Trades: {num_trades}")

collect_ct_trades(10)