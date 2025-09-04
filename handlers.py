from config import bot
from database import update_user_activity, save_user_to_db, get_user_stats, get_user_language_from_db, \
    check_user_exists, save_user_status
from translations import get_user_language, translations
from keyboards import create_language_keyboard, create_main_menu_keyboard
from telebot import types  # noqa
from database import get_user_data, save_user_citizenship

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


def show_citizenship_choice(chat_id, language):
    """Показать выбор гражданства на указанном языке"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    countries = [
        translations[language]['kazakhstan'],
        translations[language]['tajikistan'],
        translations[language]['uzbekistan'],
        translations[language]['china'],
        translations[language]['belarus'],
        translations[language]['ukraine']
    ]

    # Добавляем кнопки в две колонки
    row1 = [types.KeyboardButton(countries[0]), types.KeyboardButton(countries[1])]
    row2 = [types.KeyboardButton(countries[2]), types.KeyboardButton(countries[3])]
    row3 = [types.KeyboardButton(countries[4]), types.KeyboardButton(countries[5])]

    markup.add(*row1)
    markup.add(*row2)
    markup.add(*row3)

    bot.send_message(chat_id,
                     translations[language]['citizenship_choice'],
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
    else:
        status = 'in_russia'

    # Сохраняем статус в базу данных
    save_user_status(user_id, status)

    # Вместо сообщения о выборе статуса показываем выбор гражданства
    show_citizenship_choice(message.chat.id, lang)


@bot.message_handler(func=lambda message: message.text in [
    # Русские названия
    translations['russian']['kazakhstan'],
    translations['russian']['tajikistan'],
    translations['russian']['uzbekistan'],
    translations['russian']['china'],
    translations['russian']['belarus'],
    translations['russian']['ukraine'],
    # Английские названия
    translations['english']['kazakhstan'],
    translations['english']['tajikistan'],
    translations['english']['uzbekistan'],
    translations['english']['china'],
    translations['english']['belarus'],
    translations['english']['ukraine'],
    # Китайские названия
    translations['chinese']['kazakhstan'],
    translations['chinese']['tajikistan'],
    translations['chinese']['uzbekistan'],
    translations['chinese']['china'],
    translations['chinese']['belarus'],
    translations['chinese']['ukraine']
])
def handle_citizenship_selection(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    # Определяем выбранную страну
    country_mapping = {
        # Русские названия
        translations['russian']['kazakhstan']: 'kazakhstan',
        translations['russian']['tajikistan']: 'tajikistan',
        translations['russian']['uzbekistan']: 'uzbekistan',
        translations['russian']['china']: 'china',
        translations['russian']['belarus']: 'belarus',
        translations['russian']['ukraine']: 'ukraine',
        # Английские названия
        translations['english']['kazakhstan']: 'kazakhstan',
        translations['english']['tajikistan']: 'tajikistan',
        translations['english']['uzbekistan']: 'uzbekistan',
        translations['english']['china']: 'china',
        translations['english']['belarus']: 'belarus',
        translations['english']['ukraine']: 'ukraine',
        # Китайские названия
        translations['chinese']['kazakhstan']: 'kazakhstan',
        translations['chinese']['tajikistan']: 'tajikistan',
        translations['chinese']['uzbekistan']: 'uzbekistan',
        translations['chinese']['china']: 'china',
        translations['chinese']['belarus']: 'belarus',
        translations['chinese']['ukraine']: 'ukraine'
    }

    country_code = country_mapping.get(message.text)

    if country_code:
        # Сохраняем гражданство в базу данных
        save_user_citizenship(user_id, country_code)
        # Показываем финальное сообщение с информацией о пользователе
        show_final_message(message.chat.id, user_id, lang, country_code)


def show_final_message(chat_id, user_id, language, country_code):
    """Показать финальное сообщение с информацией о пользователе"""
    # Получаем данные пользователя
    user_data = get_user_data(user_id)

    if not user_data:
        return

    # Маппинг статусов
    status_names = {
        'not_in_russia': {
            'russian': 'Ещё не заехал на территорию РФ',
            'english': 'Not yet entered Russia',
            'chinese': '尚未进入俄罗斯'
        },
        'in_russia': {
            'russian': 'Уже нахожусь в России',
            'english': 'Already in Russia',
            'chinese': '已经在俄罗斯'
        }
    }

    # Маппинг стран
    country_names = {
        'kazakhstan': {
            'russian': 'Казахстан',
            'english': 'Kazakhstan',
            'chinese': '哈萨克斯坦'
        },
        'tajikistan': {
            'russian': 'Таджикистан',
            'english': 'Tajikistan',
            'chinese': '塔吉克斯坦'
        },
        'uzbekistan': {
            'russian': 'Узбекистан',
            'english': 'Uzbekistan',
            'chinese': '乌兹别克斯坦'
        },
        'china': {
            'russian': 'Китай',
            'english': 'China',
            'chinese': '中国'
        },
        'belarus': {
            'russian': 'Беларусь',
            'english': 'Belarus',
            'chinese': '白俄罗斯'
        },
        'ukraine': {
            'russian': 'Украина',
            'english': 'Ukraine',
            'chinese': '乌克兰'
        }
    }

    status = status_names[user_data['status']][language]
    country = country_names[country_code][language]

    # Формируем сообщение
    if language == 'russian':
        message_text = f"""✅ Вот чек-лист конкретно для вас:

📋 Ваши данные:
• Гражданство: {country}
• Текущий статус: {status}

📝 Чек-листы в разработке
Скоро здесь появятся индивидуальные инструкции для вашей ситуации!"""

    elif language == 'english':
        message_text = f"""✅ Here's a checklist specifically for you:

📋 Your details:
• Citizenship: {country}
• Current status: {status}

📝 Checklists in development
Personalized instructions for your situation will be available soon!"""

    else:  # chinese
        message_text = f"""✅ 这是专门为您准备的清单：

📋 您的详细信息：
• 国籍: {country}
• 当前状态: {status}

📝 清单开发中
针对您情况的个性化说明即将推出！"""

    # Показываем главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(translations[language]['menu']))

    bot.send_message(chat_id, message_text, reply_markup=markup)

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