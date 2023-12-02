"""
helpful:
- https://0xacab.org/viperey/telegram-bot-whisper-transcriber/-/blob/no-masters/main.py?ref_type=heads
- https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/persistentconversationbot.py
- https://github.com/python-telegram-bot/python-telegram-bot/wiki/Storing-bot%2C-user-and-chat-related-data
- https://docs.python-telegram-bot.org/en/stable/telegram.ext.conversationhandler.html
- https://docs.python-telegram-bot.org/en/v20.5/telegram.message.html
"""

# basic imports 
import os
import logging
import random
import numpy as np
from icecream import ic
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
    CallbackContext,
    PicklePersistence
)

# persistence
from JSONPersistence import JSONPersistence

# influxdb imports
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

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

from emotions import emotions_list
from plot_emotions import plot_emotions
from filters import FilterAllowedChats, FilterEmotions, FilterIsDigit

client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

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

num_columns = 3
emotion_keys = list(emotions_list.keys())
keyboard_emotion_layout = [["Done", "Show Russel map"]] + [emotion_keys[i:i+num_columns] for i in range(0, len(emotion_keys), num_columns)]
"""
Gives something like
[['Done'],
 ['Astonished', 'Excited', 'Happy'],
 ['Pleased', 'Relaxed', 'Peaceful'],
 ['Calm', 'Sleepy', 'Tired'],
 ['Bored', 'Sad', 'Miserable'],
 ['Nervous', 'Angry', 'Frustrated'],
 ['Annoyed', 'Afraid']]
"""
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


# Consersation 
STATE_GET_MOOD_SCORE, STATE_SELECT_EMOTIONS = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text="ho-ho!",
        reply_markup=keyboard_mood_markup
    )
    return STATE_GET_MOOD_SCORE


async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # send emotions.png
    chat_id = update.effective_chat.id
    image_filename = 'emotions.png'
    try:
        with open('emotions.png', 'rb') as image_file:
            await update.message.reply_photo(
                photo=image_file,
                caption="Based on the (Russel, 1980)"
            )
    except FileNotFoundError:
        # Handle the case where the image file is not found
        logging.info(f"Image {image_filename} is not found. Creating one.")
        # create an image
        plot_emotions()
        with open('emotions.png', 'rb') as image_file:
            await update.message.reply_photo(
                photo=image_file,
                caption="Based on the (Russel, 1980)"
            )

    return STATE_SELECT_EMOTIONS
    


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


