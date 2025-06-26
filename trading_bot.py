import telebot
from tradingview_ta import TA_Handler, Interval
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = '1692203172'

bot = telebot.TeleBot(BOT_TOKEN)

# Zmienne globalne do śledzenia stanu
bars_after_bb_long = {}
bars_after_bb_short = {}
bars_after_cross_long = {}
bars_after_cross_short = {}
waiting_for_cross_long = {}
waiting_for_cross_short = {}
waiting_for_bb_long = {}
waiting_for_bb_short = {}

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
            
            bb_upper = analysis.indicators['BB.upper']
            bb_lower = analysis.indicators['BB.lower']
            current_high = analysis.indicators['high']
            current_low = analysis.indicators['low']
            
            upperDistance = ((current_high - bb_upper) / bb_upper) * 100 if current_high > bb_upper else 0
            lowerDistance = ((current_low - bb_lower) / bb_lower) * 100 if current_low < bb_lower else 0
            
            k = analysis.indicators['Stoch.K']
            d = analysis.indicators['Stoch.D']
            
            cross_condition = abs(k - d) < 0.1

            # Reset liczników dla LONG
            if lowerDistance <= -0.15:
                bars_after_bb_long[pair] = 0
            else:
                bars_after_bb_long[pair] = bars_after_bb_long.get(pair, 0) + 1

            if cross_condition and k <= 20 and d <= 20:
                bars_after_cross_long[pair] = 0
            else:
                bars_after_cross_long[pair] = bars_after_cross_long.get(pair, 0) + 1

            # Reset liczników dla SHORT
            if upperDistance >= 0.15:
                bars_after_bb_short[pair] = 0
            else:
                bars_after_bb_short[pair] = bars_after_bb_short.get(pair, 0) + 1

            if cross_condition and k >= 80 and d >= 80:
                bars_after_cross_short[pair] = 0
            else:
                bars_after_cross_short[pair] = bars_after_cross_short.get(pair, 0) + 1

            # Warunek 1: Najpierw BB, potem czekamy na przecięcie
            if lowerDistance <= -0.15 and k <= 20 and d <= 20:
                waiting_for_cross_long[pair] = True
            if upperDistance >= 0.15 and k >= 80 and d >= 80:
                waiting_for_cross_short[pair] = True

            # Warunek 2: Najpierw przecięcie, potem czekamy na BB
            if cross_condition and k <= 20 and d <= 20:
                waiting_for_bb_long[pair] = True
            if cross_condition and k >= 80 and d >= 80:
                waiting_for_bb_short[pair] = True

            # Reset warunków po 4 świecach
            if bars_after_bb_long.get(pair, 0) > 4:
                waiting_for_cross_long[pair] = False
            if bars_after_bb_short.get(pair, 0) > 4:
                waiting_for_cross_short[pair] = False
            if bars_after_cross_long.get(pair, 0) > 4:
                waiting_for_bb_long[pair] = False
            if bars_after_cross_short.get(pair, 0) > 4:
                waiting_for_bb_short[pair] = False

            # Warunki sygnałów - dokładnie jak w TradingView
            long_condition = (waiting_for_cross_long.get(pair, False) and cross_condition) or (waiting_for_bb_long.get(pair, False) and lowerDistance <= -0.15)
            short_condition = (waiting_for_cross_short.get(pair, False) and cross_condition) or (waiting_for_bb_short.get(pair, False) and upperDistance >= 0.15)

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
