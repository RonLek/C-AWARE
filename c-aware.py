import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)

def start(update, context):
    keyboard = [[InlineKeyboardButton("Self Diagnosis \U0001F637", callback_data='selfdiagnosis'),
                 InlineKeyboardButton("View Test Centers Near Me \U0001F3E5", callback_data='testcenter')],

                [InlineKeyboardButton("Updates about COVID-19 \U0001F4F0", callback_data='updates')]]

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
    keyboard = [[InlineKeyboardButton("Self Diagnosis \U0001F637", callback_data='selfdiagnosis'),
                 InlineKeyboardButton("View Test Centers Near Me \U0001F3E5", callback_data='testcenter')],

                [InlineKeyboardButton("Updates about COVID-19 \U0001F4F0", callback_data='updates')]]
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
    """Show Update Choices"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Latest News", callback_data='latestnews'),
         InlineKeyboardButton("Stats", callback_data='stats'),
         InlineKeyboardButton("Return to Previous Menu", callback_data='return')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose an Option",
        reply_markup=reply_markup
    )
    return 'Update1'



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
                        CallbackQueryHandler(button, pattern='^' + 'stats' + '$'),
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
