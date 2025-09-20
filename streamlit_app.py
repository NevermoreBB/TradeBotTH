import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title('Trade Bot สำหรับคุณพ่อ')

# ส่วนรับค่าจากผู้ใช้
st.sidebar.header('ตั้งค่าหุ้น')
ticker_symbol = st.sidebar.text_input('กรอกชื่อหุ้น (เช่น OR.BK):', 'OR.BK')
start_date = st.sidebar.date_input('เลือกวันที่เริ่มต้น:', value=pd.to_datetime('2024-01-01'))
end_date = st.sidebar.date_input('เลือกวันที่สิ้นสุด:', value=pd.to_datetime('2025-01-01'))

# ดึงข้อมูลและแสดงผล
if st.sidebar.button('แสดงกราฟ'):
    try:
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        if stock_data.empty:
            st.error("ไม่พบข้อมูลหุ้นสำหรับชื่อนี้")
        else:
            st.success(f"ดึงข้อมูลหุ้น {ticker_symbol} สำเร็จ!")
            
            # คำนวณ SMA 20 วัน
            stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()

            # สร้างกราฟ
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(stock_data['Close'], label='ราคาปิด', color='blue')
            ax.plot(stock_data['SMA_20'], label='SMA 20 วัน', color='red')
            ax.set_title(f'กราฟราคาหุ้น {ticker_symbol} และ SMA 20 วัน')
            ax.set_xlabel('วันที่')
            ax.set_ylabel('ราคา')
            ax.legend()
            ax.grid(True)
            
            st.pyplot(fig) # แสดงกราฟใน Streamlit
            st.write(stock_data.tail()) # แสดงข้อมูล 5 บรรทัดสุดท้าย
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")