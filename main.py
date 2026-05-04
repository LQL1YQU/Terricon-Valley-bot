import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler, ConversationHandler
)
from dotenv import load_dotenv
import requests

load_dotenv('.env.example')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
YANDEX_SHEET_ID = os.getenv('YANDEX_SHEET_ID')

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States
START, MENU, INFO, CONFIRM, COLLECT_NAME, COLLECT_EMAIL, COLLECT_PHONE, COLLECT_FORMAT, REGISTERED = range(9)

# Texts
WELCOME_TEXT = "Добро пожаловать в бот практики Terricon Valley! Нажмите 'Старт' для начала."
MAIN_MENU_TEXT = "Выберите раздел:"

INFO_OPTIONS = {
    'how': "Можно попасть через колледж или напрямую обратиться в организацию и согласовать практику.",
    'practice': "Практика включает выполнение практических заданий, а также периодическое участие в лекциях и консультациях.",
    'documents': "Договор на практику, направление от колледжа, дневник практики.",
    'time': "Практикант посещает практику в соответствии с графиком, согласованным колледжем и нашей организацией.",
    'location': "БЦ Возрождение, улица Алалыкина, 12/1.",
    'supervisor': "Айжана.",
    'checking': "Карина.",
    'criteria': "По качеству выполнения задач и соблюдению дедлайнов."
}

RESOURCES_TEXT = """
Полезные ресурсы для практики:

• GitHub — https://github.com/
• Документация Python — https://docs.python.org/
• Telegram Bot API — https://core.telegram.org/bots/api
• python-telegram-bot — https://docs.python-telegram-bot.org/
"""

REGISTER_TEXT = "Отправьте скриншот регистрации."

# --- Меню ---
def get_main_menu():
    return InlineKeyboardMarkup([
            [InlineKeyboardButton("Как можно попасть на практику?", callback_data='how')],
            [InlineKeyboardButton("Что из себя представляет практика?", callback_data='practice')],
            [InlineKeyboardButton("Какие документы нужно подготовить?", callback_data='documents')],
            [InlineKeyboardButton("Сколько времени длится практика?", callback_data='time')],
            [InlineKeyboardButton("Где проходит практика?", callback_data='location')],
            [InlineKeyboardButton("Кто является руководителем?", callback_data='supervisor')],
            [InlineKeyboardButton("Кто проверяет задания?", callback_data='checking')],
            [InlineKeyboardButton("Критерии оценки", callback_data='criteria')],
            [InlineKeyboardButton("Я со всем ознакомился. Хочу пройти практику", callback_data='confirm_yes')]
        ])

# --- Старт ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("Старт", callback_data='start')]]
    await update.message.reply_text(WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    return START

# --- Основной обработчик ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'start':
        await query.edit_message_text(MAIN_MENU_TEXT, reply_markup=get_main_menu())
        return MENU

    elif data in INFO_OPTIONS:
        keyboard = [[InlineKeyboardButton("Назад в меню", callback_data='back_to_menu')]]
        await query.edit_message_text(INFO_OPTIONS[data], reply_markup=InlineKeyboardMarkup(keyboard))
        return INFO

    elif data == 'back_to_menu':
        await query.edit_message_text(MAIN_MENU_TEXT, reply_markup=get_main_menu())
        return MENU

    elif data == 'resources':
        keyboard = [[InlineKeyboardButton("Назад в меню", callback_data='back_to_menu')]]
        await query.edit_message_text(RESOURCES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
        return MENU

    elif data == 'acquainted':
        await query.edit_message_text(
            "Вы ознакомились с материалами. Спасибо!\n\nВыберите следующий раздел:",
            reply_markup=get_main_menu()
        )
        return MENU

    elif data == 'registered':
        await query.edit_message_text(REGISTER_TEXT)
        return REGISTERED

    return MENU

# --- Скриншот регистрации ---
async def registered_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.photo:
        
        keyboard = [[InlineKeyboardButton("Назад в меню", callback_data='back_to_menu')]]
        
        await update.message.reply_text("Скриншот получен. Спасибо!", reply_markup=InlineKeyboardMarkup(keyboard))
        
        return REGISTERED
    
        # --- Yandex отправка ---
        """
        try:
            url = f"https://api.yandex.net/v1/disk/public/resources"
            headers = {"Authorization": f"OAuth {YANDEX_API_KEY}"}
            
            data = {
                "name": context.user_data.get("name"),
                "email": context.user_data.get("email"),
                "phone": context.user_data.get("phone"),
                "format": context.user_data.get("format"),
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                logger.error(f"Yandex API error: {response.text}")

        except Exception as e:
            logger.error(f"Ошибка отправки в Yandex: {e}")
        """

    else:
        await update.message.reply_text("Пожалуйста, отправьте скриншот.")

    return REGISTERED

# --- Сбор данных ---
async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите ваш email:")
    return COLLECT_EMAIL

async def collect_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Введите ваш телефон:")
    return COLLECT_PHONE

async def collect_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Выберите формат: Онлайн / Оффлайн")
    return COLLECT_FORMAT

async def collect_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['format'] = update.message.text

    # --- Yandex отправка ---
    """
    try:
        url = f"https://api.yandex.net/v1/disk/public/resources"
        headers = {"Authorization": f"OAuth {YANDEX_API_KEY}"}

        response = requests.post(url, headers=headers, json=context.user_data)

        if response.status_code != 200:
            logger.error(f"Yandex API error: {response.text}")

    except Exception as e:
        logger.error(f"Ошибка отправки в Yandex: {e}")
    """

    await update.message.reply_text("Данные сохранены. Инструкция: ...")
    return MENU

# --- MAIN ---
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [CallbackQueryHandler(button_handler)],
            MENU: [CallbackQueryHandler(button_handler)],
            INFO: [CallbackQueryHandler(button_handler)],
            COLLECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            COLLECT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)],
            COLLECT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)],
            COLLECT_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_format)],
            REGISTERED: [
                MessageHandler(filters.PHOTO, registered_handler),
                MessageHandler(filters.TEXT, registered_handler),
                CallbackQueryHandler(button_handler)
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
