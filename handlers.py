from config import bot
from database import update_user_activity, save_user_to_db, get_user_stats
from translations import get_user_language, translations
from keyboards import create_language_keyboard, create_main_menu_keyboard
from telebot import types # noqa

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    update_user_activity(user_id)

    markup = create_language_keyboard()
    bot.send_message(message.chat.id,
                     "🌍 Выберите язык / Choose language / 选择语言:",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['🇷🇺 Русский', '🇺🇸 English', '🇨🇳 中文'])
def handle_language_selection(message):
    user_id = message.from_user.id

    if message.text == '🇷🇺 Русский':
        language = 'russian'
        response = translations['russian']['selected']
    elif message.text == '🇺🇸 English':
        language = 'english'
        response = translations['english']['selected']
    elif message.text == '🇨🇳 中文':
        language = 'chinese'
        response = translations['chinese']['selected']

    save_user_to_db(user_id, language, message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(translations[language]['menu']))
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)
    bot.send_message(message.chat.id, translations[lang]['help'])

@bot.message_handler(func=lambda message: message.text in [
    translations['russian']['menu'],
    translations['english']['menu'],
    translations['chinese']['menu']
])
def handle_main_menu(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    markup = create_main_menu_keyboard(lang)
    bot.send_message(message.chat.id,
                     f"{translations[lang]['menu']}\n\n{translations[lang]['options']}",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    print('handle callback')
