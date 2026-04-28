import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from dotenv import load_dotenv
import requests  # for Yandex API

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')  # for Yandex Tables
YANDEX_SHEET_ID = os.getenv('YANDEX_SHEET_ID')  # sheet ID

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# States for conversation
START, MENU, INFO, CONFIRM, COLLECT_NAME, COLLECT_EMAIL, COLLECT_PHONE, COLLECT_FORMAT, REGISTERED = range(9)

# Texts
WELCOME_TEXT = "Добро пожаловать в бот практики Terricon Valley! Нажмите 'Старт' для начала."

MAIN_MENU_TEXT = "Выберите раздел:"

INFO_OPTIONS = {
    'practice': "Что из себя представляет практика: Практика в Terricon Valley - это возможность получить реальный опыт работы в IT-компании.",
    'documents': "Документы: Необходимы паспорт, СНИЛС и заявление.",
    'deadlines': "Сроки: Практика проходит с июня по август.",
    'location': "Где проходит: Онлайн или в офисе в Москве.",
    'supervisor': "Руководитель: Иван Иванов, ivan@terricon.ru",
    'checking': "Проверка заданий: Задания проверяются еженедельно.",
    'criteria': "Критерии оценки: Качество кода, timeliness, коммуникация."
}

CONFIRM_TEXT = "Вы ознакомились со всей информацией?"

INSTRUCTION_TEXT = "Инструкция по облегченному формату: ... (подробный текст)"

RESOURCES_TEXT = "Ресурсы: Ссылка на GitHub, документация и т.д."

REGISTER_TEXT = "Отправьте скриншот регистрации."

# Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("Старт", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_TEXT, reply_markup=reply_markup)
    return START

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'start':
        keyboard = [
            [InlineKeyboardButton("Что из себя представляет практика", callback_data='practice')],
            [InlineKeyboardButton("Документы", callback_data='documents')],
            [InlineKeyboardButton("Сроки", callback_data='deadlines')],
            [InlineKeyboardButton("Где проходит", callback_data='location')],
            [InlineKeyboardButton("Руководитель", callback_data='supervisor')],
            [InlineKeyboardButton("Проверка заданий", callback_data='checking')],
            [InlineKeyboardButton("Критерии оценки", callback_data='criteria')],
            [InlineKeyboardButton("Я зарегистрировался на мероприятие", callback_data='registered')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(MAIN_MENU_TEXT, reply_markup=reply_markup)
        return MENU

    elif data in INFO_OPTIONS:
        keyboard = [[InlineKeyboardButton("Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(INFO_OPTIONS[data], reply_markup=reply_markup)
        return INFO

    elif data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("Что из себя представляет практика", callback_data='practice')],
            [InlineKeyboardButton("Документы", callback_data='documents')],
            [InlineKeyboardButton("Сроки", callback_data='deadlines')],
            [InlineKeyboardButton("Где проходит", callback_data='location')],
            [InlineKeyboardButton("Руководитель", callback_data='supervisor')],
            [InlineKeyboardButton("Проверка заданий", callback_data='checking')],
            [InlineKeyboardButton("Критерии оценки", callback_data='criteria')],
            [InlineKeyboardButton("Я зарегистрировался на мероприятие", callback_data='registered')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(MAIN_MENU_TEXT, reply_markup=reply_markup)
        return MENU

    elif data == 'confirm_yes':
        await query.edit_message_text("Выберите формат: Онлайн / Оффлайн")
        return COLLECT_FORMAT

    elif data == 'confirm_no':
        await query.edit_message_text("Возвращаемся в меню.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад в меню", callback_data='back_to_menu')]]))
        return MENU

    elif data == 'registered':
        await query.edit_message_text(REGISTER_TEXT)
        return REGISTERED

    return MENU

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Я со всем ознакомился. Хочу пройти практику", callback_data='confirm_yes')],
        [InlineKeyboardButton("Пока прохождение практики для меня не актуально", callback_data='confirm_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(CONFIRM_TEXT, reply_markup=reply_markup)
    return CONFIRM

# After confirm_yes, collect data
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
    # Save to Yandex Sheets
    save_to_sheets(context.user_data)
    await update.message.reply_text("Данные сохранены. Инструкция: " + INSTRUCTION_TEXT)
    keyboard = [[InlineKeyboardButton("Ознакомлен/на", callback_data='acquainted')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите для ознакомления с ресурсами.", reply_markup=reply_markup)
    return MENU

async def acquainted_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.edit_message_text(RESOURCES_TEXT)
    return MENU

async def registered_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle photo
    if update.message.photo:
        await update.message.reply_text("Скриншот получен. Спасибо!")
    else:
        await update.message.reply_text("Пожалуйста, отправьте скриншот.")
    return REGISTERED

def save_to_sheets(data):
    # Placeholder for Yandex Sheets API
    # Use requests to post to Yandex Tables API
    url = f"https://tables.yandex.net/api/v1/workbooks/{YANDEX_SHEET_ID}/tables/Sheet1/rows"
    headers = {'Authorization': f'Bearer {YANDEX_API_KEY}', 'Content-Type': 'application/json'}
    payload = {'data': [data['name'], data['email'], data['phone'], data['format']]}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        logger.info("Data saved to Yandex Sheets")
    else:
        logger.error("Failed to save data")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [CallbackQueryHandler(button_handler)],
            MENU: [CallbackQueryHandler(button_handler)],
            INFO: [CallbackQueryHandler(button_handler)],
            CONFIRM: [CallbackQueryHandler(button_handler)],
            COLLECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            COLLECT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)],
            COLLECT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)],
            COLLECT_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_format)],
            REGISTERED: [MessageHandler(filters.PHOTO, registered_handler), MessageHandler(filters.TEXT, registered_handler)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(acquainted_handler, pattern='acquainted'))

    application.run_polling()

if __name__ == '__main__':
    main()