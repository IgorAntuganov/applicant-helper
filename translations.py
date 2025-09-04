translations = {
    'russian': {
        'welcome': 'Добро пожаловать! Выберите язык:',
        'selected': 'Вы выбрали русский язык! 🇷🇺',
        'help': 'Это бот для выбора языка. Используйте /start для выбора языка.',
        'menu': 'Главное меню 🏠',
        'options': 'Выберите опцию',
        'back': 'Назад 🔙',
        'info': 'Информация',  # Добавлено
        'settings': 'Настройки',  # Добавлено
        'stats': 'Статистика'  # Добавлено
    },
    'english': {
        'welcome': 'Welcome! Choose your language:',
        'selected': 'You selected English! 🇺🇸',
        'help': 'This is a language selection bot. Use /start to choose language.',
        'menu': 'Main menu 🏠',
        'options': 'Select an option',
        'back': 'Back 🔙',
        'info': 'Information',  # Добавлено
        'settings': 'Settings',  # Добавлено
        'stats': 'Statistics'  # Добавлено
    },
    'chinese': {
        'welcome': '欢迎！请选择语言:',
        'selected': '您选择了中文！ 🇨🇳',
        'help': '这是一个语言选择机器人。使用 /start 选择语言。',
        'menu': '主菜单 🏠',
        'options': '选择一个选项',
        'back': '返回 🔙',
        'info': '信息',  # Добавлено
        'settings': '设置',  # Добавлено
        'stats': '统计'  # Добавлено
    }
}

from database import get_user_language_from_db
def get_user_language(user_id):
    db_language = get_user_language_from_db(user_id)
    if db_language:
        return db_language
    return 'russian'
