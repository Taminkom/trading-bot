import telebot
from tradingview_ta import TA_Handler, Interval
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = '1692203172'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Cześć tutaj Twój tradingowy BOT, mówi mi T4BB. Sprawdzam sygnały na giełdzie MEXC, dla par BTCUSDT.P, ETHUSDT.P, SOLUSDT.P, DOGEUSDT.P ❤️")

# Słowniki do śledzenia stanu dla każdej pary
waiting_for_cross_long = {}
waiting_for_cross_short = {}
waiting_for_bb_long = {}
waiting_for_bb_short = {}
bars_after_bb_long = {}
bars_after_bb_short = {}
bars_after_cross_long = {}
bars_after_cross_short = {}

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

            # Wariant 1: Najpierw BB, potem StochRSI
            # Dla LONG
            if lowerDistance <= -0.15:
                waiting_for_cross_long[pair] = True
                bars_after_bb_long[pair] = 0
            else:
                bars_after_bb_long[pair] = bars_after_bb_long.get(pair, 0) + 1

            # Dla SHORT
            if upperDistance >= 0.15:
                waiting_for_cross_short[pair] = True
                bars_after_bb_short[pair] = 0
            else:
                bars_after_bb_short[pair] = bars_after_bb_short.get(pair, 0) + 1

            # Wariant 2: Najpierw StochRSI, potem BB
            # Dla LONG
            if cross_condition and k <= 20 and d <= 20:
                waiting_for_bb_long[pair] = True
                bars_after_cross_long[pair] = 0
            else:
                bars_after_cross_long[pair] = bars_after_cross_long.get(pair, 0) + 1

            # Dla SHORT
            if cross_condition and k >= 80 and d >= 80:
                waiting_for_bb_short[pair] = True
                bars_after_cross_short[pair] = 0
            else:
                bars_after_cross_short[pair] = bars_after_cross_short.get(pair, 0) + 1

            # Reset warunków po 2 świecach
            if bars_after_bb_long.get(pair, 0) > 2:
                waiting_for_cross_long[pair] = False
            if bars_after_bb_short.get(pair, 0) > 2:
                waiting_for_cross_short[pair] = False
            if bars_after_cross_long.get(pair, 0) > 2:
                waiting_for_bb_long[pair] = False
            if bars_after_cross_short.get(pair, 0) > 2:
                waiting_for_bb_short[pair] = False

            # Warunki sygnałów - identyczne jak w indykatorze
            long_condition = (waiting_for_cross_long.get(pair, False) and cross_condition and k <= 20 and d <= 20) or (waiting_for_bb_long.get(pair, False) and lowerDistance <= -0.15)
            short_condition = (waiting_for_cross_short.get(pair, False) and cross_condition and k >= 80 and d >= 80) or (waiting_for_bb_short.get(pair, False) and upperDistance >= 0.15)

            if long_condition:
                message = f"🟢 Sygnał LONG dla {pair}\nCena: {current_low}\nBB: {lowerDistance:.3f}%\nK: {k:.2f} D: {d:.2f}"
                bot.send_message(CHAT_ID, message)
            
            if short_condition:
                message = f"🔴 Sygnał SHORT dla {pair}\nCena: {current_high}\nBB: {upperDistance:.3f}%\nK: {k:.2f} D: {d:.2f}"
                bot.send_message(CHAT_ID, message)
            
        except Exception as e:
            print(f"Błąd dla {pair}: {e}")

if __name__ == "__main__":
    check_signals()
