# basic imports 
import os
import logging
import random
from datetime import datetime

# bot imports
from telegram import (
    Update,
    MenuButtonCommands,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Bot,
    constants
)

from telegram.ext import (
    Application,
    Updater,
    MessageHandler,
    filters,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)

# influxdb imports
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# get env variables
# TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# ALLOWED_CHAT_IDS = os.environ.get("ALLOWED_CHAT_IDS")

from config import (
    TOKEN, 
    ALLOWED_CHAT_IDS, 
    lilya_id,
    namesForLilya,
    remindersList,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
    DUE_MINIMAL_H,
    DUE_MAXIMAL_H,
)

#client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
#write_api = client.write_api(write_options=SYNCHRONOUS)


# keyboard layouts
keyboard_mood_layout = [
    ["0"],
    ["-1", "+1"],
    ["-2", "+2"],
    ["-3", "+3"],
    ["-4", "+4"],
    ["-5", "+5"],
    ["-6", "+6"],
    ["-7", "+7"],
    ["-8", "+8"],
    ["-9", "+9"],
    ["-10", "+10"]
]
keyboard_mood_markup = ReplyKeyboardMarkup(
    keyboard=keyboard_mood_layout,
    resize_keyboard=False,
    one_time_keyboard=False,
)

keyboard_emotion_layout = [
    ["/start"],
    ["Overthinking", "Mindfulness"],
    ["Tired", "Energetic"],
    ["Stressed", "Relaxed"],
    ["Lazy", "Motivated"],
    ["Anxious", "Calm"],
    ["Sad", "Happy"],
    ["Angry", "Peaceful"],
    ["Burn Out", "Engaged"],
]
keyboard_emotion_markup = ReplyKeyboardMarkup(
    keyboard=keyboard_emotion_layout,
    resize_keyboard=False,
    one_time_keyboard=False,
)


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


    await update.message.reply_text(
        text="ho-ho!",
        reply_markup=keyboard_mood_markup
    )


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    reminderText = random.choice(remindersList)
    await context.bot.send_message(
        job.chat_id,
        text=reminderText
    )


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_removed = remove_job_if_exists(str(chat_id), context)

    hour2sec = 60 * 60  # [h -> s]
    due = random.randrange(DUE_MINIMAL_H * hour2sec, DUE_MAXIMAL_H * hour2sec)
    context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

    text = f"Thanks! I'll remember that!\nI will send you a reminder in {DUE_MINIMAL_H}-{DUE_MAXIMAL_H} hours."
    await update.effective_message.reply_text(text)

async def getEmotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    message_text = update.message.text

    if message_text in keyboard_emotion_layout:
        await update.message.reply_text(
            text=f'Thanks, I got your emotion is {message_text}. Anything else?',
            reply_markup=keyboard_emotion_markup
        )
    else: 
        await update.message.reply_text(
            text="I don't recognize this emotion. Anything else?",
            reply_markup=keyboard_emotion_markup
        )

async def getMoodScore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    message_text = update.message.text

    # check if it is a number
    # https://stackoverflow.com/a/23639915/10282471
    #if message_text.replace('.','',1).replace('-','',1).replace('+','',1).isdigit():
    #   1 + 1
    await update.message.reply_text(
        text=f"Thanks, I got your mood score which is {message_text}. What's your emotion?",
        reply_markup=keyboard_emotion_markup
    )


# it does not work, not sure how to run
async def send_startup_messages() -> None:
    bot = Bot(token=TOKEN)
    for user_id in ALLOWED_CHAT_IDS:
        await bot.send_message(
            chat_id=user_id,
            text="Я перезапустился! А как у тебя дела?"
        )


def main() -> None:
    """Run bot."""

    application = Application.builder().token(token=TOKEN).build()

    application.add_handler(CommandHandler(["start", "help"], start))

    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^[+-]?\d+\.?\d*$'), getMoodScore))
    application.add_handler(MessageHandler(filters.TEXT & ~ filters.Regex(r'^[+-]?\d+\.?\d*$'), getEmotions))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
