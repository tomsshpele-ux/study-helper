import os
import telebot
from flask import Flask, request
from openai import OpenAI

# 1. مفاتيح الربط الكاملة والصحيحة الخاصة بك
BOT_TOKEN = "8645432324:AAGo_6iS9lyew9RfQakqLb2ubY1bi8Ds-Do"
AI_API_KEY = "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"

client = OpenAI(
    api_key=AI_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# استقبال بيانات التليجرام وتحويلها عبر السيرفر المجاني
@app.route('/', methods=['POST'])
def getMessage():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    except Exception as e:
        print(e)
        return "Error", 500

# 2. استقبال الرسائل النصية من المستخدمين في التليجرام مع رسالة الانتظار الخاصة بك
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text

    # إرسال رسالة انتظار للمستخدم كما حددت بكودك
    status_message = bot.send_message(chat_id, "⏳ جاري التفكير وتوليد الرد عبر محرك لاما...")
    message_id = status_message.message_id

    try:
        # إرسال الطلب إلى نموذج لاما المستقر
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": user_text}]
        )
        
        # استخراج نص الرد بشكل سليم
        ai_reply = completion.choices[0].message.content
        
        # تعديل رسالة الانتظار بنص الرد النهائي
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=ai_reply)

    except Exception as e:
        error_msg = str(e)
        print(f"❌ حدث خطأ أثناء معالجة الرسالة: {error_msg}")
        
        if "method not allowed" in error_msg.lower() or "405" in error_msg:
            try:
                alt_client = OpenAI(api_key=AI_API_KEY, base_url="https://api.groq.com/")
                alt_completion = alt_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": user_text}]
                )
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=alt_completion.choices[0].message.content)
            except:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🤖 السيرفر واجه خطأ 405 في الاتصال، جاري إعادة التهيئة.")
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⚠️ عذراً، توجد مشكلة في صلاحيات سيرفر الذكاء الاصطناعي حالياً.")
        else:
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🤖 واجه السيرفر مشكلة غير متوقعة، يرجى المحاولة مرة أخرى.")
            except:
                pass

@app.route('/')
def webhook():
    return "السيرفر متوافق ويعمل بنجاح على منصة Vercel!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
