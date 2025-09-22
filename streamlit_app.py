import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.font_manager as fm
from datetime import datetime, timedelta

# --- ส่วนที่ 1: การตั้งค่า Font สำหรับภาษาไทย ---
font_path = os.path.join(os.getcwd(), 'fonts', 'Sarabun-Regular.ttf')

if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Sarabun'
    plt.rcParams['font.size'] = 12
else:
    st.warning("ไม่พบไฟล์ฟอนต์ Sarabun.ttf โปรแกรมจะใช้ฟอนต์เริ่มต้นแทน")
    plt.rcParams['font.family'] = 'Tahoma'

# --- ส่วนที่ 2: การสร้าง User Interface (UI) ---
st.title('Trade Bot สำหรับคุณพ่อ')

st.sidebar.header('กรอกชื่อหุ้น')
ticker_symbol_input = st.sidebar.text_input('กรอกชื่อหุ้น:', 'OR')

# --- ส่วนที่ 3: การประมวลผลและวิเคราะห์ข้อมูล ---
if ticker_symbol_input:
    ticker_symbol = ticker_symbol_input.strip().upper()
    if not ticker_symbol.endswith('.BK') and len(ticker_symbol) > 1:
        ticker_symbol += '.BK'

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date, progress=False)
        
        if stock_data.empty:
            st.error("ไม่พบข้อมูลหุ้นสำหรับชื่อนี้ กรุณาตรวจสอบสัญลักษณ์")
        else:
            # คำนวณ SMA และ RSI
            stock_data['SMA_10'] = stock_data['Close'].rolling(window=10).mean()
            stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()

            delta = stock_data['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.ewm(com=13, min_periods=14).mean()
            avg_loss = loss.ewm(com=13, min_periods=14).mean()
            rs = avg_gain / avg_loss
            stock_data['RSI'] = 100 - (100 / (1 + rs))

            # --- ส่วนที่ 4: การวิเคราะห์และแสดงสัญญาณซื้อ-ขาย (หัวข้อแรก) ---
            st.header('ผลการวิเคราะห์ล่าสุด 📊')
            
            # ดึงค่า RSI 5 วันล่าสุด
            last_5_rsi = stock_data['RSI'].tail(5)

            if len(last_5_rsi) < 5 or pd.isna(last_5_rsi.iloc[0]):
                st.info("ข้อมูลยังไม่เพียงพอสำหรับการวิเคราะห์เทรนด์ RSI")
            else:
                all_above_50 = (last_5_rsi > 50).all()
                all_below_50 = (last_5_rsi < 50).all()

                if all_above_50:
                    st.success("📈 **เทรนด์ขาขึ้นชัดเจน!** - ค่า RSI 5 วันล่าสุดอยู่เหนือ 50 ทั้งหมด")
                elif all_below_50:
                    st.error("📉 **เทรนด์ขาลงชัดเจน!** - ค่า RSI 5 วันล่าสุดอยู่ต่ำกว่า 50 ทั้งหมด")
                else:
                    st.info("🟡 **เทรนด์ไม่ชัดเจน** - ค่า RSI เคลื่อนไหวในกรอบ ควรเฝ้ารอเพื่อดูทิศทาง")

            st.write("---")

            # --- ส่วนที่ 5: การแสดงกราฟและตารางข้อมูล ---
            st.subheader('กราฟราคาและตารางข้อมูล 📈')
            st.success(f"ดึงข้อมูลหุ้น {ticker_symbol} สำเร็จ!")
            
            # สร้าง Subplots สำหรับกราฟราคาและ RSI
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})
            fig.subplots_adjust(hspace=0.5)

            # กราฟราคาหลัก (SMA)
            ax1.plot(stock_data['Close'], label='ราคาปิด', color='blue')
            ax1.plot(stock_data['SMA_10'], label='SMA 10 วัน', color='green')
            ax1.plot(stock_data['SMA_20'], label='SMA 20 วัน', color='red')
            ax1.set_title(f'กราฟราคาหุ้น {ticker_symbol} พร้อม SMA')
            ax1.set_xlabel('วันที่')
            ax1.set_ylabel('ราคา')
            ax1.legend()
            ax1.grid(True)
            
            # กราฟ RSI
            ax2.plot(stock_data['RSI'], label='RSI', color='purple')
            ax2.axhline(70, linestyle='--', color='red', label='Overbought (70)')
            ax2.axhline(30, linestyle='--', color='green', label='Oversold (30)')
            ax2.set_title('กราฟ RSI')
            ax2.set_xlabel('วันที่')
            ax2.set_ylabel('RSI')
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig)

            st.write("ตารางข้อมูลล่าสุด:")
            st.write(stock_data.tail())

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
