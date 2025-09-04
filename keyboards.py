from telebot import types  # noqa
from translations import translations


def create_language_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn_ru = types.KeyboardButton('🇷🇺 Русский')
    btn_en = types.KeyboardButton('🇺🇸 English')
    btn_cn = types.KeyboardButton('🇨🇳 中文')
    markup.add(btn_ru, btn_en, btn_cn)
    return markup


def create_main_menu_keyboard(lang):
    markup = types.InlineKeyboardMarkup()

    # Получаем переводы для выбранного языка
    lang_translations = translations.get(lang, translations['russian'])

    markup.add(types.InlineKeyboardButton(f"ℹ️ {lang_translations['info']}", callback_data="info"))
    markup.add(types.InlineKeyboardButton(f"⚙️ {lang_translations['settings']}", callback_data="settings"))
    markup.add(types.InlineKeyboardButton(f"📊 {lang_translations['stats']}", callback_data="stats"))

    return markup
