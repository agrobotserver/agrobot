import os
import base64

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
            InlineKeyboardButton("📸 Analizar imagen", callback_data="imagen"),
        ],
        [
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
        "Puedo ayudarte con cultivos, riego, plagas y análisis de imágenes.\n\n"
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
            "🌱 *Cultivos*\n\n"
            "Puedo ayudarte con:\n"
            "• Cuidados de cultivos\n"
            "• Siembra\n"
            "• Fertilización\n"
            "• Condiciones de crecimiento\n\n"
            "Ejemplo:\n"
            "¿Qué cuidados necesita el tomate?"
        )

    elif query.data == "riego":
        text = (
            "💧 *Riego*\n\n"
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
            "🐛 *Plagas y enfermedades*\n\n"
            "Puedes preguntarme sobre síntomas, posibles causas "
            "y medidas de manejo.\n\n"
            "También puedes enviarme una foto de la planta "
            "para realizar un análisis visual."
        )

    elif query.data == "imagen":
        text = (
            "📸 *Análisis de imagen*\n\n"
            "Envíame una fotografía clara de tu cultivo, hoja o planta "
            "y AgroBot intentará identificar posibles problemas y "
            "proporcionarte recomendaciones.\n\n"
            "⚠️ Para obtener mejores resultados, procura que la imagen "
            "tenga buena iluminación y que la planta se vea claramente."
        )

    elif query.data == "consultar":
        text = (
            "🤖 *Consultar AgroBot*\n\n"
            "Escribe directamente tu pregunta agrícola y analizaré "
            "la consulta para darte una recomendación."
        )

    else:
        text = "🌱 Escribe tu consulta agrícola."

    await query.message.reply_text(
        text,
        parse_mode="Markdown",
    )


# =========================
# CONSULTAS DE TEXTO
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_message = update.message.text.strip()
    user_message_lower = user_message.lower()

    greetings = [
        "hola",
        "hola!",
        "buenas",
        "buenos dias",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "hey",
        "hello",
        "holaa",
        "holaaa",
    ]

    if user_message_lower in greetings:
        await update.message.reply_text(
            "🌱 ¡Hola! Soy AgroBot, tu asistente agrícola inteligente.\n\n"
            "Puedo ayudarte con cultivos, riego, plagas y análisis de imágenes.\n\n"
            "Selecciona una opción o escríbeme directamente tu pregunta:",
            reply_markup=main_menu(),
        )
        return

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
# ANÁLISIS DE IMÁGENES
# =========================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📸 Recibí tu imagen.\n\n"
        "🔎 Analizando el cultivo, espera un momento..."
    )

    try:
        photo = update.message.photo[-1]

        telegram_file = await context.bot.get_file(photo.file_id)

        image_bytes = await telegram_file.download_as_bytearray()

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres AgroBot, un asistente agrícola especializado "
                        "en análisis visual de cultivos. "
                        "Analiza la imagen proporcionada y describe únicamente "
                        "lo que puedas observar razonablemente. "
                        "Indica posibles problemas, síntomas visibles y "
                        "recomendaciones prácticas. "
                        "No presentes un diagnóstico como certeza absoluta. "
                        "Si la imagen no permite identificar el problema, "
                        "solicita una fotografía más clara."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analiza esta imagen de una planta o cultivo. "
                                "Indica qué observas, cuáles podrían ser las "
                                "causas y qué recomendaciones agrícolas "
                                "podrían ayudar."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                },
            ],
        )

        reply = response.choices[0].message.content

        await update.message.reply_text(
            "🌱 *Análisis de AgroBot*\n\n" + reply,
            parse_mode="Markdown",
        )

    except Exception as e:
        print(f"Error analizando imagen: {e}")

        await update.message.reply_text(
            "⚠️ No pude analizar la imagen en este momento.\n\n"
            "Intenta nuevamente con una fotografía más clara."
        )


# =========================
# INICIAR BOT
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CallbackQueryHandler(button_handler))

app.add_handler(
    MessageHandler(filters.PHOTO, handle_photo)
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

app.run_polling()
