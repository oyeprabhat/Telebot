from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot.")

if __name__ == '__main__':
    keep_alive()

    application = ApplicationBuilder().token("7847553212:AAHYU2Q7zeQFxNvABc8PWJOMTP2APF4kLwY").build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()
