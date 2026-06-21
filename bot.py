import os
import telebot
from flask import Flask, request
from groq import Groq

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(func=lambda message: True)
def handle_student_request(message):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": message.text}]
        )
        response_text = completion.choices.message.content
        bot.reply_to(message, response_text)
    except Exception as e:
        bot.reply_to(message, "عذراً، حدث خطأ أثناء معالجة الطلب.")
        print(e)

@app.route('/')
def webhook():
    return "البوت يعمل بنجاح كـ Webhook على منصة Vercel!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
