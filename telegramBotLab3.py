from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import g4f
import json
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

chat_mode = {}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Студент", callback_data="Студент")],
        [InlineKeyboardButton("IT-технології", callback_data="IT-технології")],
        [InlineKeyboardButton("Контакти", callback_data="Контакти")],
        [InlineKeyboardButton("Prompt ChatGPT", callback_data="Prompt ChatGPT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Як я можу вам сьогодні допомогти?", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    text = query.data
    if text == "Студент":
        await query.message.reply_text("Студент: Полуянов Владислав\nГрупа: ІО-21")
    elif text == "IT-технології":
        await query.message.reply_text("Python, Java, Linux")
    elif text == "Контакти":
        await query.message.reply_text("Телефон: +380976937073\nEmail: vladpolianov@gmail.com")
    elif text == "Prompt ChatGPT":
        chat_mode[user_id] = True
        await query.message.reply_text(
            "Тепер ваші повідомлення надсилаються ChatGPT. Щоб вийти, напишіть /stop_chat"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if chat_mode.get(user_id):
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": text}],
                provider=None
            )
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text("Виникла помилка при зверненні до ChatGPT.")
    else:
        await update.message.reply_text("Виберіть опцію з меню або натисніть /start")

async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if chat_mode.get(user_id):
        chat_mode.pop(user_id)
        await update.message.reply_text("Ви вийшли з режиму ChatGPT.")
    else:
        await update.message.reply_text("Ви не були в режимі ChatGPT.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop_chat", stop_chat))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущений! Очікування повідомлень...")
    app.run_polling()

if __name__ == "__main__":
    main()

