import telebot
from tradingview_ta import TA_Handler, Interval
import os
from datetime import datetime
import time

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = '1692203172'

bot = telebot.TeleBot(BOT_TOKEN)

def check_signals():
    pairs = ['BTCUSDT.P', 'DOGEUSDT.P', 'SOLUSDT.P']
    
    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\nSprawdzanie sygnałów o {current_time}")
        
        for pair in pairs:
            try:
                handler = TA_Handler(
                    symbol=pair,
                    exchange="MEXC",
                    screener="crypto",
                    interval=Interval.INTERVAL_1_HOUR
                )
                
                analysis = handler.get_analysis()
                bb_upper = analysis.indicators['BB.upper']
                bb_lower = analysis.indicators['BB.lower']
                current_price = analysis.indicators['close']
                rsi = analysis.indicators['RSI']
                
                print(f"Sprawdzam {pair} - RSI: {rsi}")
                
                if current_price < bb_lower and rsi <= 20:
                    message = f"🟢 Sygnał LONG dla {pair}\nCena: {current_price}\nRSI: {rsi}"
                    bot.send_message(CHAT_ID, message)
                    print(f"Wysłano sygnał LONG dla {pair}")
                
                elif current_price > bb_upper and rsi >= 80:
                    message = f"🔴 Sygnał SHORT dla {pair}\nCena: {current_price}\nRSI: {rsi}"
                    bot.send_message(CHAT_ID, message)
                    print(f"Wysłano sygnał SHORT dla {pair}")
                
            except Exception as e:
                print(f"Błąd dla {pair}: {e}")
        
        print("Czekam 5 minut...")
        time.sleep(300)

if __name__ == "__main__":
    print("Bot started...")
    check_signals()
