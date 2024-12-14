#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from telegram import ForceReply, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

from utils import USER_NAMES, read_json, DATA_PATH, shuffle_users, save_json

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Start the conversation, display any stored data and ask user for input."""
    if context.user_data:
        reply_text = (
            'Вы уже выбрали подарок идите нахуй'
        )
        await update.message.reply_text(reply_text)
    else:
        reply_text = (
            "Привет! Сука, выбери свой подарок:"
        )
        await update.message.reply_text(reply_text)


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    user = update.effective_user
    data = read_json(DATA_PATH)
    if 'gift' in data[user.username]:
        if not all('gift' in data[user] for user in USER_NAMES):
            await update.message.reply_text('Не Все подарки выбраны')
        else:
            recipient = data[user.username]['recipient']
            gift = data[recipient]['gift']
            await update.message.reply_text(f'Ваш хуй: @{recipient}; подарок: {gift}')

    else:
        reply_text = (
            "Сначала нажми /start"
        )
        await update.message.reply_text(reply_text)


async def handle_gift_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    user = update.effective_user
    data = read_json(DATA_PATH)
    if 'gift' in data[user.username]:
        await update.message.reply_text('Вы уже выбрали подарок')
    else:
        data[user.username]['gift'] = update.message.text
        save_json(data, DATA_PATH)
        await update.message.reply_text(f'Вы выбрали подарок: {update.message.text}')


async def handle_smoking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    reply_text = 'Чтобы посмотреть своего хуя, нажми /show'
    await update.message.reply_text(reply_text)


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text('Фоллбек')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    load_dotenv()
    token = os.getenv('TOKEN')
    shuffle_users()
    application = Application.builder().token(token).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=handle_gift_choosing)

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("show", show_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()