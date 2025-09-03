import telebot # noqa
from telebot import types # noqa
from secret import token

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot = telebot.TeleBot(token)

# Словари с переводами для разных языков
translations = {
    'russian': {
        'welcome': 'Добро пожаловать! Выберите язык:',
        'selected': 'Вы выбрали русский язык! 🇷🇺',
        'help': 'Это бот для выбора языка. Используйте /start для выбора языка.',
        'menu': 'Главное меню 🏠',
        'back': 'Назад 🔙'
    },
    'english': {
        'welcome': 'Welcome! Choose your language:',
        'selected': 'You selected English! 🇺🇸',
        'help': 'This is a language selection bot. Use /start to choose language.',
        'menu': 'Main menu 🏠',
        'back': 'Back 🔙'
    },
    'chinese': {
        'welcome': '欢迎！请选择语言:',
        'selected': '您选择了中文！ 🇨🇳',
        'help': '这是一个语言选择机器人。使用 /start 选择语言。',
        'menu': '主菜单 🏠',
        'back': '返回 🔙'
    }
}

# Хранилище выбранных языков пользователей
user_languages = {}


# Функция для получения языка пользователя
def get_user_language(user_id):
    return user_languages.get(user_id, 'russian')


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Создаем клавиатуру с выбором языка
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)

    btn_ru = types.KeyboardButton('🇷🇺 Русский')
    btn_en = types.KeyboardButton('🇺🇸 English')
    btn_cn = types.KeyboardButton('🇨🇳 中文')

    markup.add(btn_ru, btn_en, btn_cn)

    bot.send_message(message.chat.id,
                     "🌍 Выберите язык / Choose language / 选择语言:",
                     reply_markup=markup)


# Обработчик выбора языка
@bot.message_handler(func=lambda message: message.text in ['🇷🇺 Русский', '🇺🇸 English', '🇨🇳 中文'])
def handle_language_selection(message):
    user_id = message.from_user.id

    if message.text == '🇷🇺 Русский':
        user_languages[user_id] = 'russian'
        response = translations['russian']['selected']
    elif message.text == '🇺🇸 English':
        user_languages[user_id] = 'english'
        response = translations['english']['selected']
    elif message.text == '🇨🇳 中文':
        user_languages[user_id] = 'chinese'
        response = translations['chinese']['selected']

    # Создаем основное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(translations[get_user_language(user_id)]['menu']))

    bot.send_message(message.chat.id, response, reply_markup=markup)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    bot.send_message(message.chat.id, translations[lang]['help'])


# Обработчик главного меню
@bot.message_handler(func=lambda message: message.text in [
    translations['russian']['menu'],
    translations['english']['menu'],
    translations['chinese']['menu']
])
def handle_main_menu(message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)

    # Создаем инлайн-клавиатуру с дополнительными опциями
    markup = types.InlineKeyboardMarkup()

    if lang == 'russian':
        markup.add(types.InlineKeyboardButton("ℹ️ Информация", callback_data="info"))
        markup.add(types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
    elif lang == 'english':
        markup.add(types.InlineKeyboardButton("ℹ️ Information", callback_data="info"))
        markup.add(types.InlineKeyboardButton("⚙️ Settings", callback_data="settings"))
    else:
        markup.add(types.InlineKeyboardButton("ℹ️ 信息", callback_data="info"))
        markup.add(types.InlineKeyboardButton("⚙️ 设置", callback_data="settings"))

    bot.send_message(message.chat.id,
                     f"{translations[lang]['menu']}\n\nВыберите опцию:",
                     reply_markup=markup)


# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    lang = get_user_language(user_id)

    if call.data == "info":
        if lang == 'russian':
            text = "📚 Это информационная страница!\nЗдесь может быть полезная информация о боте."
        elif lang == 'english':
            text = "📚 This is the information page!\nHere can be useful information about the bot."
        else:
            text = "📚 这是信息页面！\n这里可以是关于机器人的有用信息。"

        bot.send_message(call.message.chat.id, text)

    elif call.data == "settings":
        # Вернуться к выбору языка
        send_welcome(call.message)


# Обработчик всех текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)

    if lang == 'russian':
        response = f"Вы сказали: {message.text}\nИспользуйте /start для смены языка."
    elif lang == 'english':
        response = f"You said: {message.text}\nUse /start to change language."
    else:
        response = f"你说: {message.text}\n使用 /start 更改语言。"

    bot.send_message(message.chat.id, response)


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)