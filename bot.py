import telebot
import json
import re
import datetime
from telebot import types
from citymappy import madBus
from citymappy import madCercanias


# Secure token read ####
with open("./acm.token", "r") as TOKEN:
     bot = telebot.TeleBot(TOKEN.read().strip())



# Load all text to say from json file ####
with open("./dataBot/text.json", "r") as data_text:
    text = json.load(data_text)
    location_text = text['location']
    help_text = text['help']

# EMT api load
with open("./EMTapi.auth", "r") as EMTapi:
    EMTapi_id = EMTapi.readline().strip('\n')
    EMTapi_pass = EMTapi.readline().strip('\n').strip(' ')

# GMaps Static Location api load
with open("./GMapsStaticApi.auth", "r") as GMapsStatic_api:
    GMapsStatic_api_name = GMapsStatic_api.readline().strip('\n')
    GMapsStatic_api_pass = GMapsStatic_api.readline().strip('\n').strip(' ')

with open('./dataBot/admins.json', 'r') as adminData:
    admins = json.load(adminData)
# Listener


def listener(messages):
    # When new messages arrive TeleBot will call this function.
    for m in messages:
        now = str(datetime.datetime.now()).split(' ')[-1].split('.')[0]
        if m.content_type == 'text' or m.content_type == 'location':
            # Prints the sent message to the console
            if m.chat.type == 'private':
                print(now + ":: Chat -> " + str(m.chat.first_name) +
                      " [" + str(m.chat.id) + "]: " + str(m.text))
        else:
            print(now + ":: Group -> " + str(m.chat.title) +
                  " [" + str(m.chat.id) + "]: " + str(m.text))


def isAdmin_fromPrivate(message):
    if message.chat.type == 'private':
        userID = message.from_user.id
        if str(userID) in admins:
            return True
        return False


