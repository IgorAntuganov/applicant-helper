import telebot #noqa
from telebot import types # noqa
from secret import token
import sqlite3
import os

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot = telebot.TeleBot(token)


# Инициализация базы данных
def init_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT NOT NULL DEFAULT 'russian',
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Функции для работы с базой данных
def get_user_language_from_db(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def save_user_to_db(user_id, language, message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone()

    if exists:
        # Обновляем язык и время активности
        cursor.execute('''
            UPDATE users 
            SET language = ?, last_activity = CURRENT_TIMESTAMP,
                username = ?, first_name = ?, last_name = ?
            WHERE user_id = ?
        ''', (language, message.from_user.username,
              message.from_user.first_name, message.from_user.last_name, user_id))
    else:
        # Добавляем нового пользователя
        cursor.execute('''
            INSERT INTO users (user_id, language, username, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, language, message.from_user.username,
              message.from_user.first_name, message.from_user.last_name))

    conn.commit()
    conn.close()


def update_user_activity(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET last_activity = CURRENT_TIMESTAMP 
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()


# Инициализируем базу данных при запуске
init_database()

# Словари с переводами для разных языков
translations = {
    'russian': {
        'welcome': 'Добро пожаловать! Выберите язык:',
        'selected': 'Вы выбрали русский язык! 🇷🇺',
        'help': 'Это бот для выбора языка. Используйте /start для выбора языка.',
        'menu': 'Главное меню 🏠',
        'options':'Выберите опцию',
        'back': 'Назад 🔙'
    },
    'english': {
        'welcome': 'Welcome! Choose your language:',
        'selected': 'You selected English! 🇺🇸',
        'help': 'This is a language selection bot. Use /start to choose language.',
        'menu': 'Main menu 🏠',
        'options':'Select an option',
        'back': 'Back 🔙'
    },
    'chinese': {
        'welcome': '欢迎！请选择语言:',
        'selected': '您选择了中文！ 🇨🇳',
        'help': '这是一个语言选择机器人。使用 /start 选择语言。',
        'menu': '主菜单 🏠',
        'options':'选择一个选项',
        'back': '返回 🔙'
    }
}


# Функция для получения языка пользователя
def get_user_language(user_id):
    # Сначала проверяем в базе данных
    db_language = get_user_language_from_db(user_id)
    if db_language:
        return db_language
    return 'russian'  # язык по умолчанию


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    update_user_activity(user_id)

    # Проверяем, есть ли язык пользователя в базе
    user_language = get_user_language_from_db(user_id)

    if user_language:
        # Если язык уже выбран, приветствуем на этом языке
        welcome_text = translations[user_language]['welcome']
        bot.send_message(message.chat.id, welcome_text)
    else:
        # Если язык не выбран, предлагаем выбрать
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
        language = 'russian'
        response = translations['russian']['selected']
    elif message.text == '🇺🇸 English':
        language = 'english'
        response = translations['english']['selected']
    elif message.text == '🇨🇳 中文':
        language = 'chinese'
        response = translations['chinese']['selected']

    # Сохраняем пользователя в базу данных
    save_user_to_db(user_id, language, message)

    # Создаем основное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(translations[language]['menu']))

    bot.send_message(message.chat.id, response, reply_markup=markup)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
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
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    # Создаем инлайн-клавиатуру с дополнительными опциями
    markup = types.InlineKeyboardMarkup()

    if lang == 'russian':
        markup.add(types.InlineKeyboardButton("ℹ️ Информация", callback_data="info"))
        markup.add(types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
        markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="stats"))
    elif lang == 'english':
        markup.add(types.InlineKeyboardButton("ℹ️ Information", callback_data="info"))
        markup.add(types.InlineKeyboardButton("⚙️ Settings", callback_data="settings"))
        markup.add(types.InlineKeyboardButton("📊 Statistics", callback_data="stats"))
    else:
        markup.add(types.InlineKeyboardButton("ℹ️ 信息", callback_data="info"))
        markup.add(types.InlineKeyboardButton("⚙️ 设置", callback_data="settings"))
        markup.add(types.InlineKeyboardButton("📊 统计", callback_data="stats"))

    bot.send_message(message.chat.id,
                     f"{translations[lang]['menu']}\n\n{translations[lang]['options']}",
                     reply_markup=markup)


# Обработчик инлайн-кнопок
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
            text = "📚 这是信息页面！\n这里可以是关于机器人的有用信息。"

        bot.send_message(call.message.chat.id, text)

    elif call.data == "settings":
        # Вернуться к выбору языка
        send_welcome(call.message)

    elif call.data == "stats":
        # Показать статистику
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        conn.close()

        if lang == 'russian':
            text = f"📊 Статистика бота:\nВсего пользователей: {total_users}"
        elif lang == 'english':
            text = f"📊 Bot statistics:\nTotal users: {total_users}"
        else:
            text = f"📊 机器人统计:\n总用户数: {total_users}"

        bot.send_message(call.message.chat.id, text)


# Обработчик всех текстовых сообщений
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
        response = f"你说: {message.text}\n使用 /start 更改语言。"

    bot.send_message(message.chat.id, response)


# Команда для просмотра всех пользователей (только для админа)
@bot.message_handler(commands=['admin_stats'])
def admin_stats(message):
    user_id = message.from_user.id
    # Здесь можно добавить проверку на админа по user_id

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT language, COUNT(*) as count 
        FROM users 
        GROUP BY language
    ''')
    stats = cursor.fetchall()
    conn.close()

    response = "📊 Статистика пользователей:\n"
    for lang, count in stats:
        response += f"{lang}: {count} пользователей\n"

    bot.send_message(message.chat.id, response)


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    print("База данных инициализирована")
    bot.polling(none_stop=True)