import telebot
from tradingview_ta import TA_Handler, Interval
import os
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = '1692203172'

bot = telebot.TeleBot(BOT_TOKEN)

def check_signals():
    # Dodajmy test komunikacji z Telegramem
    try:
        test_message = "🔄 Test komunikacji - bot sprawdza sygnały"
        bot.send_message(CHAT_ID, test_message)
        print("Test wiadomości wysłany pomyślnie")
    except Exception as e:
        print(f"Błąd przy wysyłaniu testu: {e}")

    pairs = ['BTCUSDT.P', 'DOGEUSDT.P', 'SOLUSDT.P']
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\nSprawdzanie sygnałów o {current_time}")
    
    for pair in pairs:
        try:
            handler = TA_Handler(
                symbol=pair,
                exchange="MEXC",
                screener="crypto",
                interval=Interval.INTERVAL_15_MINUTES
            )
            
            analysis = handler.get_analysis()
            bb_upper = analysis.indicators['BB.upper']
            bb_lower = analysis.indicators['BB.lower']
            current_price = analysis.indicators['close']
            rsi = analysis.indicators['RSI']
            
            print(f"Sprawdzam {pair}:")
            print(f"RSI: {rsi}")
            print(f"Cena: {current_price}")
            print(f"Górna wstęga BB: {bb_upper}")
            print(f"Dolna wstęga BB: {bb_lower}")
            
            # Dodajmy informację o warunkach
            print(f"Warunki LONG: cena < BB_lower ({current_price < bb_lower}) i RSI <= 20 ({rsi <= 20})")
            print(f"Warunki SHORT: cena > BB_upper ({current_price > bb_upper}) i RSI >= 80 ({rsi >= 80})")
            
            if current_price < bb_lower and rsi <= 20:
                message = f"🟢 Sygnał LONG dla {pair}\nCena: {current_price}\nRSI: {rsi}\nDolna wstęga BB: {bb_lower}"
                bot.send_message(CHAT_ID, message)
                print(f"Wysłano sygnał LONG dla {pair}")
            
            elif current_price > bb_upper and rsi >= 80:
                message = f"🔴 Sygnał SHORT dla {pair}\nCena: {current_price}\nRSI: {rsi}\nGórna wstęga BB: {bb_upper}"
                bot.send_message(CHAT_ID, message)
                print(f"Wysłano sygnał SHORT dla {pair}")
            
        except Exception as e:
            print(f"Błąd dla {pair}: {e}")

if __name__ == "__main__":
    print("Bot started...")
    check_signals()
    print("Bot finished...")
