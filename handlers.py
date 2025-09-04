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
    user_id = call.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    if call.data == "info":
        if lang == 'russian':
            text = "📚 Это информационная страница!\nЗдесь может быть полезная информация о боте."
        elif lang == 'english':
            text = "📚 This is the information page!\nHere can be useful information about the bot."
        else:
            text = "📚 这是信息页面！\n这里可以是关于机器人的有用信息."
        bot.send_message(call.message.chat.id, text)

    elif call.data == "settings":
        send_welcome(call.message)

    elif call.data == "stats":
        stats = get_user_stats()
        if lang == 'russian':
            text = "📊 Статистика бота:\n"
            for lang_name, count in stats:
                text += f"{lang_name}: {count} пользователей\n"
        elif lang == 'english':
            text = "📊 Bot statistics:\n"
            for lang_name, count in stats:
                text += f"{lang_name}: {count} users\n"
        else:
            text = "📊 机器人统计:\n"
            for lang_name, count in stats:
                text += f"{lang_name}: {count} 用户\n"
        bot.send_message(call.message.chat.id, text)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    if lang == 'russian':
        response = f"Вы сказали: {message.text}\nИспользуйте /start для смены языка."
    elif lang == 'english':
        response = f"You said: {message.text}\nUse /start to change language."
    else:
        response = f"你说: {message.text}\n使用 /start 更改语言."

    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['admin_stats'])
def admin_stats(message):
    user_id = message.from_user.id
    stats = get_user_stats()
    response = "📊 Статистика пользователей:\n"
    for lang, count in stats:
        response += f"{lang}: {count} пользователей\n"
    bot.send_message(message.chat.id, response)
