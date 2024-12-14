import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from utils import USER_NAMES, read_json, DATA_PATH, shuffle_users, save_json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f'User [{user.username}] called /start command')

    if context.user_data:
        reply_text = (
            'Вы уже выбрали подарок идите нахуй'
        )
        await update.message.reply_text(reply_text)
    else:
        reply_text = (
            'Привет! Сука, выбери свой подарок:'
        )
        await update.message.reply_text(reply_text)


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f'User [{user.username}] called /show command')

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
            'Сначала нажми /start'
        )
        await update.message.reply_text(reply_text)


async def handle_gift_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f'User [{user.username}] chose gift')

    data = read_json(DATA_PATH)
    if 'gift' in data[user.username]:
        await update.message.reply_text('Вы уже выбрали подарок')
    else:
        data[user.username]['gift'] = update.message.text
        save_json(data, DATA_PATH)
        await update.message.reply_text(f'Вы выбрали подарок: {update.message.text}')


def main():
    load_dotenv()
    token = os.getenv('TOKEN')

    shuffle_users()

    application = Application.builder().token(token).build()

    conv_handler = MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=handle_gift_choosing)

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('show', show_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
