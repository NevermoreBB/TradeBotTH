import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from datetime import datetime, timedelta

# ตั้งค่าฟอนต์ที่รองรับภาษาไทย
plt.rcParams['font.family'] = 'Sarabun'
plt.rcParams['font.size'] = 12

# ตั้งชื่อหน้าเว็บแอปพลิเคชัน
st.title('Trade Bot สำหรับคุณพ่อ')

# สร้างส่วน Input สำหรับชื่อหุ้นใน Sidebar
st.sidebar.header('กรอกชื่อหุ้น')
ticker_symbol = st.sidebar.text_input('กรอกชื่อหุ้น (เช่น OR.BK):', 'OR.BK')

# เมื่อผู้ใช้กรอกชื่อหุ้น ระบบจะรันการวิเคราะห์ทันที
if ticker_symbol:
    try:
        # คำนวณช่วงเวลาอัตโนมัติ (ย้อนหลัง 1 ปี)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        # ดึงข้อมูลหุ้น
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        if stock_data.empty:
            st.error("ไม่พบข้อมูลหุ้นสำหรับชื่อนี้ กรุณาตรวจสอบสัญลักษณ์")
        else:
            st.success(f"ดึงข้อมูลหุ้น {ticker_symbol} สำเร็จ!")
            
            # คำนวณ Simple Moving Average (SMA)
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
            st.pyplot(fig)

            # --- ส่วนที่เพิ่มใหม่เพื่อวิเคราะห์และแสดงผล ---
            st.subheader('การวิเคราะห์และสัญญาณซื้อ-ขาย 🚦')
            latest_data = stock_data.iloc[-1]
            current_sma_10 = latest_data['SMA_10']
            current_sma_20 = latest_data['SMA_20']

            if pd.isna(current_sma_10) or pd.isna(current_sma_20):
                st.markdown(
                    f"<p style='color:gray; font-size:20px;'>🟡 **ข้อมูลยังไม่เพียงพอต่อการวิเคราะห์**</p>"
                    "<p>โปรแกรมจะแสดงผลเมื่อข้อมูลมีอย่างน้อย 20 วัน</p>",
                    unsafe_allow_html=True
                )
            elif current_sma_10 > current_sma_20:
                st.markdown(
                    f"<p style='color:green; font-size:20px;'>💡 **สัญญาณ: ซื้อ**</p>"
                    "<p>เนื่องจากเส้น SMA 10 วันอยู่เหนือเส้น SMA 20 วัน ซึ่งบ่งชี้แนวโน้มขาขึ้น</p>",
                    unsafe_allow_html=True
                )
            elif current_sma_10 < current_sma_20:
                st.markdown(
                    f"<p style='color:red; font-size:20px;'>🔻 **สัญญาณ: ขาย**</p>"
                    "<p>เนื่องจากเส้น SMA 10 วันอยู่ต่ำกว่าเส้น SMA 20 วัน ซึ่งบ่งชี้แนวโน้มขาลง</p>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<p style='color:orange; font-size:20px;'>🟡 **สัญญาณ: ยังไม่ชัดเจน**</p>"
                    "<p>ควรเฝ้ารอเพื่อดูการเปลี่ยนแปลงของราคา</p>",
                    unsafe_allow_html=True
                )

            st.write("ตารางข้อมูลล่าสุด:")
            st.write(stock_data.tail())

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
