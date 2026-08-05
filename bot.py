import telebot

TOKEN = "8909084087:AAEads247ARycSdPPu2IpC0hW3bRQCzDU1g"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🌱 Hola, soy Agrobot \n Estoy listo para ayudarte con información agrícola.")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()
