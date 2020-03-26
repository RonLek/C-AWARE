import logging
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, JobQueue
import requests
from functools import wraps
import flag
import reverse_geocoder as rg
from datetime import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)

sd_decider = 0
sd_secondarydecider = 0


def start(update, context):
    # Get CallbackQuery from Update
    query = update.callback_query
    # Get Bot from CallbackContext
    bot = context.bot
    if query != None:
        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text=query.message.text)
    keyboard = [[
        InlineKeyboardButton("Self Diagnosis \U0001F637",
                             callback_data='selfdiagnosis')
    ],
                [
                    
                    InlineKeyboardButton("COVID-19 News and Stats \u23F3",
                                         callback_data='updates')
                ],
                [
                    InlineKeyboardButton(
                        "Contact and Helpline \U0001F198",
                        callback_data='helpline')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=update.effective_chat.id,
                     text='What can I do for you?',
                     reply_markup=reply_markup)

    

    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST


#def start_over(update, context):
#    """Prompt same text & keyboard as `start` does but not as new message"""
#    # Get CallbackQuery from Update
#    query = update.callback_query
#    # Get Bot from CallbackContext
#    bot = context.bot
#    keyboard = [[
#        InlineKeyboardButton("Self Diagnosis \U0001F637",
#                             callback_data='selfdiagnosis')
#    ],
#                [
#                    InlineKeyboardButton(
#                        "View Test Centers Near Me \U0001F3E5",
#                        callback_data='testcenter')
#                ],
#                [
#                    InlineKeyboardButton("Updates about COVID-19 \u23F3",
#                                        callback_data='updates')
#                ]]
#    reply_markup = InlineKeyboardMarkup(keyboard)
#    # Instead of sending a new message, edit the message that
#    # originated the CallbackQuery. This gives the feeling of an
#    # interactive menu.
#    bot.edit_message_text(chat_id=query.message.chat_id,
#                         message_id=query.message.message_id,
#                          text="What can I do for you?",
#                          reply_markup=reply_markup)
#    return FIRST


def button(update, context):
    query = update.callback_query

    query.edit_message_text(text="Selected option: {}".format(query.data))


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def selfdiagnosis(update, context):
    query = update.callback_query
    val = query.data
    print(val)
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("1-9", callback_data='gender1')],
        [InlineKeyboardButton("10-18", callback_data='gender2')],
        [InlineKeyboardButton("19-29", callback_data='gender3')],
        [InlineKeyboardButton("30-49", callback_data='gender4')],
        [InlineKeyboardButton("50-59", callback_data='gender5')],
        [InlineKeyboardButton("60-79", callback_data='gender6')],
        [InlineKeyboardButton("80+", callback_data='gender7')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text="What is your age?",
                          reply_markup=reply_markup)
    return 'sd_1'


