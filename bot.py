# basic imports 
import os
import logging
import random

# bot imports
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

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


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("ho-ho!")


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

async def getStatisticsAboutTheDay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    message_text = update.message.text

    # check if it is a digit
    if message_text.replace('.','',1).replace('-','',1).isdigit():
        1 + 1



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
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token=TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()
