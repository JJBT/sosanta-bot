import logging
import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from constants import CHRISTMAS_TREE_EMOJI, DATA_PATH, GLOWING_STAR_EMOJI, HEART_WITH_RIBBON_EMOJI, PARTY_POOPER_EMOJI, \
    SPARKLES_EMOJI, STAR_EMOJI
from utils import read_json, shuffle_users, save_json

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
            'Вы уже выбрали подарок! Спасибо, что участвуете в этой игре! Если вы хотите посмотреть, кому вы будете дарить подарок, используйте команду /show.'
        )
        await update.message.reply_text(reply_text)
    else:
        reply_text = (
            f'<b>SoSanta Bot приветствует тебя, {user.first_name}!</b> {SPARKLES_EMOJI} С наступающим Новым годом! {SPARKLES_EMOJI}\n\n'
            'Вы участвуете в игре <b>Тайный Санта</b>! Вот как всё работает:\n'
            '- Сейчас Вам нужно выбрать, какой подарок вы хотите получить. Просто напишите его в ответном сообщении. Это можно сделать только ОДИН раз, так что будьте внимательны!\n'
            '- Когда Ваш получатель выберет свой подарок, Вы сможете узнать, кому Вы дарите подарок и что хочет этот человек. Для этого используйте команду /show.\n'
            '- Также Вы можете узнать, сколько времени осталось до Нового Года с помощью команды /countdown.\n\n'
            f'Если у Вас возникнут вопросы или Вы хотите поддержать проект, загляните в наш <a href=\'https://github.com/JJBT/sosanta-bot\'>GitHub</a>. Мы будем рады вашим звёздочкам! {STAR_EMOJI}\n'
            'С наилучшими пожеланиями, команда разработки SoSanta Bot: Джей Джей (Биг) БуТи, Mbappe, Эл\'Кю Райтри \n\n'
            '<b>Теперь напишите в сообщении, какой подарок Вы хотите получить!</b>'
        )
        await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f'User [{user.username}] called /show command')

    data = read_json(DATA_PATH)
    if 'gift' in data[user.username]:
        recipient = data[user.username]['recipient']
        if 'gift' not in data[recipient]:
            await update.message.reply_text(
                f'Ваш получатель @{recipient} ещё не выбрал свой подарок. Подождите немного и попробуйте снова! {GLOWING_STAR_EMOJI}'
            )
        else:
            gift = data[recipient]['gift']
            await update.message.reply_text(
                f'Ваш получатель выбрал свой подарок! {HEART_WITH_RIBBON_EMOJI}\n'
                f'Вы будете дарить подарок @{recipient}. Этот человек в своем пожелании написал: "{gift}".\n\n'
            )
    else:
        reply_text = (
            'Пожалуйста, сначала выберите подарок, написав его в ответном сообщении после команды /start.'
        )
        await update.message.reply_text(reply_text)


async def handle_gift_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f'User [{user.username}] chose gift')

    data = read_json(DATA_PATH)
    if 'gift' in data[user.username]:
        await update.message.reply_text(
            'Вы уже выбрали подарок! Если хотите узнать, кому Вы будете дарить, используйте команду /show.'
        )
    else:
        data[user.username]['gift'] = update.message.text
        save_json(data, DATA_PATH)
        context.user_data['gift_chosen'] = True
        await update.message.reply_text(
            f'Ваш подарок "{update.message.text}" успешно сохранён! {SPARKLES_EMOJI}\n'
            'Теперь вы можете воспользоваться командой /show, чтобы узнать, кому Вы будете дарить подарок.'
        )


async def countdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f'User [{user.username}] called /countdown command')

    if not context.user_data.get('gift_chosen', False):
        await update.message.reply_text(
            f'Пожалуйста, сначала выберите подарок с помощью команды /start. {CHRISTMAS_TREE_EMOJI}'
        )
        return

    now = datetime.now(timezone.utc)
    eastern_european_time = now.astimezone(timezone(timedelta(hours=2)))
    new_year = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=2)))
    time_remaining = new_year - eastern_european_time

    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    await update.message.reply_text(
        f'{SPARKLES_EMOJI} До наступления 2025 года осталось: {days} дней, {hours} часов, {minutes} минут и {seconds} секунд! {SPARKLES_EMOJI}\n\n'
        f'Уже чувствуете дух праздника? {PARTY_POOPER_EMOJI}'
    )


def main():
    load_dotenv()
    token = os.getenv('TOKEN')

    shuffle_users()

    application = Application.builder().token(token).build()

    conv_handler = MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=handle_gift_choosing)

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('show', show_command))
    application.add_handler(CommandHandler('countdown', countdown_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
