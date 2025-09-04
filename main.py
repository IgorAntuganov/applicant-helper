import telebot
from database import init_database
from config import bot
from gigachat import GigaChat
import logging
import os
import handlers

init_database()
# Настройка логирования
bot = telebot.TeleBot("8114308825:AAGxr3sY3szFx9UH4iMTGXMfdP7TjqCuDfE")
giga = GigaChat(credentials="ODMzNjllOTEtNTQ2MS00NWExLWIyNzAtMmM0ZWZhNDgwOTE5OmVhNTlmMGNlLTg4NzgtNDQyMy1iYjk1LThkODVhYjllMWIyMw==", verify_ssl_certs=False)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Отправь текст для перевода")

@bot.message_handler(func=lambda message: True)
def translate(message):
    try:
        prompt = f"Переведи: {message.text}"
        response = giga.chat(prompt)
        translation = response.choices[0].message.content
        bot.reply_to(message, f"Перевод: {translation}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

if __name__ == "__main__":
    print("Бот запущен...")
    print("База данных инициализирована")
    bot.polling(none_stop=True)
