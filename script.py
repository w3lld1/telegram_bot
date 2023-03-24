import time
import requests
import telebot
from telebot import types

BOT_TOKEN = '5785560958:AAFlufrWRoSbfQk09ZPHvyHuLBUNtZsUCAE'
DEFAULT_INTERVAL = 10800  # 3 hours in seconds
interval = DEFAULT_INTERVAL

bot = telebot.TeleBot(BOT_TOKEN)

def get_random_meme():
    try:
        url = 'https://meme-api.com/gimme'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data['url']
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    return None

def send_meme(chat_id):
    meme_url = get_random_meme()
    if meme_url:
        bot.send_photo(chat_id=chat_id, photo=meme_url)
    else:
        bot.send_message(chat_id=chat_id, text='Failed to fetch a meme. Try again later.')

def send_meme_with_delay(chat_id, delay):
    while True:
        send_meme(chat_id)
        time.sleep(delay)  # Wait for 3 hours (10800 seconds)

@bot.message_handler(commands=['meme'])
def handle_meme_command(message):
    send_meme(message.chat.id)

@bot.message_handler(commands=['setinterval'])
def handle_set_interval_command(message):
    try:
        new_interval = int(message.text.split()[1])
        interval = new_interval * 60  # Convert to seconds
        send_meme_with_delay(message.chat.id, interval)
        bot.reply_to(message, f'Successfully set the interval to {new_interval} minutes.')
    except (IndexError, ValueError):
        bot.reply_to(message, 'Usage: /setinterval <minutes>')


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    bot.reply_to(message, 'Bot started! Sending memes every 3 hours.')

    send_meme_with_delay(message.chat.id, interval)


bot.polling(none_stop=True)
