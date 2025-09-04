from gigachat import GigaChat

# Инициализация GigaChat
giga = GigaChat(
    credentials="ODMzNjllOTEtNTQ2MS00NWExLWIyNzAtMmM0ZWZhNDgwOTE5OmVhNTlmMGNlLTg4NzgtNDQyMy1iYjk1LThkODVhYjllMWIyMw==",
    verify_ssl_certs=False
)


def test_translate_ru_to_en(russian_text):
    """
    Тестовая функция для перевода с русского на английский
    """
    try:
        prompt = f"Переведи на английский: {russian_text}"
        response = giga.chat(prompt)
        translation = response.choices[0].message.content
        return translation
    except Exception as e:
        return f"Ошибка: {e}"


# Тестирование функции
if __name__ == "__main__":
    # Тестовые примеры
    test_texts = [
        "Привет, как дела?",
        "Я люблю программирование",
        "Сегодня хорошая погода",
        "Спасибо за помощь"
    ]

    print("🧪 Тестирование перевода Russian → English:")
    print("=" * 50)

    for text in test_texts:
        result = test_translate_ru_to_en(text)
        print(f"🇷🇺 Русский: {text}")
        print(f"🇺🇸 Английский: {result}")
        print("-" * 30)