def gender(update, context):
    query = update.callback_query
    val = query.data
    print(val)
    bot = context.bot
    keyboard = [[
        InlineKeyboardButton("Male", callback_data='decider'),
        InlineKeyboardButton("Female", callback_data='decider'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text="What is your gender?",
                          reply_markup=reply_markup)
    return 'sd_1'


def decider(update, context):
    query = update.callback_query
    val = query.data
    print(val)
    bot = context.bot
    keyboard = [[
        InlineKeyboardButton("Yes", callback_data='symptomfever1'),
        InlineKeyboardButton("No", callback_data='symptomfever0'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="In the two weeks before you felt sick, did you: \n" +
        "1. Have contact with someone diagnosed with COVID-19 or \n" +
        "2. Live in or visit a place where COVID-19 is spreading",
        reply_markup=reply_markup)
    return 'sd_1'


def symptomfever(update, context):
    query = update.callback_query
    val = query.data
    print(val)
    global sd_decider
    for x in val:
        if x.isdigit():
            if int(x) == 1:
                sd_decider = 1
    bot = context.bot
    keyboard = [[
        InlineKeyboardButton("Yes", callback_data='symptombreath1'),
        InlineKeyboardButton("No", callback_data='symptombreath0'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=
        "Do you have fever or feeling feverish(chills,sweats) \U0001F912 ?",
        reply_markup=reply_markup)
    return 'sd_1'


def symptombreath(update, context):
    query = update.callback_query
    val = query.data
    print(val)
    global sd_secondarydecider
    for x in val:
        if x.isdigit():
            if int(x) == 1:
                sd_secondarydecider = 1
    bot = context.bot
    keyboard = [[
        InlineKeyboardButton("Yes", callback_data='symptomcough1'),
        InlineKeyboardButton("No", callback_data='symptomcough0'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text="Do you have shortness of breath \U0001F975 ?",
                          reply_markup=reply_markup)
    return 'sd_1'


def symptomcough(update, context):
    query = update.callback_query
    val = query.data
    print(val)
    global sd_secondarydecider
    for x in val:
        if x.isdigit():
            if int(x) == 1:
                sd_secondarydecider = 1
    bot = context.bot
    keyboard = [[
        InlineKeyboardButton("Yes", callback_data='diagnosis1'),
        InlineKeyboardButton("No", callback_data='diagnosis0'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text="Do you have cough \U0001F927?",
                          reply_markup=reply_markup)
    return 'sd_1'


def diagnosis(update, context):
    query = update.callback_query
    val = query.data
    print(val)
    global sd_secondarydecider
    for x in val:
        if x.isdigit():
            if int(x) == 1:
                sd_secondarydecider = 1
    bot = context.bot
    global sd_decider
    if sd_decider and sd_secondarydecider:
        bot.send_message(
            chat_id=update.effective_chat.id,
            text=
            "Stay home and take care of yourself. Call your provider if you get worse."
            +
            "Sorry you’re feeling ill. You have one or more symptom(s) that may be related to COVID-19."
        )
    elif sd_secondarydecider:
        bot.send_message(
            chat_id=update.effective_chat.id,
            text=
            "Sorry you’re feeling ill. Call your provider if you get worse. " +
            "Since you haven't directly come in contact with someone diagnosed with COVID-19 or live in or visit a place where COVID-19 "
            +
            "is spreading there are less chances of you contracting COVID-19. Stay at home and monitor your symptoms"
        )
    else:
        bot.send_message(
            chat_id=update.effective_chat.id,
            text=
            "Since you haven't directly come in contact with someone diagnosed with COVID-19 or live in or visit a place where COVID-19 "
            +
            "is spreading there are less chances of you contracting COVID-19.\n Please stay indoors."
        )


def updates(update, context):
    """Shows Update Choices"""
    query = update.callback_query
    bot = context.bot
    keyboard = [[
        InlineKeyboardButton("Latest News \U0001F5DE",
                             callback_data='latestnews'),
        InlineKeyboardButton("Stats \U0001F4CA", callback_data='stats')
    ],
                [
                    InlineKeyboardButton("Return to Previous Menu \U0001F519",
                                         callback_data='return')
                ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text="Choose an Option",
                          reply_markup=reply_markup)
    return 'Update1'


def getstats(param):
    if param == 'all':
        r = requests.get(url='https://corona.lmao.ninja/all')
        data = r.json()
    elif param == 'worst5':
        r = requests.get(url='https://corona.lmao.ninja/countries?sort=cases')
        data = r.json()
        data = data[:5]
    elif param == 'least5':
        r = requests.get(url='https://corona.lmao.ninja/countries?sort=cases')
        data = r.json()
        data = data[-5:]
    elif param == 'india':
        r = requests.get(url='https://corona.lmao.ninja/countries/India')
        data = r.json()
    return data


def send_typing_action(func):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id,
                                     action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


@send_typing_action
def stats(update, context):
    """Shows Stats"""
    print(update == None)
    query = update.callback_query
    bot = context.bot

    if query != None:
        bot.edit_message_text(chat_id=update.effective_chat.id,
                              message_id=query.message.message_id,
                              text="Done")

    keyboard = [[
        InlineKeyboardButton("Top 5 Worst Hit Countries",
                             callback_data='worst5')
    ],
                [
                    InlineKeyboardButton("Top 5 Least Hit Countries",
                                         callback_data='least5')
                ],
                [
                    InlineKeyboardButton("Get India Stats",
                                         callback_data='mycountry')
                ],
                [
                    InlineKeyboardButton("Return to Previous Menu \U0001F519",
                                         callback_data='return')
                ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    data = getstats('all')
    print(data)
    print(update == False)
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=
        "\U0001F30E COVID-19 WORLD IMPACT \U0001F30E \n\n \U0001F9A0 Total Cases: "
        + str(data['cases']) + "\n \u26B0 Total Deaths: " +
        str(data['deaths']) + "\n \U0001F604 Total Recovered: " +
        str(data['recovered']) + "\n",
        reply_markup=reply_markup)
    return 'st_1'


@send_typing_action
def worst5(update, context):
    """Shows Worst 5 Countries Hit by COVID-19"""
    query = update.callback_query
    bot = context.bot

    if query != None:
        bot.edit_message_text(chat_id=update.effective_chat.id,
                              message_id=query.message.message_id,
                              text=query.message.text)

    keyboard = [[
        InlineKeyboardButton("Return to Previous Menu \U0001F519",
                             callback_data='return')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    data = getstats('worst5')
    bot.send_message(
        chat_id=update.effective_chat.id,
        text="\uF3F4 TOP 5 WORST HIT \uF3F4 \n\n\u0031 " +
        str(data[0]['country']) + " " +
        flag.flag(str(data[0]['countryInfo']['iso2'])) + "\n Total Cases: " +
        str(data[0]['cases']) + "\n Cases Today: " +
        str(data[0]['todayCases']) + "\n Total Deaths: " +
        str(data[0]['deaths']) + "\n Deaths Today: " +
        str(data[0]['todayDeaths']) + "\n Recovered: " +
        str(data[0]['recovered']) + "\n\n \u0032 " + str(data[1]['country']) +
        " " + flag.flag(str(data[1]['countryInfo']['iso2'])) +
        "\n Total Cases: " + str(data[1]['cases']) + "\n Cases Today: " +
        str(data[1]['todayCases']) + "\n Total Deaths: " +
        str(data[1]['deaths']) + "\n Deaths Today: " +
        str(data[1]['todayDeaths']) + "\n Recovered: " +
        str(data[1]['recovered']) + "\n\n \u0033 " + str(data[2]['country']) +
        " " + flag.flag('US') + "\n Total Cases: " + str(data[2]['cases']) +
        "\n Cases Today: " + str(data[2]['todayCases']) + "\n Total Deaths: " +
        str(data[2]['deaths']) + "\n Deaths Today: " +
        str(data[2]['todayDeaths']) + "\n Recovered: " +
        str(data[2]['recovered']) + "\n\n \u0034 " + str(data[3]['country']) +
        " " + flag.flag(str(data[3]['countryInfo']['iso2'])) +
        "\n Total Cases: " + str(data[3]['cases']) + "\n Cases Today: " +
        str(data[3]['todayCases']) + "\n Total Deaths: " +
        str(data[3]['deaths']) + "\n Deaths Today: " +
        str(data[3]['todayDeaths']) + "\n Recovered: " +
        str(data[3]['recovered']) + "\n\n \u0035 " + str(data[4]['country']) +
        " " + flag.flag(str(data[4]['countryInfo']['iso2'])) +
        "\n Total Cases: " + str(data[4]['cases']) + "\n Cases Today: " +
        str(data[4]['todayCases']) + "\n Total Deaths: " +
        str(data[4]['deaths']) + "\n Deaths Today: " +
        str(data[4]['todayDeaths']) + "\n Recovered: " +
        str(data[4]['recovered']),
        reply_markup=reply_markup)
    return FIRST


@send_typing_action
def least5(update, context):
    """Shows Worst 5 Countries Hit by COVID-19"""
    query = update.callback_query
    bot = context.bot

    if query != None:
        bot.edit_message_text(chat_id=update.effective_chat.id,
                              message_id=query.message.message_id,
                              text=query.message.text)

    keyboard = [[
        InlineKeyboardButton("Return to Previous Menu \U0001F519",
                             callback_data='return')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    data = getstats('worst5')
    bot.send_message(
        chat_id=update.effective_chat.id,
        text="\U0001F6A9 TOP 5 LEAST HIT \U0001F6A9 \n\n \u0031" +
        data[4]['country'] + " " +
        flag.flag(str(data[0]['countryInfo']['iso2'])) + "\n Total Cases: " +
        str(data[4]['cases']) + "\n Cases Today: " +
        str(data[4]['todayCases']) + "\n Total Deaths: " +
        str(data[4]['deaths']) + "\n Deaths Today: " +
        str(data[4]['todayDeaths']) + "\n Recovered: " +
        str(data[4]['recovered']) + "\n\n \u0032 " + str(data[3]['country']) +
        " " + flag.flag(str(data[3]['countryInfo']['iso2'])) +
        "\n Total Cases: " + str(data[3]['cases']) + "\n Cases Today: " +
        str(data[3]['todayCases']) + "\n Total Deaths: " +
        str(data[3]['deaths']) + "\n Deaths Today: " +
        str(data[3]['todayDeaths']) + "\n Recovered: " +
        str(data[3]['recovered']) + "\n\n \u0033 " + str(data[2]['country']) +
        " " + flag.flag(str(data[2]['countryInfo']['iso2'])) +
        "\n Total Cases: " + str(data[2]['cases']) + "\n Cases Today: " +
        str(data[2]['todayCases']) + "\n Total Deaths: " +
        str(data[2]['deaths']) + "\n Deaths Today: " +
        str(data[2]['todayDeaths']) + "\n Recovered: " +
        str(data[2]['recovered']) + "\n\n \u0034 " + str(data[1]['country']) +
        " " + flag.flag(str(data[1]['countryInfo']['iso2'])) +
        "\n Total Cases: " + str(data[1]['cases']) + "\n Cases Today: " +
        str(data[1]['todayCases']) + "\n Total Deaths: " +
        str(data[1]['deaths']) + "\n Deaths Today: " +
        str(data[1]['todayDeaths']) + "\n Recovered: " +
        str(data[1]['recovered']) + "\n\n \u0035 " + str(data[0]['country']) +
        " " + flag.flag(str(data[0]['countryInfo']['iso2'])) +
        "\n Total Cases: " + str(data[0]['cases']) + "\n Cases Today: " +
        str(data[0]['todayCases']) + "\n Total Deaths: " +
        str(data[0]['deaths']) + "\n Deaths Today: " +
        str(data[0]['todayDeaths']) + "\n Recovered: " +
        str(data[0]['recovered']),
        reply_markup=reply_markup)
    return FIRST

@send_typing_action
def mycountry(update, context):
    """Shows India COVID-19 Stats"""
    query = update.callback_query
    bot = context.bot

    if query != None:
        bot.edit_message_text(chat_id=update.effective_chat.id,
                              message_id=query.message.message_id,
                              text=query.message.text)

    keyboard = [[
        InlineKeyboardButton("Show Hospital Data \U0001F469", #\U000200D \U0002695
                             callback_data='showhospitaldata')],
        [InlineKeyboardButton("Return to Previous Menu \U0001F519",
                             callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    data = getstats('india')
    bot.send_message(
        chat_id=update.effective_chat.id,
        text= flag.flag('IN') + " India COVID-19 Stats " + flag.flag('IN') + "\n\n" +
        "Total Cases: " + str(data['cases']) +
        "\n Cases Today: " + str(data['todayCases']) +
        "\n Total Deaths: " + str(data['deaths']) +
        "\n Deaths Today: " + str(data['todayDeaths']) +
        "\n Recovered: " + str(data['recovered']),
        reply_markup=reply_markup)
    return 'mycountry'

def showhospitaldata(update, context):
    """Shows India COVID-19 Stats"""
    query = update.callback_query
    bot = context.bot
    user = update.effective_message.from_user
    user_location = update.effective_message.location
    if user_location == None:
        location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
        custom_keyboard = [[ location_keyboard]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=update.effective_chat.id, text="Would you mind sharing your location with me?", reply_markup=reply_markup)
        return 'mycountry'
    else:
        result = rg.search((user_location.latitude, user_location.longitude))
        print(result[0]['admin1'])
        r = requests.get('https://api.rootnet.in/covid19-in/stats/hospitals')
        data = r.json()
        res = next((sub for sub in data['data']['regional'] if sub['state'] == result[0]['admin1']), None)
        bot.send_message(
        chat_id=update.effective_chat.id,
        text= "\U0001F3E5 " + result[0]['admin1'] + " Hospital Stats \U0001F3E5\n\n" +
        "Rural Hospitals: " + str(res['ruralHospitals']) +
        "\n Rural Beds: " + str(res['ruralBeds']) +
        "\n Urban Hospitals: " + str(res['urbanHospitals']) +
        "\n Urban Beds: " + str(res['urbanBeds']) +
        "\n Total Hospitals: " + str(res['totalHospitals']) +
        "\n Total Beds: " + str(res['totalBeds']))
        FIRST = start(update, context)
        return FIRST

def news(update, context):
    query = update.callback_query
    bot = context.bot
    if query != None:
        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="Done")
    bot.send_message(
        chat_id=update.effective_chat.id,
        text="\U0001F4F0 Top 3 Headlines Around the World \U0001F4F0")
    r = requests.get(
        'http://newsapi.org/v2/top-headlines?country=in&q=coronavirus&sources=google-news&apiKey=c2e7ef1989004dfa8be6a78dacd148b5'
    )
    data = r.json()
    data = data['articles']
    bot.send_photo(chat_id=update.effective_chat.id,
                   photo=data[0]['urlToImage'],
                   caption=data[0]['title'] + "\n\n" + data[0]['description'] +
                   "\n\nRead More: " + data[0]['url'])
    bot.send_photo(chat_id=update.effective_chat.id,
                   photo=data[1]['urlToImage'],
                   caption=data[1]['title'] + "\n\n" + data[1]['description'] +
                   "\n\nRead More: " + data[1]['url'])
    bot.send_photo(chat_id=update.effective_chat.id,
                   photo=data[2]['urlToImage'],
                   caption=data[2]['title'] + "\n\n" + data[2]['description'] +
                   "\n\nRead More: " + data[2]['url'])
    FIRST = start(update, context)
    return FIRST

def helpline(update, context):
    query = update.callback_query
    bot = context.bot
    user = update.effective_message.from_user
    user_location = update.effective_message.location
    if user_location == None:
        location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
        custom_keyboard = [[ location_keyboard]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=update.effective_chat.id, text="Would you mind sharing your location with me?", reply_markup=reply_markup)
    else:
        result = rg.search((user_location.latitude, user_location.longitude))
        print(result[0]['admin1'])
        r = requests.get('https://api.rootnet.in/covid19-in/contacts')
        data = r.json()
        res = next((sub for sub in data['data']['contacts']['regional'] if sub['loc'] == result[0]['admin1']), None)
        bot.send_message(chat_id = update.effective_chat.id,
                         text = "\U0001F4F2 COVID-19 Helpline Contacts \U0001F4F2\n\n" +
                         res['loc'] + " State Number - " + res['number'] + "\n" +
                         "National Number - " + data['data']['contacts']['primary']['number'] + "\n" +
                         "Toll Free Number - " + data['data']['contacts']['primary']['number-tollfree'] + "\n" +
                         "Email - " + data['data']['contacts']['primary']['email'] + "\n" +
                         "Twitter - " + data['data']['contacts']['primary']['twitter'] + "\n" +
                         "Facebook - " + data['data']['contacts']['primary']['facebook'] + "\n")
        FIRST = start(update, context)
        return FIRST

def newsdaily(context):
    bot = context.bot
    bot.send_message(
        chat_id=context.job.context,
        text="\U0001F4F0 Top 3 Headlines Around the World \U0001F4F0")
    r = requests.get(
        'http://newsapi.org/v2/top-headlines?country=in&q=coronavirus&sources=google-news&apiKey=c2e7ef1989004dfa8be6a78dacd148b5'
    )
    data = r.json()
    data = data['articles']
    bot.send_photo(chat_id=context.job.context,
                   photo=data[0]['urlToImage'],
                   caption=data[0]['title'] + "\n\n" + data[0]['description'] +
                   "\n\nRead More: " + data[0]['url'])
    bot.send_photo(chat_id=context.job.context,
                   photo=data[1]['urlToImage'],
                   caption=data[1]['title'] + "\n\n" + data[1]['description'] +
                   "\n\nRead More: " + data[1]['url'])
    bot.send_photo(chat_id=context.job.context,
                   photo=data[2]['urlToImage'],
                   caption=data[2]['title'] + "\n\n" + data[2]['description'] +
                   "\n\nRead More: " + data[2]['url'])
    
def daily_job(update, context):
    """ Running on Mon, Tue, Wed, Thu, Fri = tuple(range(5)) """
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text='Setting a daily notifications!')
    t = time(9, 56, 00, 000000)
    context.job_queue.run_repeating(newsdaily, 10)

    
def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("900431564:AAG8NhNfSV1c1kWOgSw_FNgb-xhYjBjMIZU",
                      use_context=True)

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)],
        states={
            FIRST: [
                MessageHandler(Filters.location, helpline),
                CallbackQueryHandler(selfdiagnosis, pattern='^' + 'selfdiagnosis' + '$'),
                CallbackQueryHandler(helpline, pattern='^' + 'helpline' + '$'),
                CallbackQueryHandler(updates, pattern='^' + 'updates' + '$'),
                CallbackQueryHandler(start, pattern='^' + 'return' + '$'),
                CallbackQueryHandler(worst5, pattern='^' + 'worst5' + '$'),
                CallbackQueryHandler(least5, pattern='^' + 'least5' + '$'),
                CallbackQueryHandler(mycountry, pattern='^' + 'mycountry' + '$'),
                CallbackQueryHandler(stats, pattern='^' + 'stats' + '$'),
            ],
            'Update1': [
                CallbackQueryHandler(news, pattern='^' + 'latestnews' + '$'),
                CallbackQueryHandler(stats, pattern='^' + 'stats' + '$'),
                CallbackQueryHandler(start, pattern='^' + 'return' + '$')
            ],
            'st_1': [
                CallbackQueryHandler(worst5, pattern='^' + 'worst5' + '$'),
                CallbackQueryHandler(least5, pattern='^' + 'least5' + '$'),
                CallbackQueryHandler(mycountry, pattern='^' + 'mycountry' + '$'),
                CallbackQueryHandler(start, pattern='^' + 'return' + '$')
            ],
            'sd_1': [
                CallbackQueryHandler(gender, pattern='^' + 'gender1' + '$'),
                CallbackQueryHandler(gender, pattern='^' + 'gender2' + '$'),
                CallbackQueryHandler(gender, pattern='^' + 'gender3' + '$'),
                CallbackQueryHandler(gender, pattern='^' + 'gender4' + '$'),
                CallbackQueryHandler(gender, pattern='^' + 'gender5' + '$'),
                CallbackQueryHandler(gender, pattern='^' + 'gender6' + '$'),
                CallbackQueryHandler(gender, pattern='^' + 'gender7' + '$'),
                CallbackQueryHandler(decider, pattern='^' + 'decider' + '$'),
                CallbackQueryHandler(symptomfever,
                                     pattern='^' + 'symptomfever0' + '$'),
                CallbackQueryHandler(symptomfever,
                                     pattern='^' + 'symptomfever1' + '$'),
                CallbackQueryHandler(symptombreath,
                                     pattern='^' + 'symptombreath1' + '$'),
                CallbackQueryHandler(symptombreath,
                                     pattern='^' + 'symptombreath0' + '$'),
                CallbackQueryHandler(symptomcough,
                                     pattern='^' + 'symptomcough1' + '$'),
                CallbackQueryHandler(symptomcough,
                                     pattern='^' + 'symptomcough0' + '$'),
                CallbackQueryHandler(diagnosis,
                                     pattern='^' + 'diagnosis1' + '$'),
                CallbackQueryHandler(diagnosis,
                                     pattern='^' + 'diagnosis0' + '$'),
            ],
            'mycountry' : [MessageHandler(Filters.location, showhospitaldata),
                           CallbackQueryHandler(start, pattern='^' + 'return' + '$'),
                           CallbackQueryHandler(showhospitaldata, pattern='^' + 'showhospitaldata' + '$')]
        },
        fallbacks=[CommandHandler('start', start)])

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('notify', daily_job))
    updater.dispatcher.add_handler(CommandHandler('news', news))
    updater.dispatcher.add_handler(CommandHandler('stats', stats))
    updater.dispatcher.add_handler(CommandHandler('worst5', worst5))
    updater.dispatcher.add_handler(CommandHandler('least5', least5))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
