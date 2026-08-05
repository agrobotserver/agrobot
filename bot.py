import telebot
import openai

TOKEN = "8909084087:AAEads247ARycSdPPu2IpC0hW3bRQCzDU1g"
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
openai.api_key = OPENAI_KEY

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🌱 Hola, soy Agrobot 🤖\nPregúntame sobre cultivos, plagas o agricultura.")

@bot.message_handler(func=lambda message: True)
def responder(message):
    user_text = message.text

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en agricultura que ayuda a agricultores con consejos claros y prácticos."},
                {"role": "user", "content": user_text}
            ]
        )

        texto = respuesta['choices'][0]['message']['content']
        bot.reply_to(message, texto)

    except Exception as e:
        bot.reply_to(message, "⚠️ Error con la IA")

bot.infinity_polling()
