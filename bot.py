import requests
import telebot
import json
import datetime
from telebot import types


# Secure token read ####
with open("./acm.token", "r") as TOKEN:
    bot = telebot.TeleBot(TOKEN.read().strip())

# Load all text to say from json file ####
with open("./dataBot/text.json", "r") as data_text:
    text = json.load(data_text)
    location_text = text['location']

# EMT api load
with open("./EMTapi.auth", "r") as EMTapi:
    EMTapi_id = EMTapi.readline().strip('\n')
    EMTapi_pass = EMTapi.readline().strip('\n').strip(' ')

# GMaps Static Location api load
with open("./GMapsStaticApi.auth", "r") as GMapsStatic_api:
    GMapsStatic_api_name = GMapsStatic_api.readline().strip('\n')
    GMapsStatic_api_pass = GMapsStatic_api.readline().strip('\n').strip(' ')


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

####################
# Bot handlers #####
####################


@bot.message_handler(commands=['hello'])
def help(message):
    name = message.from_user.username
    bot.reply_to(message, "Hello " + name + "!")


@bot.message_handler(commands=['tiempoDeEspera'])
def tiempoDeEspera(m):
    url = 'https://openbus.emtmadrid.es:9443/emt-proxy-server/last/geo/GetArriveStop.php'
    r = requests.post(url, data={'idClient': EMTapi_id, 'passKey': EMTapi_pass,
                                 'idStop': '755'})
    r = r.json()
    line_name1 = r['arrives'][0]['lineId']
    line_name2 = r['arrives'][1]['lineId']
    destination1 = r['arrives'][0]['destination']
    destination2 = r['arrives'][1]['destination']
    time1 = str(datetime.timedelta(seconds=r['arrives'][0]['busTimeLeft']))
    time2 = str(datetime.timedelta(seconds=r['arrives'][1]['busTimeLeft']))
    textEspera1 = "Proximo bus de la linea " + line_name1 + " con destino " + destination1 + " a " + time1
    textEspera2 = "Proximo bus de la linea " + line_name2 + " con destino " + destination2 + " a " + time2
    textEspera = textEspera1 + '\n' + textEspera2
    bot.send_message(m.chat.id, textEspera)


@bot.message_handler(commands=['whereami'])
def whereiam(m):
    teclado = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                        resize_keyboard=True)
    itemLoc = types.KeyboardButton("Compartir mi localización",
                                   request_location=True)
    teclado.row(itemLoc)
    bot.send_message(m.chat.id, location_text, reply_markup=teclado)

markup = types.InlineKeyboardMarkup()
username_button = types.InlineKeyboardButton("Username",
                                             callback_data="username")
id_button = types.InlineKeyboardButton("Id", callback_data="id")
markup.add(username_button, id_button)


@bot.message_handler(commands=['whoami'])
def whoami(m):
    bot.send_message(m.chat.id, "Pulsa un botón: ", disable_notification=True,
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "username")
def callback_username(call):
    new_msg = "Tu username es: " + call.from_user.username
    bot.edit_message_text(new_msg, chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "id")
def callback_id(call):
    new_msg = "Tu id es: " + str(call.from_user.id)
    bot.edit_message_text(new_msg,
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)


@bot.message_handler(commands=['route'])
def route(m):
    with open("./dataBot/testRoute.json", "r") as route:
        route = json.load(route)
        i = 1
        step = 'Paso ' + str(i)
        indicacion = route[step]
    markup = types.InlineKeyboardMarkup()
    izquierda = types.InlineKeyboardButton(text="<<",
                                           callback_data="<<, " + str(i-1))
    derecha = types.InlineKeyboardButton(text=">>",
                                         callback_data=">>, " + str(i+1))
    markup.add(izquierda, derecha)
    bot.send_message(m.chat.id, indicacion, reply_markup=markup)

@bot.callback_query_handler(func=lambda call:
                            (call.data.split(',')[0] == "<<") or
                            (call.data.split(', ')[0] == ">>"))
def callback_route(call):
    with open("./dataBot/testRoute.json", "r") as route:
        route = json.load(route)
        i = int(call.data.split(', ')[1])
        step = 'Paso ' + str(i)
        indicacion = route[step]
    markup = types.InlineKeyboardMarkup()
    izquierda = types.InlineKeyboardButton(text="<<",
                                           callback_data="<<, " +
                                           str((i) % 3 + 1))
    derecha = types.InlineKeyboardButton(text=">>",
                                         callback_data=">>, " +
                                         str((i) % 3 + 1))
    markup.add(izquierda, derecha)
    bot.edit_message_text(indicacion, chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)


@bot.message_handler(commands=['location'])
def send_location(m):
    lat = 40.4101932
    lon = - 3.7391411,
    bot.send_location(m.chat.id, lat, lon)


@bot.message_handler(commands=['update'])
def auto_update(message):
    if False:                               # Not yet
        bot.reply_to(message,
                     "Reiniciando..")
        print("Updating..")
        exit()
    else:

bot.skip_pending = True

print("Running...")

bot.polling()
