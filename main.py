import pandas as pd
from vnstock import stock_historical_data, listing_companies
import json
from datetime import datetime, timedelta

# 1. Tự động lấy danh sách toàn bộ ~1600 mã chứng khoán trên 3 sàn
try:
    # Hàm listing_companies() giúp tự động lấy danh sách công ty niêm yết
    df_companies = listing_companies() 
    tickers = df_companies['ticker'].tolist()
except Exception as e:
    # Nếu lỗi, fallback về danh sách dự phòng
    tickers = ['FPT', 'VCB', 'SSI', 'HPG', 'VNM', 'BVH', 'VIC', 'VHM'] 

# 2. Lấy mốc thời gian 1.5 năm để đảm bảo đủ 260 ngày giao dịch
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=500)).strftime('%Y-%m-%d')

rs_results = {}
print(f"Bắt đầu quét {len(tickers)} mã cổ phiếu...")

for ticker in tickers:
    try:
        # Tải dữ liệu lịch sử
        df = stock_historical_data(symbol=ticker, start_date=start_date, end_date=end_date, resolution='1D', type='stock')
        
        # Nếu mã mới niêm yết chưa đủ 260 ngày, hoặc không có dữ liệu giao dịch -> Bỏ qua
        if df is None or df.empty or len(df) < 260:
            continue
            
        df = df.sort_values('time').reset_index(drop=True)
        
        # Tính ROC và DK6
        roc_65 = df['close'].pct_change(periods=65) * 100
        roc_130 = df['close'].pct_change(periods=130) * 100
        roc_195 = df['close'].pct_change(periods=195) * 100
        roc_260 = df['close'].pct_change(periods=260) * 100
        
        dk6 = 0.4 * roc_65 + 0.2 * roc_130 + 0.2 * roc_195 + 0.2 * roc_260
        
        # Lấy điểm RS của ngày mới nhất
        latest_rs = round(dk6.iloc[-1], 2)
        
        if latest_rs > -1000:
            rs_results[ticker] = latest_rs
            
    except Exception as e:
        # Mã nào lỗi API thì âm thầm bỏ qua để hệ thống chạy tiếp các mã khác
        continue

# 3. Lưu toàn bộ kết quả vào file dữ liệu chung
with open('data_rs.json', 'w') as f:
    json.dump(rs_results, f)

print("Đã hoàn tất tính toán điểm RS cho toàn thị trường!")
