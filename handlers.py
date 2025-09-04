from config import bot
from database import (
    update_user_activity,
    save_user_to_db,
    get_user_stats,
    get_user_language_from_db,
    check_user_exists,
    save_user_status,
    get_user_data,
    save_user_citizenship
)
from translations import get_user_language, translations, LANGUAGE_MAPPING, STATUS_MAPPING, COUNTRY_MAPPING
from keyboards import create_language_keyboard, create_main_menu_keyboard
from telebot import types
from checklist_service import ChecklistService
from database import is_item_completed, save_completed_item, remove_completed_item

# Константы и инициализация
checklist_service = ChecklistService()


# Вспомогательные функции
def get_country_mapping():
    """Создает маппинг текста сообщения на код страны"""
    mapping = {}
    for lang in ['russian', 'english', 'chinese']:
        for country_code in COUNTRY_MAPPING.keys():
            mapping[translations[lang][country_code]] = country_code
    return mapping


COUNTRY_TEXT_MAPPING = get_country_mapping()


def get_status_options():
    """Возвращает все варианты текста статуса для хэндлера"""
    options = []
    for lang in ['russian', 'english', 'chinese']:
        options.extend([
            translations[lang]['status_option1'],
            translations[lang]['status_option2']
        ])
    return options


def get_menu_options():
    """Возвращает все варианты текста меню для хэндлера"""
    return [
        translations['russian']['menu'],
        translations['english']['menu'],
        translations['chinese']['menu']
    ]


# Хэндлеры
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    markup = create_language_keyboard()
    bot.send_message(
        message.chat.id,
        "🌍 Выберите язык / Choose language / 选择语言:",
        reply_markup=markup
    )


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

    # Добавляем кнопки в три ряда по две кнопки
    for i in range(0, len(countries), 2):
        row_buttons = [
            types.KeyboardButton(countries[i]),
            types.KeyboardButton(countries[i + 1] if i + 1 < len(countries) else None)
        ]
        markup.add(*filter(None, row_buttons))

    bot.send_message(
        chat_id,
        translations[language]['citizenship_choice'],
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text in LANGUAGE_MAPPING.keys())
def handle_language_selection(message):
    user_id = message.from_user.id
    language = LANGUAGE_MAPPING[message.text]

    save_user_to_db(user_id, language, message)
    show_welcome_message(message.chat.id, language)


def show_welcome_message(chat_id, language):
    """Показать приветственное сообщение на указанном языке"""
    bot.send_message(chat_id, translations[language]['welcome'])
    show_status_choice(chat_id, language)


def show_status_choice(chat_id, language):
    """Показать выбор статуса на указанном языке"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    btn1 = types.KeyboardButton(translations[language]['status_option1'])
    btn2 = types.KeyboardButton(translations[language]['status_option2'])

    markup.add(btn1, btn2)

    bot.send_message(
        chat_id,
        translations[language]['status_choice'],
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text in get_status_options())
def handle_status_selection(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    # Определяем статус по тексту сообщения
    status_texts = [
        translations['russian']['status_option1'],
        translations['english']['status_option1'],
        translations['chinese']['status_option1']
    ]
    status = 'not_in_russia' if message.text in status_texts else 'in_russia'

    save_user_status(user_id, status)
    show_citizenship_choice(message.chat.id, lang)


@bot.message_handler(func=lambda message: message.text in COUNTRY_TEXT_MAPPING.keys())
def handle_citizenship_selection(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    country_code = COUNTRY_TEXT_MAPPING.get(message.text)

    if country_code:
        save_user_citizenship(user_id, country_code)
        show_final_message(message.chat.id, user_id, lang, country_code)


# handlers.py
def build_checklist_message(items, language, country, status, user_id, checklist_type):
    """Строит сообщение с чек-листом только с заголовками"""
    templates = {
        'russian': {
            'header': f"""✅ Ваш персонализированный чек-лист:

📋 Ваши данные:
• Гражданство: {country}
• Текущий статус: {status}

