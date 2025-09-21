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
ticker_symbol = st.sidebar.text_input('กรอกชื่อหุ้น:', 'OR')

# --- ส่วนที่ 3: การประมวลผลและวิเคราะห์ข้อมูล ---
if ticker_symbol:
    if not ticker_symbol.upper().endswith('.BK'):
        ticker_symbol += '.BK'

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        
        if stock_data.empty:
            st.error("ไม่พบข้อมูลหุ้นสำหรับชื่อนี้ กรุณาตรวจสอบสัญลักษณ์")
        else:
            st.success(f"ดึงข้อมูลหุ้น {ticker_symbol} สำเร็จ!")
            
            # คำนวณ Simple Moving Average (SMA)
            stock_data['SMA_10'] = stock_data['Close'].rolling(window=10).mean()
            stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()

            # ส่วนเพิ่มใหม่: คำนวณ RSI
            delta = stock_data['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.ewm(com=13, min_periods=14).mean()
            avg_loss = loss.ewm(com=13, min_periods=14).mean()

            rs = avg_gain / avg_loss
            stock_data['RSI'] = 100 - (100 / (1 + rs))

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

            # --- ส่วนที่ 4: การวิเคราะห์และแสดงสัญญาณซื้อ-ขาย ---
            st.subheader('การวิเคราะห์และสัญญาณซื้อ-ขาย 🚦')
            
            # ดึงค่าล่าสุดและตรวจสอบ
            latest_sma_10 = stock_data['SMA_10'].iloc[-1].item() if not stock_data['SMA_10'].empty else None
            latest_sma_20 = stock_data['SMA_20'].iloc[-1].item() if not stock_data['SMA_20'].empty else None
            latest_rsi = stock_data['RSI'].iloc[-1].item() if not stock_data['RSI'].empty else None

            # วิเคราะห์จาก SMA และ RSI
            if pd.isna(latest_sma_10) or pd.isna(latest_sma_20) or pd.isna(latest_rsi):
                st.markdown(
                    f"<p style='color:gray; font-size:20px;'>🟡 **ข้อมูลยังไม่เพียงพอต่อการวิเคราะห์**</p>"
                    "<p>โปรแกรมจะแสดงผลเมื่อมีข้อมูลย้อนหลังครบถ้วน</p>",
                    unsafe_allow_html=True
                )
            else:
                # สรุปคำแนะนำจากข้อมูลทั้ง SMA และ RSI
                buy_signal = latest_sma_10 > latest_sma_20 and latest_rsi < 70
                sell_signal = latest_sma_10 < latest_sma_20 and latest_rsi > 30

                if buy_signal:
                    st.markdown(
                        f"<p style='color:green; font-size:20px;'>💡 **คำแนะนำ: พิจารณา ซื้อ (BUY)**</p>"
                        "<p>เนื่องจากมีแนวโน้มขาขึ้นจาก SMA และ RSI ยังไม่อยู่ในโซนซื้อมากเกินไป</p>",
                        unsafe_allow_html=True
                    )
                elif sell_signal:
                    st.markdown(
                        f"<p style='color:red; font-size:20px;'>🔻 **คำแนะนำ: พิจารณา ขาย (SELL)**</p>"
                        "<p>เนื่องจากมีแนวโน้มขาลงจาก SMA และ RSI ยังไม่อยู่ในโซนขายมากเกินไป</p>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<p style='color:orange; font-size:20px;'>🟡 **คำแนะนำ: รอดูสถานการณ์ (HOLD)**</p>"
                        "<p>ไม่มีสัญญาณซื้อหรือขายที่ชัดเจนจากทั้ง SMA และ RSI ควรเฝ้ารอเพื่อดูแนวโน้ม</p>",
                        unsafe_allow_html=True
                    )

            # แสดงรายละเอียดการวิเคราะห์
            st.write("---")
            st.subheader('รายละเอียดการวิเคราะห์')
            
            st.write(f"**สัญญาณจาก SMA:**")
            if latest_sma_10 > latest_sma_20:
                st.markdown(f"<p>เส้น SMA 10 วัน **อยู่เหนือ** เส้น SMA 20 วัน (แนวโน้มขาขึ้น)</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p>เส้น SMA 10 วัน **อยู่ต่ำกว่า** เส้น SMA 20 วัน (แนวโน้มขาลง)</p>", unsafe_allow_html=True)

            st.write(f"**สัญญาณจาก RSI:**")
            st.markdown(f"<p>ค่า RSI ล่าสุด: **{latest_rsi:.2f}**</p>", unsafe_allow_html=True)
            if latest_rsi > 70:
                st.markdown(f"<p style='color:red;'>อยู่ในโซน **Overbought** (ซื้อมากเกินไป)</p>", unsafe_allow_html=True)
            elif latest_rsi < 30:
                st.markdown(f"<p style='color:green;'>อยู่ในโซน **Oversold** (ขายมากเกินไป)</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p>อยู่ในโซนกลาง</p>", unsafe_allow_html=True)

            st.write("ตารางข้อมูลล่าสุด:")
            st.write(stock_data.tail())

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
