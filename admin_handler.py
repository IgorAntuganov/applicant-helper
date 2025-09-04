import os
from config import bot
from checklist_service import ChecklistService
from telebot import types  # noqa
from secret import admin_password
import json

# В начале файла изменим CHECKLIST_COMBINATIONS
CHECKLIST_COMBINATIONS = {
    'in_russia_kazakhstan': '🇷🇺 Уже в России • 🇰🇿 Казахstan',
    'in_russia_china': '🇷🇺 Уже в России • 🇨🇳 Китай',
    'in_russia_belarus': '🇷🇺 Уже в России • 🇧🇾 Беларусь',
    'not_in_russia_kazakhstan': '🌍 Еще не в России • 🇰🇿 Казахстан',
    'not_in_russia_china': '🌍 Еще не в России • 🇨🇳 Китай',
    'not_in_russia_belarus': '🌍 Еще не в России • 🇧🇾 Беларусь',
}

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

    markup = types.InlineKeyboardMarkup(row_width=2)

    # Добавляем кнопки для просмотра каждого чеклиста
    for combo_id, combo_name in CHECKLIST_COMBINATIONS.items():
        markup.add(types.InlineKeyboardButton(combo_name, callback_data=f"view_{combo_id}"))

    bot.send_message(
        message.chat.id,
        "👑 Панель администратора\n\nВыберите чеклист для просмотра:",
        reply_markup=markup
    )

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


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_'))
def start_adding_to_checklist(call):
    if not is_admin(call.from_user.id):
        return

    checklist_type = call.data.replace('add_to_', '')

    user_id = call.from_user.id
    user_states[user_id] = 'add_title'
    user_data[user_id] = {'checklist_type': checklist_type}

    bot.send_message(call.message.chat.id, "Введите заголовок пункта:")



@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def view_checklist(call):
    if not is_admin(call.from_user.id):
        return

    checklist_type = call.data.replace('view_', '')
    items = checklist_service.get_items(checklist_type)
    checklist_name = CHECKLIST_COMBINATIONS[checklist_type]

    if not items:
        # Создаем markup с кнопкой добавления
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Добавить пункт", callback_data=f"add_to_{checklist_type}"))

        bot.send_message(call.message.chat.id,
                         f"📭 В чеклисте '{checklist_name}' пока нет пунктов",
                         reply_markup=markup)
        return

    # Отправляем пункты чеклиста
    for item in items:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete__{checklist_type}__{item[0]}"))

        caption = f"<b>{item[1]}</b>\n\n{item[2]}\n\n"
        caption += f"📋 Чеклист: {checklist_name}"

        if item[3] and os.path.exists(item[3]):  # image_path
            with open(item[3], 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo,
                               caption=caption,
                               parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id,
                             caption,
                             parse_mode='HTML', reply_markup=markup)

    # Также отправляем отдельное сообщение с кнопкой добавления в конце
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Добавить пункт", callback_data=f"add_to_{checklist_type}"))

    bot.send_message(call.message.chat.id,
                     f"📋 Чеклист: {checklist_name}\nВсего пунктов: {len(items)}",
                     reply_markup=markup)


# Обработчик всех текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return

    state = user_states.get(user_id)

    if state == 'select_checklist':
        # Находим ID комбинации по названию
        selected_combo = None
        for combo_id, combo_name in CHECKLIST_COMBINATIONS.items():
            if message.text == combo_name:
                selected_combo = combo_id
                break

        if selected_combo:
            user_data[user_id]['checklist_type'] = selected_combo
            user_states[user_id] = 'add_title'
            bot.send_message(message.chat.id, "Введите заголовок пункта:", reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "Отмена":
            cancel_adding(message)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, выберите чеклист из списка")

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


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_item_handler(call):
    if not is_admin(call.from_user.id):
        return

    # Разбираем callback_data: delete_{checklist_type}_{item_id}
    parts = call.data.split('__')
    if len(parts) >= 3:
        checklist_type = parts[1]
        item_id = parts[2]
        checklist_name = CHECKLIST_COMBINATIONS.get(checklist_type, 'Неизвестный чеклист')

        try:
            # Удаляем пункт
            checklist_service.delete_item(checklist_type, item_id)

            # Удаляем сообщение с удаленным пунктом
            bot.delete_message(call.message.chat.id, call.message.message_id)

            # Отправляем подтверждение
            bot.send_message(call.message.chat.id, f"✅ Пункт из чеклиста '{checklist_name}' успешно удален!")

        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Ошибка при удалении: {str(e)}")


def cancel_adding(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "❌ Добавление отменено", reply_markup=types.ReplyKeyboardRemove())
    reset_user_state(user_id)


def finish_adding_item(message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    try:
        checklist_type = data.get('checklist_type')
        item_id = checklist_service.add_item(
            checklist_type,
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
