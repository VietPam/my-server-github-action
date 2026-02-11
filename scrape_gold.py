import os
import requests
import json
from datetime import datetime
import pytz

API_URL = "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1h"

def get_current_gold_price():
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://mihong.vn",
        "referer": "https://mihong.vn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "x-market": "mihong"
    }

    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                latest_data = data[-1]
                return {
                    "buying": latest_data.get('buyingPrice', 0),
                    "selling": latest_data.get('sellingPrice', 0),
                    "time": latest_data.get('dateTime', '')
                }
    except:
        pass
    return None

data = get_current_gold_price()
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
current_run_time = datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y")

subject = ""
body = ""

if data:
    buy_str = "{:,.0f}".format(data['buying'])
    sell_str = "{:,.0f}".format(data['selling'])
    
    subject = f"Gia Vang {data['time']}: Mua {buy_str} - Ban {sell_str}"
    body = f"Thoi gian cap nhat tu he thong: {data['time']}\n" \
           f"Thoi gian chay cronjob: {current_run_time}\n\n" \
           f"Gia Mua vao: {buy_str} VND\n" \
           f"Gia Ban ra: {sell_str} VND"
else:
    subject = f"Loi lay gia vang luc {current_run_time}"
    body = "Khong the ket noi den API hoac du lieu tra ve bi loi."

with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as fh:
    print(f'GOLD_SUBJECT={subject}', file=fh)
    print('GOLD_BODY<<EOF', file=fh)
    print(body, file=fh)
    print('EOF', file=fh)