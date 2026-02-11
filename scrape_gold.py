import os
import requests
import json
from datetime import datetime
import pytz

HEADERS = {
    "accept": "*/*",
    "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "origin": "https://mihong.vn",
    "referer": "https://mihong.vn/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-market": "mihong"
}

APIS = {
    "1 Giờ": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1h",
    "24 Giờ": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=24h",
    "15 Ngày": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=15d",
    "1 Tháng": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1M",
    "6 Tháng": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=6M",
    "1 Năm": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1y"
}

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

def log(msg):
    now = datetime.now(vn_tz).strftime("%H:%M:%S")
    print(f"[{now}] {msg}")

def fetch_data(url, label="Unknown"):
    try:
        log(f"Fetching: {label}...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data
    except Exception as e:
        log(f"Error: {e}")
    return None

def format_time_display(time_str, label):
    if not time_str: return ""
    try:
        dt_obj = None
        formats = ["%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                dt_obj = datetime.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        if dt_obj:
            if label in ["1 Giờ", "24 Giờ"]:
                return dt_obj.strftime("%H:%M %d/%m")
            else:
                return dt_obj.strftime("%d/%m/%Y")
        return time_str
    except Exception:
        return time_str

def get_diff_html(current_val, min_val):
    diff = current_val - min_val
    if diff > 0:
        color = "#27ae60" # Xanh
        sign = "+"
    elif diff < 0:
        color = "#d9534f" # Đỏ
        sign = "-"
    else:
        color = "#999" # Xám
        sign = "+"
    
    return f'<span style="color: {color}; font-size: 0.85em; display: block; font-weight: normal;">({sign}{abs(diff):,.0f})</span>'

def create_table_html(title, color, rows):
    return f"""
    <h3 style="color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px; margin-top: 25px;">{title}</h3>
    <table style="border-collapse: collapse; width: 100%; font-size: 13px; margin-bottom: 10px;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ddd; padding: 8px; width: 15%;">Kỳ Hạn</th>
                <th style="border: 1px solid #ddd; padding: 8px; width: 25%;">Hiện tại <br><span style="font-weight:normal; font-size:10px">(vs Thấp nhất)</span></th>
                <th style="border: 1px solid #ddd; padding: 8px; width: 30%;">Thấp nhất (Thời gian)</th>
                <th style="border: 1px solid #ddd; padding: 8px; width: 30%;">Cao nhất (Thời gian)</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """

log("=== START JOB ===")
run_time = datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y")

current_data = fetch_data(APIS["1 Giờ"], "1 Giờ (Spot)")
subject = ""
html_body = ""

if current_data:
    latest = current_data[-1]
    buy_now = latest.get('buyingPrice', 0)
    sell_now = latest.get('sellingPrice', 0)
    time_now = latest.get('dateTime', '')
    
    subject = f"Giá Vàng {time_now}: Mua {buy_now:,.0f} - Bán {sell_now:,.0f}"
    
    rows_buy = ""
    rows_sell = ""
    
    for label, url in APIS.items():
        data = fetch_data(url, label)
        if data:
            # BUY
            min_buy_item = min(data, key=lambda x: x['buyingPrice'])
            max_buy_item = max(data, key=lambda x: x['buyingPrice'])
            curr_buy_item = data[-1]
            
            t_min_buy = format_time_display(min_buy_item.get('dateTime', ''), label)
            t_max_buy = format_time_display(max_buy_item.get('dateTime', ''), label)
            
            diff_buy_html = get_diff_html(curr_buy_item['buyingPrice'], min_buy_item['buyingPrice'])
            
            rows_buy += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 6px; font-weight:bold;">{label}</td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; font-weight: bold;">
                    {curr_buy_item['buyingPrice']:,.0f}
                    {diff_buy_html}
                </td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #d9534f;">
                    {min_buy_item['buyingPrice']:,.0f} <span style="color: #666; font-size: 0.85em; display:block;">({t_min_buy})</span>
                </td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #27ae60;">
                    {max_buy_item['buyingPrice']:,.0f} <span style="color: #666; font-size: 0.85em; display:block;">({t_max_buy})</span>
                </td>
            </tr>
            """
            
            # SELL
            min_sell_item = min(data, key=lambda x: x['sellingPrice'])
            max_sell_item = max(data, key=lambda x: x['sellingPrice'])
            curr_sell_item = data[-1]
            
            t_min_sell = format_time_display(min_sell_item.get('dateTime', ''), label)
            t_max_sell = format_time_display(max_sell_item.get('dateTime', ''), label)
            
            diff_sell_html = get_diff_html(curr_sell_item['sellingPrice'], min_sell_item['sellingPrice'])
            
            rows_sell += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 6px; font-weight:bold;">{label}</td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; font-weight: bold;">
                    {curr_sell_item['sellingPrice']:,.0f}
                    {diff_sell_html}
                </td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #d9534f;">
                    {min_sell_item['sellingPrice']:,.0f} <span style="color: #666; font-size: 0.85em; display:block;">({t_min_sell})</span>
                </td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #27ae60;">
                    {max_sell_item['sellingPrice']:,.0f} <span style="color: #666; font-size: 0.85em; display:block;">({t_max_sell})</span>
                </td>
            </tr>
            """

    table_buy_html = create_table_html("BẢNG GIÁ MUA VÀO (SJC)", "#e67e22", rows_buy)
    table_sell_html = create_table_html("BẢNG GIÁ BÁN RA (SJC)", "#27ae60", rows_sell)
    
    html_body = f"""
    <html>
    <body style="font-family: Helvetica, Arial, sans-serif; color: #333; line-height: 1.4;">
        <div style="max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50; text-align: center;">Cập nhật Giá Vàng Mi Hồng</h2>
            <p style="text-align: center; color: #7f8c8d; font-size: 12px;">
                Cập nhật lúc: <strong>{time_now}</strong> | Chạy lúc: {run_time}
            </p>
            {table_buy_html}
            {table_sell_html}
            <p style="font-size: 11px; color: #999; margin-top: 20px; border-top: 1px dashed #ccc; padding-top: 10px;">
                * <strong>(±...):</strong> Sự chênh lệch giữa giá Hiện Tại so với giá Thấp Nhất trong cùng kỳ hạn.<br>
                * <strong>Thấp nhất/Cao nhất:</strong> Mức giá đỉnh và đáy trong kỳ hạn.
            </p>
        </div>
    </body>
    </html>
    """
    
    log("HTML generated successfully.")
    print("-" * 20)
    print(html_body)
    print("-" * 20)

else:
    subject = "Lỗi lấy dữ liệu giá vàng"
    html_body = "<h3>Không thể kết nối API Mi Hồng</h3>"
    log("No input data.")

with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as fh:
    print(f'GOLD_SUBJECT={subject}', file=fh)
    print('GOLD_BODY<<EOF', file=fh)
    print(html_body, file=fh)
    print('EOF', file=fh)