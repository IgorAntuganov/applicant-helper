import telebot
from database import init_database
from config import bot
import handlers

init_database()

if __name__ == "__main__":
    print("Бот запущен...")
    print("База данных инициализирована")
    bot.polling(none_stop=True)
