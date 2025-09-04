translations = {
    'russian': {
        'welcome': '🇷🇺 Добро пожаловать! Рады приветствовать вас в нашем университете. Данный бот поможет вам с оформлением документов для переезда в Россию.',
        'status_choice': 'Выберите свой текущий статус:\n\n1. Ещё не заехал на территорию РФ\n2. Уже нахожусь в России\n\nОт этого будут зависеть ваши дальнейшие действия.',
        'status_option1': 'Ещё не заехал на территорию РФ',
        'status_option2': 'Уже нахожусь в России',
        'citizenship_choice': 'Выберите ваше гражданство:',
        'kazakhstan': 'Казахстан',
        'tajikistan': 'Таджикистан',
        'uzbekistan': 'Узбекистан',
        'china': 'Китай',
        'belarus': 'Беларусь',
        'ukraine': 'Украина',
        'help': 'Это бот для выбора языка. Используйте /start для выбора языка.',
        'menu': 'Главное меню 🏠',
        'options': 'Выберите опцию',
        'back': 'Назад 🔙',
        'info': 'Информация',  # Добавлено
        'settings': 'Настройки',  # Добавлено
        'stats': 'Статистика'  # Добавлено
    },
    'english': {
        'welcome': '🇺🇸 Welcome! We are glad to welcome you to our university. This bot will help you with the paperwork for moving to Russia.',
        'status_choice': 'Choose your current status:\n\n1. Not yet entered the territory of the Russian Federation\n2. Already in Russia\n\nYour further actions will depend on this.',
        'status_option1': 'Not yet entered Russia',
        'status_option2': 'Already in Russia',
        'citizenship_choice': 'Choose your citizenship:',
        'kazakhstan': 'Kazakhstan',
        'tajikistan': 'Tajikistan',
        'uzbekistan': 'Uzbekistan',
        'china': 'China',
        'belarus': 'Belarus',
        'ukraine': 'Ukraine',
        'help': 'This is a language selection bot. Use /start to choose language.',
        'menu': 'Main menu 🏠',
        'options': 'Select an option',
        'back': 'Back 🔙',
        'info': 'Information',  # Добавлено
        'settings': 'Settings',  # Добавлено
        'stats': 'Statistics'  # Добавлено
    },
    'chinese': {
        'welcome': '🇨🇳 欢迎！很高兴欢迎您来到我们大学。这个机器人将帮助您办理移居俄罗斯的文件。',
        'status_choice': '选择您当前的状态:\n\n1. 尚未进入俄罗斯联邦领土\n2. 已经在俄罗斯\n\n您后续的行动将取决于此。',
        'status_option1': '尚未进入俄罗斯',
        'status_option2': '已经在俄罗斯',
        'citizenship_choice': '选择您的国籍:',
        'kazakhstan': '哈萨克斯坦',
        'tajikistan': '塔吉克斯坦',
        'uzbekistan': '乌兹别克斯坦',
        'china': '中国',
        'belarus': '白俄罗斯',
        'ukraine': '乌克兰',
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
    """Получить язык пользователя, возвращает None если пользователя нет в базе"""
    return get_user_language_from_db(user_id)  # Должна возвращать None если пользователя нет

