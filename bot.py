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

with open("./dataBot/testRoute.json", "r") as route:
    route = json.load(route)
    
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
    print("Mensaje de " + m.from_user.first_name)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=str(m.from_user.first_name), callback_data="test"))
    bot.send_message(m.chat.id, "Pulsa en tu nombre: ", disable_notification=True, reply_markup=markup)
    bot.send_message(m.chat.id, "Si no recibes nada tras pulsar, es que no ha funcionado.")
    
@bot.callback_query_handler(func=lambda call: call.data == "test" )
def callback_whoami(call):
    bot.send_message(call.message.chat.id, "Respuesta al callback.")

@bot.message_handler(commands=['route'])
def route(m):
    print(m.from_user.first_name + " ha solicitado una ruta")
    with open("./dataBot/testRoute.json", "r") as route:
        route = json.load(route)
        i = 1
        step = 'Paso ' + str(i)
        indicacion = route[step]
    markup = types.InlineKeyboardMarkup()
    izquierda = types.InlineKeyboardButton(text="<<", callback_data="<<")
    derecha = types.InlineKeyboardButton(text=">>", callback_data="<<")
    markup.add(izquierda, derecha)
    bot.send_message(m.chat.id, indicacion, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: (call.data == "<<") or (call.data == ">>"))
def callback_route(call):
    with open("./dataBot/testRoute.json", "r") as route:
        route = json.load(route)
        i = 2
        step = 'Paso ' + str(i)
        indicacion = route[step]
    markup = types.InlineKeyboardMarkup()
    izquierda = types.InlineKeyboardButton(text="<<", callback_data="<<")
    derecha = types.InlineKeyboardButton(text=">>", callback_data="<<")
    markup.add(izquierda, derecha)
    if call.data == "<<" or call.data == ">>":
        bot.edit_message_text(indicacion,chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)

@bot.message_handler(commands=['location'])
def send_location(m):
    lat = 40.4101932
    lon = - 3.7391411, 19
    bot.send_location(m.chat.id, lat, lon)

bot.skip_pending = True

print("Running...")
bot.polling()
