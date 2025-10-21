from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import g4f
import json


with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["TELEGRAM_TOKEN"]
updater = Updater(TELEGRAM_TOKEN)

chat_mode = {}
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Студент", callback_data="Студент")],
        [InlineKeyboardButton("IT-технології", callback_data="IT-технології")],
        [InlineKeyboardButton("Контакти", callback_data="Контакти")],
        [InlineKeyboardButton("Prompt ChatGPT", callback_data="Prompt ChatGPT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Привіт! Як я можу вам сьогодні допомогти?", reply_markup=reply_markup)


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    text = query.data
    if text == "Студент":
        query.message.reply_text("Студент: Полуянов Владислав\nГрупа: ІО-21")
    elif text == "IT-технології":
        query.message.reply_text("Python, Java, Linux")
    elif text == "Контакти":
        query.message.reply_text("Телефон: +380976937073\nEmail: vladpolianov@gmail.com")
    elif text == "Prompt ChatGPT":
        chat_mode[user_id] = True
        query.message.reply_text(
            "Тепер ваші повідомлення надсилаються ChatGPT. Щоб вийти, напишіть /stop_chat"
        )

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if chat_mode.get(user_id):
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": text}],
                provider=None
            )
            update.message.reply_text(response)
        except Exception as e:
            update.message.reply_text("Виникла помилка при зверненні до ChatGPT.")
    else:
        update.message.reply_text("Виберіть опцію з меню або натисніть /start")


def stop_chat(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if chat_mode.get(user_id):
        chat_mode.pop(user_id)
        update.message.reply_text("Ви вийшли з режиму ChatGPT.")
    else:
        update.message.reply_text("Ви не були в режимі ChatGPT.")
def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop_chat", stop_chat))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Бот запущений! Очікування повідомлень")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()