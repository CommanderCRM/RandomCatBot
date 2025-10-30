from threading import Thread
from time import sleep
import os
import telebot
import random
import sqlite3
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from db import db_creation, add_user_id, update_chat_id
import praw
import requests

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("BOT_API")

reddit = praw.Reddit(
  client_id=os.environ['CLIENT_ID'],
  client_secret=os.environ['SECRET'],
  user_agent="telegram:RandomCatBot:v.1.0.0 (by u/CommanderCRM)",
)

# bot instance initialization
bot = telebot.TeleBot(f"{api_key}")

# sqlite db initialization
db = sqlite3.connect("pusha.db", check_same_thread=False)
db_creation()

generic_str = "Generic🐱"
belly_str = "Belly🐈"
loaf_str = "Loaf🍞"
eyes_str = "Eyes👀"
curled_str = "Curled paws🐾"
black_str = "Black🐈‍⬛"
siamese_str = "Siamese😼"
bengal_str = "Bengal🐆"
mainecoon_str = "Maine Coon🐈"
tucked_str = "Tucked in🦢"
random_str = "Random category🔄"


# start command, just a simple message
@bot.message_handler(commands=["start"])
def handle_start(message):
  bot.reply_to(
    message,
    "Hello and welcome to Random Cat Bot (meow)! Choose between different categories with commands (such as /belly, /loaf, /random) and get random pics of cats!",
  )

  user_id = message.from_user.id
  chat_id = message.chat.id

  add_user_id(user_id, chat_id)
  update_chat_id(user_id, chat_id)

  keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

  generic = KeyboardButton(text=generic_str)
  belly = KeyboardButton(text=belly_str)
  loaf = KeyboardButton(text=loaf_str)
  curled = KeyboardButton(text=curled_str)
  black = KeyboardButton(text=black_str)
  siamese = KeyboardButton(text=siamese_str)
  bengal = KeyboardButton(text=bengal_str)
  mainecoon = KeyboardButton(text=mainecoon_str)
  eyes = KeyboardButton(text=eyes_str)
  tucked = KeyboardButton(text=tucked_str)
  random = KeyboardButton(text=random_str)

  keyboard.row(generic, belly)
  keyboard.row(loaf, curled)
  keyboard.row(black, siamese)
  keyboard.row(bengal, mainecoon)
  keyboard.row(eyes, tucked)
  keyboard.row(random)

  bot.send_message(message.chat.id,
                   "You can also choose with buttons",
                   reply_markup=keyboard)


def handle_subreddit(subreddits, message=None, chat_id=None, direct=False):
  # we can either send a message or reply to a message
  if message:
    msg_chat_id = message.chat.id
    msg_user_id = message.from_user.id
    add_user_id(msg_user_id, msg_chat_id)
    update_chat_id(msg_user_id, msg_chat_id)

  urls = []
  if not isinstance(subreddits, list):
      subreddits = [subreddits]

  # finding pics to download and send
  for subreddit_name in subreddits:
      subreddit = reddit.subreddit(subreddit_name)
      urls.extend([
          post.url for post in subreddit.search('author:"CommanderCRM"')
          if post.url.endswith(".jpg") or post.url.endswith(".png")
      ])

  if not urls:
      return

  # random url is chosen, pic is stored temporarily and then deleted
  url = random.choice(urls)
  response = requests.get(url)
  tmp_file = os.path.join("/tmp", url.split("/")[-1])

  with open(tmp_file, "wb") as f:
    f.write(response.content)

  with open(tmp_file, "rb") as img:
    if direct and chat_id:
        bot.send_photo(chat_id, img)
    elif message:
        bot.send_photo(msg_chat_id, img)

  os.remove(tmp_file)


@bot.message_handler(commands=["generic"])
def handle_generic(message):
  generic_subreddits = ["cats", "calicokittys", "catpics"]
  handle_subreddit(generic_subreddits, message=message)


@bot.message_handler(commands=["loaf"])
def handle_loaf(message):
  handle_subreddit("catloaf", message=message)


@bot.message_handler(commands=["belly"])
def handle_belly(message):
  handle_subreddit("catbellies", message=message)


@bot.message_handler(commands=["eyes"])
def handle_eyes(message):
  handle_subreddit("cattoeyes", message=message)


@bot.message_handler(commands=["curled"])
def handle_curled(message):
  handle_subreddit("curledfeetsies", message=message)


@bot.message_handler(commands=["black"])
def handle_black(message):
  handle_subreddit("blackcats", message=message)


@bot.message_handler(commands=["siamese"])
def handle_siamese(message):
  handle_subreddit("Siamesecats", message=message)


@bot.message_handler(commands=["bengal"])
def handle_bengal(message):
  handle_subreddit("bengalcats", message=message)


@bot.message_handler(commands=["mainecoon"])
def handle_mainecoon(message):
  handle_subreddit("mainecoons", message=message)


@bot.message_handler(commands=["tucked"])
def handle_tucked(message):
  handle_subreddit("tuckedinkitties", message=message)

@bot.message_handler(commands=["random"])
def handle_random(message):
    commands = [handle_generic, handle_belly, handle_loaf, handle_belly, handle_eyes, handle_curled,
                handle_black, handle_siamese, handle_bengal, handle_mainecoon, handle_tucked]
    random_command = random.choice(commands)
    command_splitted = random_command.__name__.split('_')
    bot.reply_to(message, f"{command_splitted[1].capitalize()}!")
    random_command(message)


# when button is pressed (generally)
@bot.message_handler(content_types=["text"])
def handle_messages(message):
  user_id = message.from_user.id
  chat_id = message.chat.id

  add_user_id(user_id, chat_id)
  update_chat_id(user_id, chat_id)

  if generic_str in message.text:
    handle_generic(message)
  elif belly_str in message.text:
    handle_belly(message)
  elif loaf_str in message.text:
    handle_loaf(message)
  elif eyes_str in message.text:
    handle_eyes(message)
  elif curled_str in message.text:
    handle_curled(message)
  elif black_str in message.text:
    handle_black(message)
  elif siamese_str in message.text:
    handle_siamese(message)
  elif bengal_str in message.text:
    handle_bengal(message)
  elif mainecoon_str in message.text:
    handle_maincoon(message)
  elif tucked_str in message.text:
    handle_tucked(message)
  elif random_str in message.text:
    handle_random(message)
  else:
    bot.reply_to(message, "Something is wrong! Try using command from the bot menu")


def daily_dose_of_cats():
  subreddits = ["cats", "calicokittys", "catpics", "catloaf", "cattoeyes", "catswhosqueak", 
                "curledfeetsies", "bengalcats", "blackcats", "mainecoons", "tuckedinkitties", "Siamesecats"]
  result = db.execute("SELECT chat_id FROM user_ids")
  # sending messages to all users which interacted with the bot (present in DB)
  try:
    rows = result.fetchall()
    for row in rows:
      chat_id = row[0]
      bot.send_message(chat_id, "Daily dose of cats")
      handle_subreddit(subreddits, chat_id=chat_id, direct=True)
      sleep(5)
  except Exception as e:
    print("Error occurred while fetching chat IDs from the database:", e)


# sending daily dose of cats each day on 5:00 MSK
scheduler = BlockingScheduler(timezone="Europe/Moscow")
scheduler.add_job(daily_dose_of_cats, "cron", hour=5)


def schedule_checker():
  while True:
    scheduler.start()


Thread(target=schedule_checker).start()

bot.infinity_polling()
