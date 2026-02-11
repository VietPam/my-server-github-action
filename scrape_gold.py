import os
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
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

# --- HÀM HỖ TRỢ ---
def log(msg):
    now = datetime.now(vn_tz).strftime("%H:%M:%S")
    print(f"[{now}] {msg}")

def fetch_data(url, label="Unknown"):
    try:
        log(f"Đang gọi API: {label}...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data
    except Exception as e:
        log(f"  -> Lỗi: {e}")
    return None

def format_time_display(time_str, label):
    """
    Format thời gian hiển thị tùy theo kỳ hạn.
    - 1 Giờ, 24 Giờ: Chỉ lấy Giờ:Phút (HH:mm)
    - Còn lại: Lấy Ngày/Tháng Giờ:Phút (dd/MM HH:mm)
    """
    try:
        # API Mi Hồng thường trả về định dạng ISO hoặc chuỗi cụ thể
        # Giả sử format trả về có thể parse được, nếu không sẽ trả về nguyên gốc
        # Đây là ví dụ parse đơn giản, cần điều chỉnh nếu format API khác biệt
        # Thường API trả về: "2024-02-11T14:30:00" hoặc tương tự
        
        # Nếu chuỗi quá ngắn, trả về luôn
        if len(time_str) < 5: return time_str
        
        # Parse chuỗi thời gian (Cố gắng xử lý ISO format)
        dt_obj = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
            try:
                dt_obj = datetime.strptime(time_str.split('.')[0], fmt)
                break
            except ValueError:
                continue
        
        if dt_obj:
            if label in ["1 Giờ", "24 Giờ"]:
                return dt_obj.strftime("%H:%M") # Chỉ hiện giờ
            else:
                return dt_obj.strftime("%d/%m %H:%M") # Ngày + Giờ
                
        # Fallback nếu không parse được nhưng chuỗi có vẻ chứa giờ (lấy phần cuối)
        return time_str.split(' ')[-1] if ' ' in time_str else time_str
        
    except Exception:
        return time_str

def create_table_html(title, color, rows):
    """Hàm tạo bảng HTML dùng chung"""
    return f"""
    <h3 style="color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px; margin-top: 25px;">{title}</h3>
    <table style="border-collapse: collapse; width: 100%; font-size: 13px; margin-bottom: 10px;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ddd; padding: 8px; width: 15%;">Kỳ Hạn</th>
                <th style="border: 1px solid #ddd; padding: 8px; width: 25%;">Hiện tại</th>
                <th style="border: 1px solid #ddd; padding: 8px; width: 30%;">Thấp nhất (Lúc)</th>
                <th style="border: 1px solid #ddd; padding: 8px; width: 30%;">Cao nhất (Lúc)</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """

# --- MAIN ---
log("=== START JOB ===")
run_time = datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y")

# 1. Lấy dữ liệu Spot để làm tiêu đề
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
    
    # 2. Loop qua các API để tính toán
    for label, url in APIS.items():
        data = fetch_data(url, label)
        if data:
            # --- XỬ LÝ GIÁ MUA ---
            # Tìm item có buyingPrice nhỏ nhất và lớn nhất
            min_buy_item = min(data, key=lambda x: x['buyingPrice'])
            max_buy_item = max(data, key=lambda x: x['buyingPrice'])
            curr_buy_item = data[-1]
            
            # Format thời gian
            t_min_buy = format_time_display(min_buy_item.get('dateTime', ''), label)
            t_max_buy = format_time_display(max_buy_item.get('dateTime', ''), label)
            
            # Tạo hàng cho bảng Mua
            rows_buy += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 6px; font-weight:bold;">{label}</td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; font-weight: bold;">{curr_buy_item['buyingPrice']:,.0f}</td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #d9534f;">
                    {min_buy_item['buyingPrice']:,.0f} <span style="color: #888; font-size: 0.85em; display:block;">({t_min_buy})</span>
                </td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #27ae60;">
                    {max_buy_item['buyingPrice']:,.0f} <span style="color: #888; font-size: 0.85em; display:block;">({t_max_buy})</span>
                </td>
            </tr>
            """
            
            # --- XỬ LÝ GIÁ BÁN ---
            min_sell_item = min(data, key=lambda x: x['sellingPrice'])
            max_sell_item = max(data, key=lambda x: x['sellingPrice'])
            curr_sell_item = data[-1]
            
            t_min_sell = format_time_display(min_sell_item.get('dateTime', ''), label)
            t_max_sell = format_time_display(max_sell_item.get('dateTime', ''), label)
            
            rows_sell += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 6px; font-weight:bold;">{label}</td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; font-weight: bold;">{curr_sell_item['sellingPrice']:,.0f}</td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #d9534f;">
                    {min_sell_item['sellingPrice']:,.0f} <span style="color: #888; font-size: 0.85em; display:block;">({t_min_sell})</span>
                </td>
                <td style="border: 1px solid #ddd; padding: 6px; text-align: right; color: #27ae60;">
                    {max_sell_item['sellingPrice']:,.0f} <span style="color: #888; font-size: 0.85em; display:block;">({t_max_sell})</span>
                </td>
            </tr>
            """

    # 3. Ghép HTML hoàn chỉnh
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
                * <strong>Thấp nhất/Cao nhất:</strong> Là mức giá đỉnh và đáy ghi nhận được trong khoảng thời gian tương ứng.<br>
                * Thời gian trong ngoặc đơn thể hiện thời điểm đạt mức giá đó.
            </p>
        </div>
    </body>
    </html>
    """
    
    # In ra log debug
    log("Tạo HTML thành công!")
    print("-" * 20)
    print(html_body) # Để xem log trên Github Action
    print("-" * 20)

else:
    subject = "Lỗi lấy dữ liệu giá vàng"
    html_body = "<h3>Không thể kết nối API Mi Hồng</h3>"
    log("Lỗi: Không có dữ liệu đầu vào.")

# Ghi output
with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as fh:
    print(f'GOLD_SUBJECT={subject}', file=fh)
    print('GOLD_BODY<<EOF', file=fh)
    print(html_body, file=fh)
    print('EOF', file=fh)