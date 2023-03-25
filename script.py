import time
import requests
import telebot
import threading
import os

with open('bot_token.txt', 'r') as file:
    token = file.read().strip()

BOT_TOKEN = token
DEFAULT_INTERVAL = 3600  # in seconds
interval = DEFAULT_INTERVAL
is_running = False
timer = None  # Add this line to define timer globally

bot = telebot.TeleBot(BOT_TOKEN)


def get_random_meme():
  try:
    url = 'https://meme-api.com/gimme/ProgrammerHumor'
    response = requests.get(url)

    if response.status_code == 200:
      data = response.json()
      return data['url']
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
  return None


def set_interval(message, minutes: int, firstCall=False):
  global interval, timer
  interval = minutes * 60
  chat_id = message.chat.id  # Store the chat_id from the message

  if not firstCall:
    bot.reply_to(message,
                 f'Successfully set the interval to {minutes} minutes.')

  # Reset the timer with the new interval
  if timer is not None and timer.is_alive():
    timer.cancel()

  timer = threading.Timer(interval, send_meme,
                          args=(chat_id, ))  # Pass the chat_id as an argument
  timer.start()


def send_meme(chat_id):
  meme_url = get_random_meme()
  if meme_url:
    bot.send_photo(chat_id=chat_id, photo=meme_url)
  else:
    bot.send_message(chat_id=chat_id,
                     text='Failed to fetch a meme. Try again later.')


def meme_sending_loop(message):
  global is_running, interval
  while is_running:
    send_meme(message.chat.id)
    time.sleep(interval)


@bot.message_handler(commands=['stop'])
def handle_stop_command(message):
  global is_running

  if is_running:
    is_running = False
    bot.reply_to(message, 'Stopping send memes')
  else:
    bot.reply_to(message, 'Bot is not running!')


@bot.message_handler(commands=['meme'])
def handle_meme_command(message):
  send_meme(message.chat.id)


@bot.message_handler(commands=['set_interval'])
def handle_set_interval_command(message):
  try:
    minutes = int(message.text.split()[1])
    set_interval(message, minutes)  # Pass 'message' to the function
  except (IndexError, ValueError):
    bot.reply_to(message, 'Usage: /setinterval <minutes>')


@bot.message_handler(commands=['start'])
def handle_start_command(message):
  global is_running
  if not is_running:
    is_running = True
    bot.reply_to(message, 'Bot started! Sending memes every hour.')
    set_interval(message, interval // 60, True)  # Set the initial interval

    # Start the meme_sending_loop in a new thread
    meme_loop_thread = threading.Thread(target=meme_sending_loop,
                                        args=(message, ))
    meme_loop_thread.start()
  else:
    bot.reply_to(message, 'Bot is already running!')

bot.polling(none_stop=True)
