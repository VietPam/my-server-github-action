import os
import requests
import json
from datetime import datetime
import pytz

# Cấu hình headers giả lập trình duyệt để tránh bị chặn
HEADERS = {
    "accept": "*/*",
    "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "origin": "https://mihong.vn",
    "referer": "https://mihong.vn/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-market": "mihong"
}

# Danh sách API và tên hiển thị tiếng Việt
APIS = {
    "1 Giờ": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1h",
    "24 Giờ": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=24h",
    "15 Ngày": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=15d",
    "1 Tháng": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1M",
    "6 Tháng": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=6M",
    "1 Năm": "https://api.mihong.vn/v1/gold-prices?market=domestic&goldCode=SJC&last=1y"
}

def fetch_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

# Lấy thời gian hiện tại
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
run_time = datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y")

# Lấy dữ liệu 1 giờ để làm tiêu đề chính (Giá Spot)
current_data = fetch_data(APIS["1 Giờ"])
subject = ""
html_body = ""

if current_data:
    latest = current_data[-1]
    buy_now_spot = latest.get('buyingPrice', 0)
    sell_now_spot = latest.get('sellingPrice', 0)
    time_now_spot = latest.get('dateTime', '')
    
    # Format tiêu đề email
    buy_fmt = "{:,.0f}".format(buy_now_spot)
    sell_fmt = "{:,.0f}".format(sell_now_spot)
    subject = f"Giá Vàng {time_now_spot}: Mua {buy_fmt} - Bán {sell_fmt}"

    # Tạo các dòng cho bảng
    table_rows = ""
    
    for label, url in APIS.items():
        data = fetch_data(url)
        if data:
            # Tách mảng giá mua và bán để tìm min/max
            buy_prices = [x.get('buyingPrice', 0) for x in data]
            sell_prices = [x.get('sellingPrice', 0) for x in data]
            
            # Tính toán các chỉ số
            b_current = buy_prices[-1]
            b_min = min(buy_prices)
            b_max = max(buy_prices)
            
            s_current = sell_prices[-1]
            s_min = min(sell_prices)
            s_max = max(sell_prices)
            
            # CSS styles
            style_cell = "border: 1px solid #ddd; padding: 6px; text-align: right;"
            style_curr = "font-weight: bold; color: #333;"
            style_min = "color: #d9534f; font-size: 0.9em;" # Đỏ nhạt
            style_max = "color: #5cb85c; font-size: 0.9em;" # Xanh lá
            
            row = f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: left; background-color: #f9f9f9;">
                    <strong>{label}</strong>
                </td>
                
                <td style="{style_cell} {style_curr}">{b_current:,.0f}</td>
                <td style="{style_cell} {style_min}">{b_min:,.0f}</td>
                <td style="{style_cell} {style_max}">{b_max:,.0f}</td>
                
                <td style="{style_cell} {style_curr}">{s_current:,.0f}</td>
                <td style="{style_cell} {style_min}">{s_min:,.0f}</td>
                <td style="{style_cell} {style_max}">{s_max:,.0f}</td>
            </tr>
            """
            table_rows += row

    # Tạo khung HTML hoàn chỉnh
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #d35400;">Cập nhật Giá Vàng SJC - Mi Hồng</h2>
        <p><strong>Thời gian hệ thống:</strong> {time_now_spot}</p>
        <p><strong>Thời gian chạy:</strong> {run_time}</p>
        
        <table style="border-collapse: collapse; width: 100%; font-size: 13px;">
            <thead>
                <tr style="background-color: #34495e; color: white;">
                    <th rowspan="2" style="border: 1px solid #ddd; padding: 8px;">Kỳ Hạn</th>
                    <th colspan="3" style="border: 1px solid #ddd; padding: 8px; background-color: #e67e22;">GIÁ MUA (VND)</th>
                    <th colspan="3" style="border: 1px solid #ddd; padding: 8px; background-color: #27ae60;">GIÁ BÁN (VND)</th>
                </tr>
                <tr style="background-color: #ecf0f1; color: #333;">
                    <th style="border: 1px solid #ddd; padding: 6px;">Hiện tại</th>
                    <th style="border: 1px solid #ddd; padding: 6px;">Thấp nhất</th>
                    <th style="border: 1px solid #ddd; padding: 6px;">Cao nhất</th>
                    <th style="border: 1px solid #ddd; padding: 6px;">Hiện tại</th>
                    <th style="border: 1px solid #ddd; padding: 6px;">Thấp nhất</th>
                    <th style="border: 1px solid #ddd; padding: 6px;">Cao nhất</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        <p style="font-size: 11px; color: #777; margin-top: 10px;">
            * Min/Max: Giá thấp nhất và cao nhất ghi nhận được trong kỳ hạn tương ứng.
        </p>
    </body>
    </html>
    """

else:
    subject = f"Lỗi lấy giá vàng {run_time}"
    html_body = "<h3>Không thể lấy dữ liệu từ API.</h3>"

# Ghi ra output cho GitHub Action
with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as fh:
    print(f'GOLD_SUBJECT={subject}', file=fh)
    print('GOLD_BODY<<EOF', file=fh)
    print(html_body, file=fh)
    print('EOF', file=fh)