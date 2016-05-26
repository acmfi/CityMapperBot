import telebot
import json
from telebot import types


# Secure token read ####
with open("./acm.token", "r") as TOKEN:
    bot = telebot.TeleBot(TOKEN.read().strip())


# Load all text to say from json file ####
with open("./dataBot/text.json", "r") as data_text:
    text = json.load(data_text)
    location_text = text['location']

########################
# Bot handlers #####
########################


@bot.message_handler(commands=['hello'])
def help(message):
    name = message.from_user.username
    bot.reply_to(message, "Hello " + name + "!")


@bot.message_handler(commands=['whereiam'])
def whereiam(m):
    teclado = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itemLoc = types.KeyboardButton("Enviar mi localización", request_location=True)
    teclado.row(itemLoc)
    bot.send_message(m.chat.id, location_text, reply_markup=teclado)


@bot.message_handler(commands=['whoami'])
def whoami(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=str(m.from_user.first_name), callback_data='test'))
    bot.send_message(m.chat.id, "Lo sabia", disable_notification=True, reply_markup=markup)


@bot.message_handler(commands=['test'])
def test(m):
    print("callback")


@bot.message_handler(commands=['location'])
def send_location(m):
    lat = 40.4101932
    lon = - 3.7391411, 19
    bot.send_location(m.chat.id, lat, lon)

bot.skip_pending = True

print("Running...")
bot.polling()
