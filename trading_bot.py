import telebot
from tradingview_ta import TA_Handler, Interval
import time
import os
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = '1692203172'

bot = telebot.TeleBot(BOT_TOKEN)

def check_signals():
    pairs = ['BTCUSDT.P', 'DOGEUSDT.P', 'SOLUSDT.P']
    
    for pair in pairs:
        handler = TA_Handler(
            symbol=pair,
            exchange="MEXC",
            screener="crypto",
            interval=Interval.INTERVAL_1_HOUR
        )
        
        try:
            analysis = handler.get_analysis()
            
            if analysis.indicators['BB.upper'] and analysis.indicators['RSI']:
                bb_upper = analysis.indicators['BB.upper']
                bb_lower = analysis.indicators['BB.lower']
                current_price = analysis.indicators['close']
                rsi = analysis.indicators['RSI']
                
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if current_price < bb_lower and rsi <= 20:
                    message = f"🟢 Sygnał LONG dla {pair}\nCena: {current_price}\nRSI: {rsi}\nCzas: {current_time}"
                    bot.send_message(CHAT_ID, message)
                    print(f"Wysłano sygnał LONG dla {pair}")
                
                elif current_price > bb_upper and rsi >= 80:
                    message = f"🔴 Sygnał SHORT dla {pair}\nCena: {current_price}\nRSI: {rsi}\nCzas: {current_time}"
                    bot.send_message(CHAT_ID, message)
                    print(f"Wysłano sygnał SHORT dla {pair}")
                
        except Exception as e:
            print(f"Błąd dla {pair}: {e}")

def run_bot():
    print("Bot started...")
    while True:  # to jest pętla nieskończona
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"Sprawdzam sygnały... {current_time}")
            check_signals()
            print("Czekam 5 minut...")
            time.sleep(300)  # czeka 5 minut przed następnym sprawdzeniem
        except Exception as e:
            print(f"Główny błąd: {e}")
            time.sleep(60)  # w przypadku błędu czeka minutę

if __name__ == "__main__":
    run_bot()
