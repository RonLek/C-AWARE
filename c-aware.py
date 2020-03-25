import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
import requests
from functools import wraps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)

def start(update, context):
    keyboard = [[InlineKeyboardButton("Self Diagnosis \U0001F637", callback_data='selfdiagnosis')],
                 [InlineKeyboardButton("View Test Centers Near Me \U0001F3E5", callback_data='testcenter')],

                [InlineKeyboardButton("Updates about COVID-19 \u23F3", callback_data='updates')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('What can I do for you?', reply_markup=reply_markup)

    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST

def start_over(update, context):
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # Get Bot from CallbackContext
    bot = context.bot
    keyboard = [[InlineKeyboardButton("Self Diagnosis \U0001F637", callback_data='selfdiagnosis')],
                 [InlineKeyboardButton("View Test Centers Near Me \U0001F3E5", callback_data='testcenter')],

                [InlineKeyboardButton("Updates about COVID-19 \u23F3", callback_data='updates')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="What can I do for you?",
        reply_markup=reply_markup
    )
    return FIRST


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

    query.edit_message_text(text="Selected option: {}".format(query.data))

    return FIRST

def updates(update, context):
    """Shows Update Choices"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Latest News \U0001F4F0", callback_data='latestnews'),
         InlineKeyboardButton("Stats \U0001F4CA", callback_data='stats')],
         [InlineKeyboardButton("Return to Previous Menu \U0001F519", callback_data='return')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose an Option",
        reply_markup=reply_markup
    )
    return 'Update1'

def getstats(param):
    if param == 'all':
        r = requests.get(url = 'https://corona.lmao.ninja/all')
        data = r.json()
    elif param == 'worst5':
        r = requests.get(url = 'https://corona.lmao.ninja/countries?sort=cases')
        data = r.json()
        data = data[:5]
    elif param == 'least5':
        r = requests.get(url = 'https://corona.lmao.ninja/countries?sort=cases')
        data = r.json()
        data = data[-5:]
    return data

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

@send_typing_action
def stats(update, context):
    """Shows Stats"""
    print(update == None)
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Top 5 Worst Hit Countries", callback_data='worst5')],
         [InlineKeyboardButton("Top 5 Least Hit Countries", callback_data='least5')],
        [InlineKeyboardButton("Get Stats for my Country", callback_data='mycountry')],
         [InlineKeyboardButton("Return to Previous Menu \U0001F519", callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    data = getstats('all')
    print(data)
    print(update == False)
    bot.send_message(chat_id=update.effective_chat.id,
        text="\U0001F30E COVID-19 WORLD IMPACT \U0001F30E \n\n \U0001F9A0 Total Cases: " + str(data['cases']) +
        "\n \u26B0 Total Deaths: " + str(data['deaths']) + "\n \U0001F604 Total Recovered: " + str(data['recovered']) + "\n",
        reply_markup=reply_markup
    )
    return 'st_1'

@send_typing_action
def worst5(update, context):
    """Shows Worst 5 Countries Hit by COVID-19"""
    query = update.callback_query
    bot = context.bot
    keyboard = [[InlineKeyboardButton("Return to Previous Menu \U0001F519", callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    data = getstats('worst5')
    bot.send_message(chat_id=update.effective_chat.id,
        text = "\uF3F4 TOP 5 WORST HIT \uF3F4 \n\n  \u0031" + str(data[0]['country']) +
            "\n Total Cases: " + str(data[0]['cases']) +
            "\n Cases Today: " + str(data[0]['todayCases']) +
            "\n Total Deaths: " + str(data[0]['deaths']) +
            "\n Deaths Today: " + str(data[0]['todayDeaths']) +
            "\n Recovered: " + str(data[0]['recovered'])
            + "\n\n \u0032 " + str(data[1]['country']) +
            "\n Total Cases: " + str(data[1]['cases']) +
            "\n Cases Today: " + str(data[1]['todayCases']) +
            "\n Total Deaths: " + str(data[1]['deaths']) +
            "\n Deaths Today: " + str(data[1]['todayDeaths']) +
            "\n Recovered: " + str(data[1]['recovered'])
            + "\n\n \u0033 " + str(data[2]['country']) +
            "\n Total Cases: " + str(data[2]['cases']) +
            "\n Cases Today: " + str(data[2]['todayCases']) +
            "\n Total Deaths: " + str(data[2]['deaths']) +
            "\n Deaths Today: " + str(data[2]['todayDeaths']) +
            "\n Recovered: " + str(data[2]['recovered'])
            + "\n\n \u0034 " + str(data[3]['country']) +
            "\n Total Cases: " + str(data[3]['cases']) +
            "\n Cases Today: " + str(data[3]['todayCases']) +
            "\n Total Deaths: " + str(data[3]['deaths']) +
            "\n Deaths Today: " + str(data[3]['todayDeaths']) +
            "\n Recovered: " + str(data[3]['recovered'])
            + "\n\n \u0035 " + str(data[4]['country']) +
            "\n Total Cases: " + str(data[4]['cases']) +
            "\n Cases Today: " + str(data[4]['todayCases']) +
            "\n Total Deaths: " + str(data[4]['deaths']) +
            "\n Deaths Today: " + str(data[4]['todayDeaths']) +
            "\n Recovered: " + str(data[4]['recovered']),
        reply_markup=reply_markup
    )
    return 'st_1'

@send_typing_action
def least5(update, context):
    """Shows Worst 5 Countries Hit by COVID-19"""
    query = update.callback_query
    bot = context.bot
    keyboard = [[InlineKeyboardButton("Return to Previous Menu \U0001F519", callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    data = getstats('worst5')
    bot.send_message(chat_id=update.effective_chat.id,
        text="\U0001F6A9 TOP 5 LEAST HIT \U0001F6A9 \n\n \u0031" + data[4]['country'] +
            "\n Total Cases: " + str(data[4]['cases']) +
            "\n Cases Today: " + str(data[4]['todayCases']) +
            "\n Total Deaths: " + str(data[4]['deaths']) +
            "\n Deaths Today: " + str(data[4]['todayDeaths']) +
            "\n Recovered: " + str(data[4]['recovered'])
            + "\n\n \u0032 " + str(data[3]['country']) +
            "\n Total Cases: " + str(data[3]['cases']) +
            "\n Cases Today: " + str(data[3]['todayCases']) +
            "\n Total Deaths: " + str(data[3]['deaths']) +
            "\n Deaths Today: " + str(data[3]['todayDeaths']) +
            "\n Recovered: " + str(data[3]['recovered'])
            + "\n\n \u0033 " + str(data[2]['country']) +
            "\n Total Cases: " + str(data[2]['cases']) +
            "\n Cases Today: " + str(data[2]['todayCases']) +
            "\n Total Deaths: " + str(data[2]['deaths']) +
            "\n Deaths Today: " + str(data[2]['todayDeaths']) +
            "\n Recovered: " + str(data[2]['recovered'])
            + "\n\n \u0034 " + str(data[1]['country']) +
            "\n Total Cases: " + str(data[1]['cases']) +
            "\n Cases Today: " + str(data[1]['todayCases']) +
            "\n Total Deaths: " + str(data[1]['deaths']) +
            "\n Deaths Today: " + str(data[1]['todayDeaths']) +
            "\n Recovered: " + str(data[1]['recovered'])
            + "\n\n \u0035 " + str(data[0]['country']) +
            "\n Total Cases: " + str(data[0]['cases']) +
            "\n Cases Today: " + str(data[0]['todayCases']) +
            "\n Total Deaths: " + str(data[0]['deaths']) +
            "\n Deaths Today: " + str(data[0]['todayDeaths']) +
            "\n Recovered: " + str(data[0]['recovered']),reply_markup=reply_markup)
    return 'st_1'


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("900431564:AAG8NhNfSV1c1kWOgSw_FNgb-xhYjBjMIZU", use_context=True)

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(selfdiagnosis, pattern='^' + 'selfdiagnosis' + '$'),
                    CallbackQueryHandler(button, pattern='^' + 'testcenter' + '$'),
                    CallbackQueryHandler(updates, pattern='^' + 'updates' + '$')],
            'Update1': [CallbackQueryHandler(button, pattern='^' + 'latestnews' + '$'),
                        CallbackQueryHandler(stats, pattern='^' + 'stats' + '$'),
                     CallbackQueryHandler(start_over, pattern='^' + 'return' + '$')],
            'st_1' : [CallbackQueryHandler(worst5, pattern='^' + 'worst5' + '$'),
                        CallbackQueryHandler(least5, pattern='^' + 'least5' + '$'),
                      CallbackQueryHandler(button, pattern='^' + 'mycountry' + '$'),
                     CallbackQueryHandler(start_over, pattern='^' + 'return' + '$')]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button)) 
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
