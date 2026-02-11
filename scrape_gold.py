import os
import requests
import json
from datetime import datetime
import pytz

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://mihong.vn",
    "referer": "https://mihong.vn/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
    "x-market": "mihong",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Microsoft Edge";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

APIS = {
    "1H": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1h",
    "24H": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=24h",
    "15 Ngay": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=15d",
    "1 Thang": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1M",
    "6 Thang": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=6M",
    "1 Nam": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1y"
}

def fetch_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data
    except:
        pass
    return None

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
run_time = datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y")

current_data = fetch_data(APIS["1H"])
subject = ""
html_body = ""

if current_data:
    latest = current_data[-1]
    buy_now = latest.get('buyingPrice', 0)
    sell_now = latest.get('sellingPrice', 0)
    time_now = latest.get('dateTime', '')
    
    buy_fmt = "{:,.0f}".format(buy_now)
    sell_fmt = "{:,.0f}".format(sell_now)
    subject = f"Gia Vang {time_now}: Mua {buy_fmt} - Ban {sell_fmt}"

    table_rows = ""
    
    for label, url in APIS.items():
        data = fetch_data(url)
        if data:
            first = data[0]
            last = data[-1]
            
            b_start = first.get('buyingPrice', 0)
            b_end = last.get('buyingPrice', 0)
            b_diff = b_end - b_start
            
            s_start = first.get('sellingPrice', 0)
            s_end = last.get('sellingPrice', 0)
            s_diff = s_end - s_start
            
            color_buy = "green" if b_diff >= 0 else "red"
            color_sell = "green" if s_diff >= 0 else "red"
            
            start_time = first.get('dateTime', '').split(' ')[0]
            
            row = f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{label} <br><small>({start_time})</small></td>
                <td style="border: 1px solid #ddd; padding: 8px;">
                    {b_end:,.0f} <br>
                    <span style="color:{color_buy}; font-size: 12px;">({b_diff:+,.0f})</span>
                </td>
                <td style="border: 1px solid #ddd; padding: 8px;">
                    {s_end:,.0f} <br>
                    <span style="color:{color_sell}; font-size: 12px;">({s_diff:+,.0f})</span>
                </td>
            </tr>
            """
            table_rows += row

    html_body = f"""
    <html>
    <body>
        <h2>Cap nhat Gia Vang SJC - Mi Hong</h2>
        <p><strong>Thoi gian he thong:</strong> {time_now}</p>
        <p><strong>Thoi gian chay cronjob:</strong> {run_time}</p>
        
        <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Ky Han</th>
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Gia Mua (VND)</th>
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Gia Ban (VND)</th>
            </tr>
            {table_rows}
        </table>
        <p><i>So sanh gia hien tai voi gia dau ky han tuong ung.</i></p>
    </body>
    </html>
    """

else:
    subject = f"Loi lay gia vang {run_time}"
    html_body = "Khong the lay du lieu tu API."

with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as fh:
    print(f'GOLD_SUBJECT={subject}', file=fh)
    print('GOLD_BODY<<EOF', file=fh)
    print(html_body, file=fh)
    print('EOF', file=fh)