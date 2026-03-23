import os
import threading
from flask import Flask
import telebot
from openai import OpenAI

# 1. Setup Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

# 2. Initialize OpenAI Client (pointing to Hugging Face)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# 3. Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# 4. Flask Web Server (Required for Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 5. Telegram Bot Logic
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am your AI assistant powered by DeepSeek via Hugging Face. Send me a message!")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # Show "typing..." status in Telegram
        bot.send_chat_action(message.chat.id, 'typing')

        # Call Hugging Face API
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1:novita",
            messages=[
                {
                    "role": "user",
                    "content": message.text,
                },
            ],
        )

        # Get response content
        ai_response = chat_completion.choices[0].message.content
        
        # Send response back to user
        bot.reply_to(message, ai_response)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I encountered an error processing your request.")

# 6. Run Bot and Flask
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start Telegram Bot polling
    print("Bot is starting...")
    bot.polling()
