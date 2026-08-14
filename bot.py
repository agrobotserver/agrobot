import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from openai import OpenAI


# =========================
# CONFIGURACIÓN
# =========================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN = os.getenv("TELEGRAM_TOKEN")


# =========================
# MENÚ PRINCIPAL
# =========================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🌱 Cultivos", callback_data="cultivos"),
            InlineKeyboardButton("💧 Riego", callback_data="riego"),
        ],
        [
            InlineKeyboardButton("🐛 Plagas", callback_data="plagas"),
            InlineKeyboardButton("🤖 Consultar AgroBot", callback_data="consultar"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 ¡Hola! Soy AgroBot, tu asistente agrícola inteligente.\n\n"
        "Puedo ayudarte con cultivos, riego, plagas y recomendaciones agrícolas.\n\n"
        "Selecciona una opción o escríbeme directamente tu pregunta:",
        reply_markup=main_menu(),
    )


# =========================
# BOTONES
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cultivos":
        text = (
            "🌱 **Cultivos**\n\n"
            "Puedo ayudarte con:\n"
            "• Cuidados de cultivos\n"
            "• Siembra\n"
            "• Fertilización\n"
            "• Condiciones de crecimiento\n\n"
            "Escribe tu pregunta, por ejemplo:\n"
            "¿Qué cuidados necesita el tomate?"
        )

    elif query.data == "riego":
        text = (
            "💧 **Riego**\n\n"
            "Puedo ayudarte con recomendaciones sobre:\n"
            "• Frecuencia de riego\n"
            "• Cantidad de agua\n"
            "• Etapa del cultivo\n"
            "• Factores ambientales\n\n"
            "Ejemplo:\n"
            "¿Cada cuánto debo regar el tomate?"
        )

    elif query.data == "plagas":
        text = (
            "🐛 **Plagas y enfermedades**\n\n"
            "Puedes preguntarme sobre síntomas, posibles causas "
            "y medidas de manejo.\n\n"
            "Ejemplo:\n"
            "Las hojas de mi tomate tienen manchas amarillas, ¿qué puede ser?"
        )

    elif query.data == "consultar":
        text = (
            "🤖 **Consultar AgroBot**\n\n"
            "Escribe directamente tu pregunta agrícola y analizaré "
            "la consulta para darte una recomendación."
        )

    else:
        text = "🌱 Escribe tu consulta agrícola."

    await query.message.reply_text(text)


# =========================
# CONSULTAS A OPENAI
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_message = update.message.text

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres AgroBot, un asistente agrícola inteligente "
                        "especializado en ayudar a productores y campesinos. "
                        "Proporciona respuestas claras, prácticas y fáciles "
                        "de entender sobre cultivos, riego, fertilización, "
                        "plagas y enfermedades. "
                        "Cuando no tengas suficiente información, indica "
                        "qué datos necesita proporcionar el usuario. "
                        "No inventes diagnósticos con certeza."
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )

        reply = response.choices[0].message.content

        await update.message.reply_text(reply)

    except Exception as e:
        print(f"Error con OpenAI: {e}")

        await update.message.reply_text(
            "⚠️ Lo siento, ocurrió un problema procesando tu consulta. "
            "Intenta nuevamente en unos segundos."
        )


# =========================
# INICIAR BOT
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

app.run_polling()
