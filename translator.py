from gigachat import GigaChat

# Инициализация GigaChat
giga = GigaChat(
    credentials="ODMzNjllOTEtNTQ2MS00NWExLWIyNzAtMmM0ZWZhNDgwOTE5OjNmYmYxNjI5LWVkOWItNDkyMS05YzdiLWEzODZmOTUxM2EyMg==",
    verify_ssl_certs=False
)

class TranslationService:
    """Сервис для перевода текстов"""

    @staticmethod
    def translate_to_english(text: str) -> str:
        try:
            prompt = (f"Переведи на английский без лишнего, без жирного и курсива, "
                      f"никаких двойных звездочек для выделения текста, только данный текст: {text}")
            response = giga.chat(prompt)
            translation = response.choices[0].message.content
            return translation
        except Exception as e:
            return f"Ошибка: {e}"

    @staticmethod
    def translate_to_chinese(text: str) -> str:
        try:
            prompt = (f"Переведи на китайский без лишнего, без жирного и курсива, "
                      f"никаких двойных звездочек для выделения текста, только данный текст: {text}")
            response = giga.chat(prompt)
            translation = response.choices[0].message.content
            return translation
        except Exception as e:
            return f"Ошибка: {e}"