def format_bus_stop_time(idStop):
    # try:
    response = madBus.get_stop_time(idStop)
    # except Exception:
    #     return "Error. Por favor, intentalo de nuevo."
    response_text = "{: <6}{: ^15}{: >6}\n".format("Linea", "Destino", "Salida")
    try:
        for i in range(response['stops'].__len__()):
            n = str(response['stops'][i]['name'])
            h = str(response['stops'][i]['headsign'])
            h_trunk = h[:14] + (h[14:] and '.')  # Prevent a big headsign
            a = response['stops'][i]['arrival']
            if ((a / 60) > 1):
                a = str(a//60)
            else:
                a = '>>'
            response_text += '{: <6}{: ^15}{: >6}\n'.format(n, h, a)
    except:
        pass
    return '```\n' + response_text + '```'


def format_raildepartures(idStop):
    response = madCercanias.get_departures(idStop)
    response_text = "{: <6}{: ^15}{: >6}\n".format("Linea", "Destino", "Salida")
    # try:
    times = 7
    # Prevent massive departures in text
    if (response['departures'].__len__() < times):
        times = response['departures'].__len__()

    for i in range(times):
        n = str(response['departures'][i]['route_id'])
        d = str(response['departures'][i]['destination'])
        d_trunk = d[:14] + (d[14:] and '.')  # Prevent a big headsign
        is_live = response['departures'][i]['is_live']
        a = str(response['departures'][i]['arrival'])
        if is_live:
            a = str(a//60) + ' min.'
        else:
            a = a.split('T')[-1].split('+')[0].split(':00')[0]  # hh:mm
        response_text += '{: <6}{: <15}{: >6}\n'.format(n, d_trunk, a)
    # except:
    #     pass
    return '```\n' + response_text + '```'


# Initializing listener
bot.set_update_listener(listener)


# USER DATA ########

location = {}

####################
# Bot handlers #####
####################


@bot.message_handler(commands=['help', 'start'])
def help(message):
    bot.reply_to(message, help_text)


@bot.message_handler(func=lambda message: True, content_types=['location'])
def set_location(message):
    user = str(message.chat.id)
    loc = {}
    loc['lat'] = message.location.latitude
    loc['lon'] = message.location.longitude
    location[user] = loc
    print(location[user])


espera = re.compile(r'(/)(\d\d\d?\d?)')


@bot.message_handler(func=lambda m: espera.search(str(m.text)))
def tiempoDeEspera_lambda(m):
    idStop = espera.search(m.text).group(2)
    markup = types.InlineKeyboardMarkup()
    actualizar = types.InlineKeyboardButton(text='Actualizar',
                                            callback_data='rst,' + str(idStop))
    markup.add(actualizar)
    bot.send_message(m.chat.id, format_bus_stop_time(idStop),
                     parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split(',')[0] == 'rst')
def callback_update_stop_time(call):
    idStop = call.data.split(',')[1]
    markup = types.InlineKeyboardMarkup()
    callback_data = 'rst,' + str(idStop)
    actualizar = types.InlineKeyboardButton(text='Actualizar',
                                            callback_data=callback_data)
    markup.add(actualizar)
    now = str(datetime.datetime.now()).split(' ')[-1].split('.')[0]
    message = format_bus_stop_time(idStop) + '_' + now + '_'
    bot.edit_message_text(message,
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          parse_mode="Markdown",
                          reply_markup=markup)


@bot.message_handler(commands=['tiempoDeEspera', 't'])
def tiempoDeEspera(m):
    idStop = m.text.split(' ')[-1]
    markup = types.InlineKeyboardMarkup()
    actualizar = types.InlineKeyboardButton(text='Actualizar',
                                            callback_data='rst' + idStop)
    markup.add(actualizar)
    bot.send_message(m.chat.id, format_bus_stop_time(idStop), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split(',')[0] == 'uca')
def callback_raildepartures(call):
    idStop = call.data.split(',')[-1]
    markup = types.InlineKeyboardMarkup()
    actualizar = types.InlineKeyboardButton(text='Actualizar',
                                            callback_data='uca,' + str(idStop))
    markup.add(actualizar)
    bot.edit_message_text(format_raildepartures(idStop),
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          parse_mode="Markdown",
                          reply_markup=markup)


# CERCANIAS

@bot.message_handler(commands=['cerca'])  # Tiempo de espera de cercanias
def nearby(m):
    user = str(m.chat.id)
    if not str(user) in location:
        response = "Por favor, comparte tu ubicación conmigo y después pregúntame de nuevo:\n /cerca"
        bot.send_message(m.chat.id, response)
        return

    lat = str(location[user]['lat'])
    lon = str(location[user]['lon'])
    request = lat + ',' + lon
    near = madCercanias.nearby(request)
    response = "Elige la estación de Cercanías"
    markup = types.InlineKeyboardMarkup()

    for i in range(near['railstations'].__len__()):
        station = near['railstations'][i]
        button = types.InlineKeyboardButton(text=station['name'],
                                            callback_data=station['id'])
        markup.add(button)

    bot.send_message(m.chat.id, response, reply_markup=markup)


@bot.message_handler(commands=['cercanias', 'c'])  # Tiempo de espera de cercanias
def cercanias_departures(m):
    idStop = m.text.split(' ')[-1]
    markup = types.InlineKeyboardMarkup()
    actualizar = types.InlineKeyboardButton(text='Actualizar',
                                            callback_data='uca' + idStop)
    # uca = update cercanias arrivals
    markup.add(actualizar)
    bot.send_message(m.chat.id,
                     format_raildepartures(idStop),
                     parse_mode="Markdown",
                     reply_markup=markup)


@bot.message_handler(commands=['whereami'])
def whereiam(m):
    teclado = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                        resize_keyboard=True)
    itemLoc = types.KeyboardButton("Compartir mi localización",
                                   request_location=True)
    teclado.row(itemLoc)
    bot.send_message(m.chat.id, location_text, reply_markup=teclado)


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
    if isAdmin_fromPrivate(message):
        bot.reply_to(message,
                     "Reiniciando..")
        print("Updating..")
        exit()
    else:
        pass


bot.skip_pending = True

print("Running...")

bot.polling()
