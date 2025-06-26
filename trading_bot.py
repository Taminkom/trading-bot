import telebot
from tradingview_ta import TA_Handler, Interval
import time
import os
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = '1692203172'

bot = telebot.TeleBot(BOT_TOKEN)

def check_signals():
    pairs = ['BTCUSDT.P', 'DOGEUSDT.P', 'SOLUSDT.P', 'ETHUSDT.P']
    
    for pair in pairs:
        handler = TA_Handler(
            symbol=pair,
            exchange="MEXC",
            screener="crypto",
            interval=Interval.INTERVAL_15_MINUTES
        )
        
        try:
            analysis = handler.get_analysis()
            
            # Obliczanie odległości od wstęg BB
            bb_upper = analysis.indicators['BB.upper']
            bb_lower = analysis.indicators['BB.lower']
            current_high = analysis.indicators['high']
            current_low = analysis.indicators['low']
            
            # Obliczanie tak samo jak w indykatorze
            upperDistance = ((current_high - bb_upper) / bb_upper) * 100 if current_high > bb_upper else 0
            lowerDistance = ((current_low - bb_lower) / bb_lower) * 100 if current_low < bb_lower else 0
            
            # StochRSI
            k = analysis.indicators['Stoch.K']
            d = analysis.indicators['Stoch.D']
            
            # Warunki bazowe
            bb_long_condition = lowerDistance <= -0.15
            bb_short_condition = upperDistance >= 0.15
            
            stoch_long_condition = k <= 20 and d <= 20
            stoch_short_condition = k >= 80 and d >= 80
            
            # Sprawdzanie przecięcia
            cross_condition = abs(k - d) < 0.1  # przybliżenie przecięcia
            
            # Warunki sygnałów
            if bb_long_condition and stoch_long_condition and cross_condition:
                message = f"🟢 Sygnał LONG dla {pair}\nCena: {current_low}\nOdległość od BB: {lowerDistance:.3f}%\nRSI K: {k:.2f}, D: {d:.2f}"
                bot.send_message(CHAT_ID, message)
                print(f"Wysłano sygnał LONG dla {pair}")
            
            if bb_short_condition and stoch_short_condition and cross_condition:
                message = f"🔴 Sygnał SHORT dla {pair}\nCena: {current_high}\nOdległość od BB: {upperDistance:.3f}%\nRSI K: {k:.2f}, D: {d:.2f}"
                bot.send_message(CHAT_ID, message)
                print(f"Wysłano sygnał SHORT dla {pair}")
            
        except Exception as e:
            print(f"Błąd dla {pair}: {e}")

def run_bot():
    print("Bot started...")
    while True:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"Sprawdzam sygnały... {current_time}")
            check_signals()
            print("Czekam 5 minut...")
            time.sleep(300)  # czeka 5 minut
        except Exception as e:
            print(f"Główny błąd: {e}")
            time.sleep(60)  # w przypadku błędu czeka minutę

if __name__ == "__main__":
    run_bot()
