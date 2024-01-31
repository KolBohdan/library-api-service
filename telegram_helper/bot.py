import telebot
from django.conf import settings


bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(func=lambda message: True)
def send_create_notification(message: str):
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
