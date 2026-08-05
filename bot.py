import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# API OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Token Telegram
TOKEN = "8909084087:AAEads247ARycSdPPu2IpC0hW3bRQCzDU1g"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌱 Hola, soy el asistente agrícola de FRUTIPAZ. ¿En qué puedo ayudarte?")

# Mensajes normales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente técnico agrícola para campesinos, das respuestas claras y prácticas."},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

# Main
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