async def setup_reminder_due_max(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # set min time if not set to compare
    if context.user_data.get("REMINDER_DUE_MINIMAL_H") is None:
        context.user_data["REMINDER_DUE_MINIMAL_H"] = DUE_MINIMAL_H

    try:
        # args[0] should contain the time
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Must be positive.")
            #return ConversationHandler.END
        elif due < context.user_data["REMINDER_DUE_MINIMAL_H"]:
            await update.effective_message.reply_text(f'Must be not less than minimal value, which is set to {context.user_data["REMINDER_DUE_MINIMAL_H"]} hours.')
            #return ConversationHandler.END
        else:
            context.user_data["REMINDER_DUE_MAXIMAL_H"] = due
            await update.effective_message.reply_text(f'Got it! Maximal reminder due is set to {context.user_data["REMINDER_DUE_MAXIMAL_H"]} hours.')
    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /setup_reminder_due_max <hours>")
        #return ConversationHandler.END


async def setup_reminder_due_min(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # set max time if not set to compare
    if context.user_data.get("REMINDER_DUE_MAXIMAL_H") is None:
        context.user_data["REMINDER_DUE_MAXIMAL_H"] = DUE_MAXIMAL_H

    try:
        # args[0] should contain the time
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Must be positive.")
            #return ConversationHandler.END
        elif due > context.user_data["REMINDER_DUE_MAXIMAL_H"]:
            await update.effective_message.reply_text(f'Must be not more than maximal value, which is set to {context.user_data["REMINDER_DUE_MAXIMAL_H"]} hours.')
        else:
            context.user_data["REMINDER_DUE_MINIMAL_H"] = due
            await update.effective_message.reply_text(f'Got it! Minimal reminder due is set to {context.user_data["REMINDER_DUE_MINIMAL_H"]} hours.')
    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /setup_reminder_due_min <hours>")
        #return ConversationHandler.END


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_removed = remove_job_if_exists(str(chat_id), context)

    hour2sec = 60 * 60  # [h -> s]
    low  = context.user_data.get("REMINDER_DUE_MINIMAL_H", DUE_MINIMAL_H) * hour2sec
    high = context.user_data.get("REMINDER_DUE_MAXIMAL_H", DUE_MAXIMAL_H) * hour2sec
    
    due = np.random.uniform(low=low, high=high)
    context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

    #text = f"Thanks! I'll remember that!\nI will send you a reminder in {DUE_MINIMAL_H}-{DUE_MAXIMAL_H} hours."
    #await update.effective_message.reply_text(text)

async def unknown_emotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    message_text = update.message.text
    await update.message.reply_text(
        text="I don't recognize this emotion. Anything else?",
        reply_markup=keyboard_emotion_markup
    )
    return STATE_SELECT_EMOTIONS


async def get_mood_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    message_text = update.message.text
    mode_score = float(message_text)

    context.chat_data.clear()
    context.chat_data['mood_score'] = mode_score

    await update.message.reply_text(
        text=f"Thanks, I got your mood score which is {message_text}. What's your emotion?",
        reply_markup=keyboard_emotion_markup
    )
    return STATE_SELECT_EMOTIONS


async def get_emotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    message_text = update.message.text

    context.chat_data[message_text] = emotions_list[message_text]

    #await update.message.reply_text(
    #    text=f'Thanks, I got your emotion is {message_text}. Anything else?',
    #    reply_markup=keyboard_emotion_markup
    #)
    await update.message.reply_text(
        text='Anything else?',
        reply_markup=keyboard_emotion_markup
    )
    return STATE_SELECT_EMOTIONS
    

def calculate_emotion_average(selected_emotions):
    valence_values = np.array([], dtype=float)
    arousal_values = np.array([], dtype=float)

    are_emotions_valid = any(emotion in emotions_list.keys() for emotion in selected_emotions)
    if are_emotions_valid:
        for emotion_name in selected_emotions:
            emotion_data = emotions_list.get(emotion_name)
            if emotion_data:
                valence_values = np.append(valence_values, emotion_data["valence"])
                arousal_values = np.append(arousal_values, emotion_data["arousal"])

        mean_valence = np.mean(valence_values)
        mean_arousal = np.mean(arousal_values)
        print(valence_values)
        print(arousal_values)
        return mean_valence, mean_arousal
    else:
        return 0.0, 0.0


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    #message_text = update.message.text

    mood_score = context.chat_data["mood_score"]
    
    # emotion_average function filters out any non-emotion related keys
    selected_emotions = list(context.chat_data.keys())
    selected_emotions.remove("mood_score")
    mean_valence, mean_arousal = calculate_emotion_average(selected_emotions=selected_emotions)
    point = (
        Point('emotion_measurement')
        .tag('user', update.effective_chat.id)
        .field('mood_score', float(mood_score))
        .field('mean_valence', mean_valence)
        .field('mean_arousal', mean_arousal)
        .field('emotions', ', '.join(selected_emotions))
        .time(datetime.utcnow())
    )
    
    points = []
    points.append(point)
    for emotion in selected_emotions:
        points.append(
            Point('selected_emotions')
            .tag('user', update.effective_chat.id)
            .tag('emotion', emotion)
            .field('value', 1)
            .time(datetime.utcnow())
        )

    write_api.write(bucket=INFLUXDB_BUCKET, record=points)
    done_text="Writing down your mood score and emotions. I will ask again you later. See ya!"
    if chat_id == lilya_id:
        done_text = "Хорошо, " + random.choice(namesForLilya) + "! Я записал. Потом спрошу еще!"
    await update.message.reply_text(
        text=done_text,
        reply_markup=keyboard_mood_markup
    )
    await set_timer(update=update, context=context)
    return ConversationHandler.END
    #return STATE_GET_MOOD_SCORE


# to handel bot restarts
def schedule_reminders(application, chat_ids):
    hour2sec = 60 * 60  # [h -> s]
    low  = DUE_MINIMAL_H * hour2sec
    high = DUE_MAXIMAL_H * hour2sec

    for chat_id in chat_ids:
        current_jobs = application.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()

        due = int(np.random.uniform(low=low, high=high))
        application.job_queue.run_once(alarm, due, chat_id=int(chat_id), name=str(chat_id), data=due)


def main() -> None:
    # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/persistentconversationbot.py
    persistence = JSONPersistence(file_path="data.json")
    application = Application.builder().token(token=TOKEN).persistence(persistence).build()

    #application = Application.builder().token(token=TOKEN).build()

    # reset all reminders after restart

    #application.job_queue.run_once(alarm, when=10, chat_id=63688320, name=str(63688320))
    schedule_reminders(application, ALLOWED_CHAT_IDS)

    # setup filters
    filter_allowed_chat_ids = FilterAllowedChats(ALLOWED_CHAT_IDS)
    filter_emotions = FilterEmotions(emotions_list)
    filter_isgidit = FilterIsDigit()

    start_handler = CommandHandler("start", start)
    mood_handler = MessageHandler(
        filters.TEXT & filter_allowed_chat_ids & filter_isgidit,
        get_mood_score
    )
    emotion_handler = MessageHandler(
        filters.TEXT & filter_allowed_chat_ids & filter_emotions,
        get_emotions
    )
    done_handler = MessageHandler(filters.Regex("^Done$"), done)
    show_map_handler = MessageHandler(filters.Regex("^Show Russel map$"), get_help)

    conv_handler = ConversationHandler(
        entry_points=[start_handler, mood_handler],
        states={
            STATE_GET_MOOD_SCORE: [
                mood_handler
            ],
            STATE_SELECT_EMOTIONS: [
                emotion_handler,
                show_map_handler
            ]
        },
        fallbacks=[done_handler],
        #name='emotional_handler',
        #persistent=True
    )

    application.add_handler(conv_handler)

    application.add_handler(
        CommandHandler("setup_reminder_due_max", setup_reminder_due_max)
    )
    application.add_handler(
        CommandHandler("setup_reminder_due_min", setup_reminder_due_min)
    )
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()