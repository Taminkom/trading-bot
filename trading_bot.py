import telebot
from tradingview_ta import TA_Handler, Interval
import os

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
            
            upperDistance = ((current_high - bb_upper) / bb_upper) * 100 if current_high > bb_upper else 0
            lowerDistance = ((current_low - bb_lower) / bb_lower) * 100 if current_low < bb_lower else 0
            
            # StochRSI
            k = analysis.indicators['Stoch.K']
            d = analysis.indicators['Stoch.D']
            
            # Sprawdzanie przecięcia
            cross_condition = abs(k - d) < 0.1
            
            # Warunki sygnałów
            if lowerDistance <= -0.15 and k <= 20 and d <= 20 and cross_condition:
                message = f"🟢 Sygnał LONG dla {pair}\nCena: {current_low}\nBB: {lowerDistance:.3f}%\nK: {k:.2f} D: {d:.2f}"
                bot.send_message(CHAT_ID, message)
            
            if upperDistance >= 0.15 and k >= 80 and d >= 80 and cross_condition:
                message = f"🔴 Sygnał SHORT dla {pair}\nCena: {current_high}\nBB: {upperDistance:.3f}%\nK: {k:.2f} D: {d:.2f}"
                bot.send_message(CHAT_ID, message)
            
        except Exception as e:
            print(f"Błąd dla {pair}: {e}")

if __name__ == "__main__":
    check_signals()
