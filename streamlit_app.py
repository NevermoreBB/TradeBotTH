import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.font_manager as fm
from datetime import datetime, timedelta

# --- ส่วนที่ 1: การตั้งค่า Font สำหรับภาษาไทย ---
# สร้าง path ไปยังไฟล์ฟอนต์ในโฟลเดอร์ fonts
font_path = os.path.join(os.getcwd(), 'fonts', 'Sarabun-Regular.ttf')

# ตรวจสอบว่าไฟล์ฟอนต์มีอยู่หรือไม่
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Sarabun'
    plt.rcParams['font.size'] = 12
else:
    # กรณีหาฟอนต์ไม่เจอ ให้ใช้ฟอนต์ดีฟอลต์ที่รองรับภาษาไทยได้
    st.warning("ไม่พบไฟล์ฟอนต์ Sarabun.ttf โปรแกรมจะใช้ฟอนต์เริ่มต้นแทน")
    plt.rcParams['font.family'] = 'Tahoma'

# --- ส่วนที่ 2: การสร้าง User Interface (UI) ---
st.title('Simple Trade Bot')

# ส่วนกรอกชื่อหุ้นใน Sidebar
st.sidebar.header('กรอกชื่อหุ้น')
ticker_symbol = st.sidebar.text_input('กรอกชื่อหุ้น (เช่น PTTGC.BK):', 'OR.BK')

# --- ส่วนที่ 3: การประมวลผลและวิเคราะห์ข้อมูล ---
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

            # สร้างกราฟราคาและ SMA
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

            # --- ส่วนที่ 4: การวิเคราะห์และแสดงสัญญาณซื้อ-ขาย ---
            st.subheader('การวิเคราะห์และสัญญาณซื้อ-ขาย 🚦')
            
            # ดึงค่าล่าสุดของ SMA และราคา
            # แก้ไข: ใช้ .iloc[-1] เพื่อเข้าถึงแถวสุดท้าย และใช้ .at เพื่อดึงค่าที่เจาะจง
            # วิธีนี้จะดึงค่าเพียงค่าเดียว ไม่ใช่ Series
            latest_sma_10 = stock_data['SMA_10'].iloc[-1]
            latest_sma_20 = stock_data['SMA_20'].iloc[-1]

            if pd.isna(latest_sma_10) or pd.isna(latest_sma_20):
                st.markdown(
                    f"<p style='color:gray; font-size:20px;'>🟡 **ข้อมูลยังไม่เพียงพอต่อการวิเคราะห์**</p>"
                    "<p>โปรแกรมจะแสดงผลเมื่อข้อมูลมีอย่างน้อย 20 วัน</p>",
                    unsafe_allow_html=True
                )
            elif latest_sma_10 > latest_sma_20:
                st.markdown(
                    f"<p style='color:green; font-size:20px;'>💡 **สัญญาณ: ซื้อ**</p>"
                    "<p>เนื่องจากเส้น SMA 10 วันอยู่เหนือเส้น SMA 20 วัน ซึ่งบ่งชี้แนวโน้มขาขึ้น</p>",
                    unsafe_allow_html=True
                )
            elif latest_sma_10 < latest_sma_20:
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
