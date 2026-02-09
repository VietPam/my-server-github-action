import os
import random
from datetime import datetime

# --- PHẦN 1: LOGIC CÀO WEB (Bạn sẽ sửa phần này để cào thật) ---
# Ví dụ: dùng thư viện requests và BeautifulSoup để lấy giá từ web
# price = soup.find('div', class_='gold-price').text
# Ở đây mình random để demo cho bạn thấy nó hoạt động
price = random.randint(70, 80) 
price_str = f"{price}.000.000 VND"
current_time = datetime.now().strftime("%H:%M %d/%m/%Y")

# Nội dung tiêu đề email muốn hiển thị
email_subject = f"Giá vàng lúc {current_time} là: {price_str}"

# --- PHẦN 2: GỬI DỮ LIỆU RA NGOÀI ĐỂ GITHUB ACTION ĐỌC ---
# Đây là bước quan trọng nhất để chuyển dữ liệu từ Python sang bước Gửi Email
with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
    print(f'GOLD_SUBJECT={email_subject}', file=fh)
    print(f'GOLD_BODY=Chào bạn, giá vàng hiện tại là {price_str}. Hãy kiểm tra nhé!', file=fh)
