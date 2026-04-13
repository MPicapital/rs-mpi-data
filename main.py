import pandas as pd
from vnstock import stock_historical_data
import json
from datetime import datetime, timedelta

# Danh sách các mã cổ phiếu bạn muốn theo dõi (bạn có thể thêm bớt)
tickers = ['FPT', 'VCB', 'SSI', 'HPG', 'VNM']

# Lấy ngày hôm nay và 1.5 năm trước để đủ dữ liệu tính 260 ngày
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=500)).strftime('%Y-%m-%d')

rs_results = {}

for ticker in tickers:
    try:
        # Tải dữ liệu lịch sử
        df = stock_historical_data(symbol=ticker, start_date=start_date, end_date=end_date, resolution='1D', type='stock')
        df = df.sort_values('time').reset_index(drop=True)

        # Tính ROC và DK6
        roc_65 = df['close'].pct_change(periods=65) * 100
        roc_130 = df['close'].pct_change(periods=130) * 100
        roc_195 = df['close'].pct_change(periods=195) * 100
        roc_260 = df['close'].pct_change(periods=260) * 100

        dk6 = 0.4 * roc_65 + 0.2 * roc_130 + 0.2 * roc_195 + 0.2 * roc_260

        # Lấy điểm RS mới nhất của ngày hôm nay
        latest_rs = round(dk6.iloc[-1], 2)

        # Chỉ lấy những mã có RS > -1000
        if latest_rs > -1000:
            rs_results[ticker] = latest_rs
    except Exception as e:
        print(f"Lỗi ở mã {ticker}: {e}")

# Lưu kết quả ra file JSON
with open('data_rs.json', 'w') as f:
    json.dump(rs_results, f)
