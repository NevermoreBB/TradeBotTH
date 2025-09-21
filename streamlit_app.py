import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# ตั้งค่าฟอนต์ที่รองรับภาษาไทย
plt.rcParams['font.family'] = 'Sarabun'
plt.rcParams['font.size'] = 12

# ตั้งชื่อหน้าเว็บแอปพลิเคชัน
st.title('Trade Bot สำหรับคุณพ่อ')

# สร้างส่วน Input ใน Sidebar
st.sidebar.header('ตั้งค่าหุ้น')
ticker_symbol = st.sidebar.text_input('กรอกชื่อหุ้น (เช่น OR.BK):', 'OR.BK')
start_date = st.sidebar.date_input('เลือกวันที่เริ่มต้น:', value=pd.to_datetime('2024-01-01'))
end_date = st.sidebar.date_input('เลือกวันที่สิ้นสุด:', value=pd.to_datetime('2025-01-01'))

# เพิ่มปุ่ม "แสดงกราฟ"
if st.sidebar.button('แสดงกราฟ'):
    try:
        # ดึงข้อมูลหุ้น
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        if stock_data.empty:
            st.error("ไม่พบข้อมูลหุ้นสำหรับชื่อนี้ กรุณาตรวจสอบสัญลักษณ์")
        else:
            st.success(f"ดึงข้อมูลหุ้น {ticker_symbol} สำเร็จ!")
            
            # คำนวณ Simple Moving Average (SMA)
            # เพิ่ม SMA 10 วัน (ระยะสั้น) และ SMA 20 วัน (ระยะยาว)
            stock_data['SMA_10'] = stock_data['Close'].rolling(window=10).mean()
            stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()

            # สร้างกราฟราคา
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(stock_data['Close'], label='ราคาปิด', color='blue')
            ax.plot(stock_data['SMA_10'], label='SMA 10 วัน', color='green')
            ax.plot(stock_data['SMA_20'], label='SMA 20 วัน', color='red')
            ax.set_title(f'กราฟราคาหุ้น {ticker_symbol} พร้อม SMA')
            ax.set_xlabel('วันที่')
            ax.set_ylabel('ราคา')
            ax.legend()
            ax.grid(True)
            
            # แสดงกราฟ
            st.pyplot(fig)

            # --- ส่วนที่เพิ่มใหม่เพื่อวิเคราะห์และแสดงผล ---
            st.subheader('การวิเคราะห์และสัญญาณซื้อ-ขาย 🚦')
            # ดึงค่าล่าสุดของ SMA และราคา
            latest_data = stock_data.iloc[-1]
            current_sma_10 = latest_data['SMA_10']
            current_sma_20 = latest_data['SMA_20']

            if current_sma_10 > current_sma_20:
                st.markdown(
                    f"<p style='color:green; font-size:20px;'>💡 **สัญญาณ: ซื้อ**</p>"
                    "<p>เพราะ SMA 10 วันตัดขึ้นเหนือ SMA 20 วัน ซึ่งบ่งชี้ว่าแนวโน้มราคากำลังเป็นขาขึ้น</p>",
                    unsafe_allow_html=True
                )
            elif current_sma_10 < current_sma_20:
                st.markdown(
                    f"<p style='color:red; font-size:20px;'>🔻 **สัญญาณ: ขาย**</p>"
                    "<p>เพราะ SMA 10 วันตัดลงต่ำกว่า SMA 20 วัน ซึ่งบ่งชี้ว่าแนวโน้มราคากำลังเป็นขาลง</p>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<p style='color:orange; font-size:20px;'>🟡 **สัญญาณ: ยังไม่ชัดเจน**</p>"
                    "<p>ควรเฝ้ารอเพื่อดูการเปลี่ยนแปลงของราคา</p>",
                    unsafe_allow_html=True
                )
            # --------------------------------------------------

            st.write("ตารางข้อมูลล่าสุด:")
            st.write(stock_data.tail())

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
