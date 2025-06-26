import telebot
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.text == '/start':
        bot.reply_to(message, "Cześć tutaj Twój tradingowy BOT, mówi mi T4BB. Sprawdzam sygnały na giełdzie MEXC, dla par BTCUSDT.P, ETHUSDT.P, SOLUSDT.P, DOGEUSDT.P ❤️")

# Ignoruj wszystkie inne wiadomości
@bot.message_handler(func=lambda message: True)
def ignore_all(message):
    pass

if __name__ == "__main__":
    bot.polling(none_stop=True)
