import telebot
from tradingview_ta import TA_Handler, Interval
import os

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
                
                if current_price < bb_lower and rsi <= 20:
                    message = f"🟢 Sygnał LONG dla {pair}\nCena: {current_price}\nRSI: {rsi}"
                    bot.send_message(CHAT_ID, message)
                
                elif current_price > bb_upper and rsi >= 80:
                    message = f"🔴 Sygnał SHORT dla {pair}\nCena: {current_price}\nRSI: {rsi}"
                    bot.send_message(CHAT_ID, message)
                
        except Exception as e:
            print(f"Błąd dla {pair}: {e}")

if __name__ == "__main__":
    check_signals()