📝 Отметьте выполненные пункты:""",
            'empty': "\n\n📋 Чек-лист пока пуст. Администратор добавит инструкции позже.",
            'completed': "✅ ",
            'not_completed': "❌ "
        },
        'english': {
            'header': f"""✅ Your personalized checklist:

📋 Your details:
• Citizenship: {country}
• Current status: {status}

📝 Mark completed items:""",
            'empty': "\n\n📋 Checklist is empty. Administrator will add instructions later.",
            'completed': "✅ ",
            'not_completed': "❌ "
        },
        'chinese': {
            'header': f"""✅ 您的个性化清单：

📋 您的详细信息：
• 国籍: {country}
• 当前状态: {status}

📝 标记已完成的项目：""",
            'empty': "\n\n📋 清单为空。管理员稍后会添加说明。",
            'completed': "✅ ",
            'not_completed': "❌ "
        }
    }

    template = templates[language]
    message_text = template['header']

    if items:
        for index, item in enumerate(items):
            # Проверяем, выполнен ли пункт
            is_completed = is_item_completed(user_id, checklist_type, item['id'])
            status_icon = template['completed'] if is_completed else template['not_completed']

            # Выбираем заголовок на нужном языке
            if language == 'russian':
                title = item['title']
            elif language == 'english':
                title = item['title_en'] or item['title']
            elif language == 'chinese':
                title = item['title_zh'] or item['title']

            message_text += f"\n{index + 1}. {status_icon}{title}"
    else:
        message_text += template['empty']

    return message_text


# handlers.py
def show_final_message(chat_id, user_id, language, country_code):
    """Показать финальное сообщение с чек-листом"""
    user_data = get_user_data(user_id)
    if not user_data:
        return

    status = STATUS_MAPPING[user_data['status']][language]
    country = COUNTRY_MAPPING[country_code][language]

    # Получаем чек-лист
    checklist_type = f"{user_data['status']}_{country_code}"
    items = checklist_service.get_items(checklist_type)

    # Строим сообщение только с заголовками
    message_text = build_checklist_message(items, language, country, status, user_id, checklist_type)

    # Создаем инлайн-кнопки для управления
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Кнопки для отметки выполнения/снятия отметки
    for index, item in enumerate(items):
        is_completed = is_item_completed(user_id, checklist_type, item['id'])
        callback_action = "uncomplete" if is_completed else "complete"

        if language == 'russian':
            button_text = "Снять отметку" if is_completed else "Выполнено"
        elif language == 'english':
            button_text = "Unmark" if is_completed else "Complete"
        elif language == 'chinese':
            button_text = "取消标记" if is_completed else "已完成"

        markup.add(types.InlineKeyboardButton(
            f"{button_text} #{index + 1}",
            callback_data=f"{callback_action}__{checklist_type}__{item['id']}"
        ))

    # Кнопки для просмотра описаний
    if items:
        if language == 'russian':
            button_text = "📋 Показать описания"
        elif language == 'english':
            button_text = "📋 Show descriptions"
        elif language == 'chinese':
            button_text = "📋 显示描述"

        markup.add(types.InlineKeyboardButton(
            button_text,
            callback_data=f"descriptions__{checklist_type}__{language}"
        ))

    # Показываем главное меню в reply-клавиатуре
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(types.KeyboardButton(translations[language]['menu']))

    # Отправляем сообщение
    bot.send_message(chat_id, message_text, reply_markup=reply_markup)

    # Отправляем кнопки управления
    if items:
        if language == 'russian':
            control_text = "Управление пунктами:"
        elif language == 'english':
            control_text = "Item management:"
        elif language == 'chinese':
            control_text = "项目管理:"

        bot.send_message(chat_id, control_text, reply_markup=markup)


@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)
    bot.send_message(message.chat.id, translations[lang]['help'])


# handlers.py
@bot.message_handler(func=lambda message: message.text in get_menu_options())
def handle_main_menu(message):
    user_id = message.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    # Получаем данные пользователя из базы
    user_data = get_user_data(user_id)

    if user_data and user_data.get('status') and user_data.get('citizenship'):
        # Показываем чек-лист пользователя (только заголовки)
        show_final_message(message.chat.id, user_id, lang, user_data['citizenship'])
    else:
        # Если данных нет, просим пройти регистрацию заново
        markup = create_main_menu_keyboard(lang)
        bot.send_message(
            message.chat.id,
            translations[lang].get('need_registration',
                                   '❌ Данные не найдены. Пожалуйста, пройдите регистрацию заново.'),
            reply_markup=markup
        )


# handlers.py
@bot.callback_query_handler(func=lambda call: call.data.startswith(('complete__', 'uncomplete__')))
def handle_item_completion(call):
    user_id = call.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    # Разбираем callback_data
    parts = call.data.split('__')
    if len(parts) >= 3:
        action = parts[0]
        checklist_type = parts[1]
        item_id = int(parts[2])

        # Получаем информацию о пункте
        item = checklist_service.get_item(checklist_type, item_id)
        if item:
            if action == 'complete':
                # Сохраняем пройденный пункт
                save_completed_item(user_id, checklist_type, item_id, item['title'], item['description'])
                message = "✅ Пункт отмечен как выполненный!" if lang == 'russian' else "✅ Item marked as completed!" if lang == 'english' else "✅ 项目标记为已完成!"
            else:
                # Удаляем отметку о выполнении
                remove_completed_item(user_id, checklist_type, item_id)
                message = "❌ Отметка о выполнении снята!" if lang == 'russian' else "❌ Completion mark removed!" if lang == 'english' else "❌ 完成标记已移除!"

            bot.answer_callback_query(call.id, message)

            # Обновляем список пунктов
            user_data = get_user_data(user_id)
            if user_data:
                show_final_message(call.message.chat.id, user_id, lang, user_data['citizenship'])


@bot.callback_query_handler(func=lambda call: call.data.startswith('descriptions__'))
def handle_show_descriptions(call):
    user_id = call.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    parts = call.data.split('__')
    if len(parts) >= 3:
        checklist_type = parts[1]
        target_language = parts[2]  # Язык для отображения описаний
    else:
        checklist_type = parts[1]
        target_language = lang  # По умолчанию используем язык пользователя

    items = checklist_service.get_items(checklist_type)

    if not items:
        bot.answer_callback_query(call.id,
                                  "Нет пунктов для показа" if lang == 'russian' else "No items to show" if lang == 'english' else "没有可显示的项目")
        return

    # Отправляем описания каждого пункта
    for index, item in enumerate(items):
        # Выбираем заголовок и описание на нужном языке
        if target_language == 'russian':
            title = item['title']
            description = item['description']
        elif target_language == 'english':
            title = item['title_en'] or item['title']
            description = item['description_en'] or item['description']
        elif target_language == 'chinese':
            title = item['title_zh'] or item['title']
            description = item['description_zh'] or item['description']

        description_text = f"<b>#{index + 1}: {title}</b>\n\n"
        if description:
            description_text += f"{description}\n\n"
        else:
            if target_language == 'russian':
                description_text += "ℹ️ Описание отсутствует\n\n"
            elif target_language == 'english':
                description_text += "ℹ️ No description available\n\n"
            elif target_language == 'chinese':
                description_text += "ℹ️ 无描述可用\n\n"

        # Проверяем выполнение
        is_completed = is_item_completed(user_id, checklist_type, item['id'])
        if target_language == 'russian':
            status_text = "✅ Выполнено" if is_completed else "❌ Не выполнено"
        elif target_language == 'english':
            status_text = "✅ Completed" if is_completed else "❌ Not completed"
        elif target_language == 'chinese':
            status_text = "✅ 已完成" if is_completed else "❌ 未完成"

        description_text += f"<i>{status_text}</i>"

        bot.send_message(call.message.chat.id, description_text, parse_mode='HTML')

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    update_user_activity(user_id)
    lang = get_user_language(user_id)

    callback_handlers = {
        'info': lambda: bot.send_message(
            call.message.chat.id,
            translations[lang].get('info_text', 'Информация')
        ),
        'settings': lambda: send_welcome(call.message),
    }

    handler = callback_handlers.get(call.data)
    if handler:
        handler()