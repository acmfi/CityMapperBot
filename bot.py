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

# Listener

def listener(messages):
    # When new messages arrive TeleBot will call this function.
    for m in messages:
        if m.content_type == 'text':
            # Prints the sent message to the console
            if m.chat.type == 'private':
                print("Chat -> " + str(m.chat.first_name) +
                      " [" + str(m.chat.id) + "]: " + m.text)
        else:
            print("Group -> " + str(m.chat.title) +
                  " [" + str(m.chat.id) + "]: " + m.text)

# Initializing listener
bot.set_update_listener(listener)

########################
# Bot handlers #####
########################


@bot.message_handler(commands=['hello'])
def help(message):
    name = message.from_user.username
    bot.reply_to(message, "Hello " + name + "!")


@bot.message_handler(commands=['whereami'])
def whereiam(m):
    teclado = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itemLoc = types.KeyboardButton("Enviar mi localización", request_location=True)
    teclado.row(itemLoc)
    bot.send_message(m.chat.id, location_text, reply_markup=teclado)

markup = types.InlineKeyboardMarkup()
username_button = types.InlineKeyboardButton("Username", callback_data="username")
id_button = types.InlineKeyboardButton("Id", callback_data="id")
markup.add(username_button, id_button)


@bot.message_handler(commands=['whoami'])
def whoami(m):
    bot.send_message(m.chat.id, "Pulsa un botón: ", disable_notification=True, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "username")
def callback_username(call):
    new_msg = "Tu username es: " + call.from_user.username
    bot.edit_message_text(new_msg, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "id")
def callback_id(call):
    new_msg = "Tu id es: " + str(call.from_user.id)
    bot.edit_message_text(new_msg, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_whoami(call):
    bot.send_message(call.message.chat.id, call.data)

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
