import os
import telebot
from openai import OpenAI

# جلب المفاتيح بأمان من سيرفر الاستضافة لمنع سرقتها
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

if not BOT_TOKEN or not AI_API_KEY:
    print("❌ خطأ: لم يتم العثور على المفاتيح في نظام السيرفر!")
    exit()

try:
    client = OpenAI(api_key=AI_API_KEY, base_url="https://api.groq.com/openai/v1")
    bot = telebot.TeleBot(BOT_TOKEN)
    print("✅ تم إعداد البوت بنجاح.")
except Exception as init_error:
    print(f"❌ خطأ في الإعداد: {init_error}")
    exit()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text
    status_message = bot.send_message(chat_id, "⏳ جاري التفكير وتوليد الرد عبر محرك لاما...")
    message_id = status_message.message_id

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_text}]
        )
        ai_reply = completion.choices[0].message.content
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=ai_reply)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🤖 واجه السيرفر مشكلة، أعد المحاولة.")
        except:
            pass

if __name__ == "__main__":
    print("🚀 البوت يعمل الآن في الخلفية...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
