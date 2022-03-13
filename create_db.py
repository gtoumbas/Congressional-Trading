import json 

from dateutil import parser
from tqdm import tqdm
from data_types import Member, Trade


def create_from_watcher(file_name):
    with open(file_name) as f:
        data = json.load(f)
    print(len(data))
    for d in tqdm(data):
        if "house" in file_name:
            trade, member = read_house_data(d)
            trade.save()
            member.save()
        # else:
        #     trade, member = read_cong_data(d)



def read_house_data(dict):
    # Member info
    name = dict["representative"]
    chamber = "House"
    district = dict["district"]
    member, created = Member.get_or_create(name=name, chamber=chamber, district=district)

    # Trade info 
    d_date = parser.parse(dict["disclosure_date"]).date()
    t_date = parser.parse(dict["transaction_date"]).date()
    owner = dict["owner"]
    if not owner: owner = "NA"
    ticker = dict["ticker"]
    description = dict["asset_description"]
    type = dict["type"]

    amount = dict["amount"]
    amount = amount.replace("$", "").replace(",", "").replace(" ", "").split("-")
    try:
        high_amount = int(amount[1])
        low_amount = int(amount[0])
    except:
        high_amount = 0
        low_amount = 0
    disc_link = dict["ptr_link"]

    trade, created = Trade.get_or_create(member=member, trade_date=t_date, disclosure_date=d_date,
                                owner=owner, ticker=ticker, description=description, type=type,
                                high_amount=high_amount, low_amount=low_amount, disclosure_url=disc_link)

    return trade, member
create_from_watcher("house_transactions.json")


#TODO write cong read method

# TODO write method to fill out missing values of member (could use a list of senate members maybe)