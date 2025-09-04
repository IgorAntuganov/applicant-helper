import os
from config import bot
from checklist_service import ChecklistService
from telebot import types
from secret import admin_password
import json


# Загрузка и сохранение админов
def load_admin_ids():
    try:
        with open('admins.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('admin_ids', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # ID по умолчанию


def save_admin_ids(admin_ids):
    data = {'admin_ids': admin_ids}
    with open('admins.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Загрузка админов при старте
ADMIN_IDS = load_admin_ids()
ADMIN_PASSWORD = admin_password

checklist_service = ChecklistService()

# Хранение временных данных и состояний
user_states = {}  # Будет хранить текущее состояние пользователя: 'add_title', 'add_description', 'add_image'
user_data = {}


def is_admin(user_id):
    return user_id in ADMIN_IDS


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Добавить пункт", callback_data="add_item"))
    markup.add(types.InlineKeyboardButton("📋 Список пунктов", callback_data="list_items"))

    bot.send_message(message.chat.id, "👑 Панель администратора", reply_markup=markup)


@bot.message_handler(commands=['addadmin'])
def add_admin_command(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Используйте: /addadmin <пароль>")
        return

    password = parts[1]
    if password == ADMIN_PASSWORD:
        user_id = message.from_user.id
        if not is_admin(user_id):
            ADMIN_IDS.append(user_id)
            save_admin_ids(ADMIN_IDS)
        bot.send_message(message.chat.id, "✅ Вы добавлены в администраторы!")
    else:
        bot.send_message(message.chat.id, "❌ Неверный пароль")


@bot.callback_query_handler(func=lambda call: call.data == "add_item")
def start_adding_item(call):
    if not is_admin(call.from_user.id):
        return

    user_id = call.from_user.id
    user_states[user_id] = 'add_title'
    user_data[user_id] = {}

    bot.send_message(call.message.chat.id, "Введите заголовок пункта:")


# Обработчик всех текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        return

    state = user_states.get(user_id)

    if state == 'add_title':
        user_data[user_id]['title'] = message.text
        user_states[user_id] = 'add_description'
        bot.send_message(message.chat.id, "Введите описание пункта:")

    elif state == 'add_description':
        user_data[user_id]['description'] = message.text
        user_states[user_id] = 'add_image'

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Пропустить", "Отмена")
        bot.send_message(message.chat.id, "Отправьте картинку или нажмите 'Пропустить'", reply_markup=markup)

    elif state == 'add_image':
        if message.text == "Пропустить":
            user_data[user_id]['image_path'] = None
            finish_adding_item(message)
        elif message.text == "Отмена":
            cancel_adding(message)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте изображение или выберите 'Пропустить'/'Отмена'")


# Обработчик изображений
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        return

    state = user_states.get(user_id)

    if state == 'add_image':
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            filename = f"item_{message.from_user.id}_{message.message_id}.jpg"
            filepath = os.path.join(checklist_service.upload_folder, filename)

            with open(filepath, 'wb') as new_file:
                new_file.write(downloaded_file)

            user_data[user_id]['image_path'] = filepath
            finish_adding_item(message)

        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            reset_user_state(user_id)


def cancel_adding(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "❌ Добавление отменено", reply_markup=types.ReplyKeyboardRemove())
    reset_user_state(user_id)


def finish_adding_item(message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    try:
        item_id = checklist_service.add_item(
            data.get('title'),
            data.get('description'),
            data.get('image_path')
        )

        bot.send_message(message.chat.id, "✅ Пункт успешно добавлен!", reply_markup=types.ReplyKeyboardRemove())
        reset_user_state(user_id)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        reset_user_state(user_id)


def reset_user_state(user_id):
    if user_id in user_states:
        del user_states[user_id]
    if user_id in user_data:
        del user_data[user_id]


@bot.callback_query_handler(func=lambda call: call.data == "list_items")
def show_items_list(call):
    if not is_admin(call.from_user.id):
        return

    items = checklist_service.get_all_active_items()

    if not items:
        bot.send_message(call.message.chat.id, "📭 Пунктов пока нет")
        return

    for item in items:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_{item.id}"))
        markup.add(types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{item.id}"))

        if item.image_path and os.path.exists(item.image_path):
            with open(item.image_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo,
                               caption=f"<b>{item.title}</b>\n\n{item.description}",
                               parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id,
                             f"<b>{item.title}</b>\n\n{item.description}",
                             parse_mode='HTML', reply_markup=markup)
