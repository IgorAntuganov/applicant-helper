from config import bot
from database import update_user_activity, save_user_to_db, get_user_stats, get_user_language_from_db, \
    check_user_exists, save_user_status
from translations import get_user_language, translations
from keyboards import create_language_keyboard, create_main_menu_keyboard
from telebot import types  # noqa


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    update_user_activity(user_id)

    # Проверяем, есть ли пользователь в базе
    user_exists = check_user_exists(user_id)

    if user_exists:
        # Получаем язык пользователя
        user_language = get_user_language(user_id)
        # Показываем приветственное сообщение на выбранном языке
        show_welcome_message(message.chat.id, user_language)
    else:
        # Предлагаем выбрать язык
        markup = create_language_keyboard()
        bot.send_message(message.chat.id,
                         "🌍 Выберите язык / Choose language / 选择语言:",
                         reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['🇷🇺 Русский', '🇺🇸 English', '🇨🇳 中文'])
def handle_language_selection(message):
    user_id = message.from_user.id

    if message.text == '🇷🇺 Русский':
        language = 'russian'
    elif message.text == '🇺🇸 English':
        language = 'english'
    elif message.text == '🇨🇳 中文':
        language = 'chinese'

    save_user_to_db(user_id, language, message)

    # Показываем приветственное сообщение
    show_welcome_message(message.chat.id, language)


def show_welcome_message(chat_id, language):
    """Показать приветственное сообщение на указанном языке"""
    response = translations[language]['welcome']
    bot.send_message(chat_id, response)

    # После приветствия показываем выбор статуса
    show_status_choice(chat_id, language)


def show_status_choice(chat_id, language):
    """Показать выбор статуса на указанном языке"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    btn1 = types.KeyboardButton(translations[language]['status_option1'])
    btn2 = types.KeyboardButton(translations[language]['status_option2'])

    markup.add(btn1, btn2)

    bot.send_message(chat_id,
                     translations[language]['status_choice'],
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in [
    translations['russian']['status_option1'],
    translations['russian']['status_option2'],
    translations['english']['status_option1'],
    translations['english']['status_option2'],
    translations['chinese']['status_option1'],
    translations['chinese']['status_option2']
])
def handle_status_selection(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    # Определяем выбранный статус
    if message.text in [translations['russian']['status_option1'],
                        translations['english']['status_option1'],
                        translations['chinese']['status_option1']]:
        status = 'not_in_russia'
        if lang == 'russian':
            response = "Вы выбрали: Ещё не заехал на территорию РФ"
        elif lang == 'english':
            response = "You selected: Not yet entered Russia"
        else:
            response = "您选择了: 尚未进入俄罗斯"

    else:
        status = 'in_russia'
        if lang == 'russian':
            response = "Вы выбрали: Уже нахожусь в России"
        elif lang == 'english':
            response = "You selected: Already in Russia"
        else:
            response = "您选择了: 已经在俄罗斯"

    # Сохраняем статус в базу данных
    save_user_status(user_id, status)

    # Показываем главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(translations[lang]['menu']))

    bot.send_message(message.chat.id, response, reply_markup=markup)


# Остальные обработчики остаются без изменений
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