import os
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

# Инициализируем клиента OpenAI (ключ вы передадите в настройках сервера)
# Если запускаете локально, замените os.environ.get на ваш "sk-..." ключ
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "ВАШ_КЛЮЧ_ЕСЛИ_ТЕСТИРУЕТЕ_ДОМА")
client = OpenAI(api_key=OPENAI_API_KEY)

@app.post("/webhook")
async def yandex_dialogs_webhook(request: Request):
    req_data = await request.json()
    
    # Извлекаем текст, который пользователь сказал Алисе
    user_text = req_data["request"]["original_utterance"]
    
    # Проверяем, если это первый запуск навыка (приветствие)
    if req_data["session"]["new"]:
        return {
            "version": req_data["version"],
            "session": req_data["session"],
            "response": {
                "text": "Ahoj! Jsem tvůj ChatGPT asistent. Můžeme mluvit česky nebo rusky. O čem si popovídáme?",
                "end_session": False
            }
        }

    try:
        # Отправляем запрос в ChatGPT (используем быструю и дешевую модель gpt-4o-mini)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant inside Yandex Alice. Respond in the language the user speaks to you (Russian or Czech). Keep answers concise, direct, and suitable for text-to-speech voice playback (avoid markdown, lists, and long paragraphs)."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=300
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = "Извини, произошла ошибка при обращении к ChatGPT."

    # Возвращаем ответ в Яндекс.Диалоги
    return {
        "version": req_data["version"],
        "session": req_data["session"],
        "response": {
            "text": ai_response,
            "end_session": False
        }
    }
