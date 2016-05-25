import telebot
from telebot import types

with open ("./acm.token", "r") as TOKEN:
    bot = telebot.TeleBot(TOKEN.read())

@bot.message_handler(commands=['hello'])
def help(message):
    name = message.from_user.username
    bot.reply_to(message, "Hello " + name + "!")

@bot.message_handler(commands=['whereiam'])
def whereiam(m):
    teclado = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itemLoc = types.KeyboardButton("Enviar mi localización", request_location=True)
    teclado.row(itemLoc)
    bot.send_message(m.chat.id, "Para saber dónde estás, necesito que compartas conmigo tu ubicación. Si estás de acuerdo, pulsa sobre el teclado.", reply_markup=teclado)

@bot.message_handler(commands=['location'])
def send_location(m):
    lat = 40.4101932
    lon =-3.7391411,19
    bot.send_location(m.chat.id, lat, lon)

bot.skip_pending = True

print("Running...")
bot.polling()
