import telebot
from tradingview_ta import TA_Handler, Interval
import os
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = '1692203172'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Cześć! Bot jest aktywny i sprawdza sygnały dla BTCUSDT.P, DOGEUSDT.P i SOLUSDT.P")

def check_signals():
    pairs = ['BTCUSDT.P', 'DOGEUSDT.P', 'SOLUSDT.P']
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\nSprawdzanie sygnałów o {current_time}")
    
    # Test wysyłania wiadomości
    try:
        test_message = "🔄 Bot działa i sprawdza sygnały..."
        bot.send_message(CHAT_ID, test_message)
        print("Test wiadomości wysłany pomyślnie")
    except Exception as e:
        print(f"Błąd przy wysyłaniu testu: {e}")
    
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
    bot.polling(none_stop=True)
    check_signals()
    print("Bot finished...")
