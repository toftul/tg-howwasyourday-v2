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
from datetime import datetime, timezone

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
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
    DUE_MINIMAL_H,
    DUE_MAXIMAL_H,
    DEFAULT_LANG
)

from emotions import emotions_list
from plot_emotions import plot_emotions
from get_stats_plots import generate_stats_plot
# translations
from phrases_multilang import (
    bot_phases_dict, 
    emotions_translations, 
    range_due_options_in_hours,
    index_to_words,
    word_to_index,
    stats_time_ranges,
    translated_emotion_to_key
)

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
keyboard_emotion_layout = [["Done"]] + [emotion_keys[i:i+num_columns] for i in range(0, len(emotion_keys), num_columns)]
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

STATE_SETTINGS_CHOOSING, STATE_SETTINGS_DUE, STATE_SETTINGS_TOGGLE_REMINDERS, STATE_SETTINGS_LANGUAGE = range(4)

STATE_STATS_CHOOSING = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    await update.message.reply_text(
        text=bot_phases_dict["start_hello"]["en"] + "\n\n" + bot_phases_dict["start_hello"]["ru"],
        reply_markup=keyboard_mood_markup,
        parse_mode=bot_phases_dict["start_hello"]["parse_mode"]
    )
    return STATE_GET_MOOD_SCORE


def get_emotions_keyboard_markup(lang=DEFAULT_LANG):
    num_columns = 3
    emotion_keys = list(emotions_list.keys())
    translated_emotions = []
    for emotion_key in emotion_keys:
        translated_emotions.append(emotions_translations[emotion_key][lang])

    keyboard_emotion_layout = [[bot_phases_dict["done"][lang]]] + [translated_emotions[i:i+num_columns] for i in range(0, len(translated_emotions), num_columns)]
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
    return keyboard_emotion_markup

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    await update.message.reply_text(
        text=bot_phases_dict["okay"][lang],
        parse_mode=bot_phases_dict["okay"]["parse_mode"]
    )
    return ConversationHandler.END


async def get_stats_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)

    keyboard_range = [
        [InlineKeyboardButton(stats_time_ranges[stats_time_range_key]["label"][lang], callback_data=stats_time_range_key)] for stats_time_range_key in stats_time_ranges.keys()
    ]
    keyboard_range.append(
        [InlineKeyboardButton(bot_phases_dict["cancel"][lang], callback_data="cancel")]
    )
    range_reply_markup = InlineKeyboardMarkup(keyboard_range)

    await update.message.reply_text(
        text=bot_phases_dict["choose_stats_range"][lang],
        reply_markup=range_reply_markup,
        parse_mode=bot_phases_dict["choose_stats_range"]["parse_mode"]
    )
    
    return STATE_STATS_CHOOSING


async def handel_stats_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    query = update.callback_query
    user_choice_callback_data = query.data
    chat_id = update.effective_chat.id

    if user_choice_callback_data in stats_time_ranges.keys():
        try:
            await query.edit_message_text(
                text=bot_phases_dict["generating_stats"][lang],
                parse_mode=bot_phases_dict["generating_stats"]["parse_mode"]
            )
            stats_plot_file = generate_stats_plot(
                chat_id=chat_id,
                range_start=stats_time_ranges[user_choice_callback_data]["range_start"],
                range_stop=stats_time_ranges[user_choice_callback_data]["range_stop"],
                lang=lang
            )
            with open(stats_plot_file, 'rb') as image_file:
                await update.effective_message.reply_photo(
                    photo=image_file,
                    caption=stats_time_ranges[user_choice_callback_data]["label"][lang],
                    parse_mode=stats_time_ranges[user_choice_callback_data]["label"]["parse_mode"]
                )
            return ConversationHandler.END
        except:
            await query.edit_message_text(
                text=bot_phases_dict["generating_stats_fail"][lang],
                parse_mode=bot_phases_dict["generating_stats_fail"]["parse_mode"]
            )
            logging.error("Cannot generate stats plot.")
            return ConversationHandler.END
    elif user_choice_callback_data == "cancel":
        await query.edit_message_text(
            text=bot_phases_dict["canceled"][lang],
            parse_mode=bot_phases_dict["canceled"]["parse_mode"]
        )
        return ConversationHandler.END
    else:
        return ConversationHandler.END


def get_reply_markup_main_settings(lang="en"):
    settings_items_keyboard = [
        [InlineKeyboardButton(bot_phases_dict["reminders_due"][lang], callback_data="reminders_due")],
        [InlineKeyboardButton(bot_phases_dict["toggle_reminders"][lang], callback_data="toggle_reminders")],
        [InlineKeyboardButton(bot_phases_dict["change_language"][lang], callback_data="change_language")],
        [InlineKeyboardButton(bot_phases_dict["cancel"][lang], callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(settings_items_keyboard)
    return reply_markup

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    reply_markup = get_reply_markup_main_settings(lang)

    await update.message.reply_text(
        text=bot_phases_dict["choose_settings"][lang],
        reply_markup=reply_markup,
        parse_mode=bot_phases_dict["choose_settings"]["parse_mode"]
    )

    return STATE_SETTINGS_CHOOSING


async def handle_settings_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    query = update.callback_query
    user_choice_callback_data = query.data

    if user_choice_callback_data == "reminders_due":
        # create due ranges
        reminders_range_options = []
        for due_range in range_due_options_in_hours:
            reminders_range_options.append(
                bot_phases_dict["range_due"][lang].format(due_min=due_range[0], due_max=due_range[1])
            )

        keyboard_range = [
            [InlineKeyboardButton(reminders_range_options[i], callback_data=index_to_words[i])] for i in range(len(range_due_options_in_hours))
        ]
        keyboard_range.append(
            [InlineKeyboardButton(bot_phases_dict["back"][lang], callback_data="back")]
        )
        range_reply_markup = InlineKeyboardMarkup(keyboard_range)

        await query.edit_message_text(
            text=bot_phases_dict["change_due_message"][lang],
            parse_mode=bot_phases_dict["change_due_message"]["parse_mode"],
            reply_markup=range_reply_markup
        )
        return STATE_SETTINGS_DUE

    elif user_choice_callback_data == "toggle_reminders":
        keyboard_toggle_reminders = [
            [InlineKeyboardButton(bot_phases_dict["on"][lang], callback_data="reminders_on")],
            [InlineKeyboardButton(bot_phases_dict["off"][lang], callback_data="reminders_off")],
            [InlineKeyboardButton(bot_phases_dict["back"][lang], callback_data="back")]
        ]
        toggle_reply_markup = InlineKeyboardMarkup(keyboard_toggle_reminders)
        await query.edit_message_text(
            text=bot_phases_dict["toggle_reminders"][lang],
            parse_mode=bot_phases_dict["toggle_reminders"]["parse_mode"],
            reply_markup=toggle_reply_markup
        )
        return STATE_SETTINGS_TOGGLE_REMINDERS

    elif user_choice_callback_data == "change_language":
        keyboard_toggle_reminders = [
            [InlineKeyboardButton(bot_phases_dict["language_name_ru"][lang], callback_data="change_language_to_ru")],
            [InlineKeyboardButton(bot_phases_dict["language_name_en"][lang], callback_data="change_language_to_en")],
            [InlineKeyboardButton(bot_phases_dict["back"][lang], callback_data="back")]
        ]
        toggle_reply_markup = InlineKeyboardMarkup(keyboard_toggle_reminders)
        await query.edit_message_text(
            text=bot_phases_dict["change_language"][lang],
            parse_mode=bot_phases_dict["change_language"]["parse_mode"],
            reply_markup=toggle_reply_markup
        )

        return STATE_SETTINGS_LANGUAGE
    elif user_choice_callback_data == "cancel":
        await query.edit_message_text(
            text=bot_phases_dict["canceled"][lang],
            parse_mode=bot_phases_dict["canceled"]["parse_mode"]
        )
        return ConversationHandler.END
    else:
        return ConversationHandler.END


async def handel_toggle_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    query = update.callback_query
    user_choice_callback_data = query.data

    if user_choice_callback_data == "back":
        lang = context.user_data.get("language", DEFAULT_LANG)
        reply_markup = get_reply_markup_main_settings(lang)

        await query.edit_message_text(
            text=bot_phases_dict["choose_settings"][lang],
            reply_markup=reply_markup,
            parse_mode=bot_phases_dict["choose_settings"]["parse_mode"]
        )
        return STATE_SETTINGS_CHOOSING
    elif user_choice_callback_data == "reminders_on":
        context.user_data["reminders"] = "on"
        await query.edit_message_text(
            text=bot_phases_dict["reminders_on"][lang],
            parse_mode=bot_phases_dict["reminders_on"]["parse_mode"]
        )
        return ConversationHandler.END
    elif user_choice_callback_data == "reminders_off":
        context.user_data["reminders"] = "off"
        await query.edit_message_text(
            text=bot_phases_dict["reminders_off"][lang],
            parse_mode=bot_phases_dict["reminders_off"]["parse_mode"]
        )
        return ConversationHandler.END
    else:
        return ConversationHandler.END


async def handel_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    query = update.callback_query
    user_choice_callback_data = query.data

    if user_choice_callback_data == "back":
        lang = context.user_data.get("language", DEFAULT_LANG)
        reply_markup = get_reply_markup_main_settings(lang)

        await query.edit_message_text(
            text=bot_phases_dict["choose_settings"][lang],
            reply_markup=reply_markup,
            parse_mode=bot_phases_dict["choose_settings"]["parse_mode"]
        )
        return STATE_SETTINGS_CHOOSING
    elif user_choice_callback_data == "change_language_to_ru":
        context.user_data["language"] = "ru"
        await query.edit_message_text(
            text=bot_phases_dict["language_is_set_to_ru"]["ru"],
            parse_mode=bot_phases_dict["language_is_set_to_ru"]["parse_mode"]
        )
        return ConversationHandler.END
    elif user_choice_callback_data == "change_language_to_en":
        context.user_data["language"] = "en"
        await query.edit_message_text(
            text=bot_phases_dict["language_is_set_to_en"]["en"],
            parse_mode=bot_phases_dict["language_is_set_to_en"]["parse_mode"]
        )
        return ConversationHandler.END
    else:
        return ConversationHandler.END


async def handel_due_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    query = update.callback_query
    user_choice_callback_data = query.data

    if user_choice_callback_data == "back":
        lang = context.user_data.get("language", DEFAULT_LANG)
        reply_markup = get_reply_markup_main_settings(lang)

        await query.edit_message_text(
            text=bot_phases_dict["choose_settings"][lang],
            reply_markup=reply_markup,
            parse_mode=bot_phases_dict["choose_settings"]["parse_mode"]
        )
        return STATE_SETTINGS_CHOOSING
    elif user_choice_callback_data in word_to_index.keys():
        selected_range = np.asarray(range_due_options_in_hours[word_to_index[user_choice_callback_data]], dtype=float)

        context.user_data["REMINDER_DUE_MINIMAL_H"] = selected_range.min()
        context.user_data["REMINDER_DUE_MAXIMAL_H"] = selected_range.max()
        
        await query.edit_message_text(
            text=bot_phases_dict["reminders_are_set"][lang].format(due_min=selected_range.min(), due_max=selected_range.max()),
            parse_mode=bot_phases_dict["reminders_are_set"]["parse_mode"]
        )
        return ConversationHandler.END
    else:
        return ConversationHandler.END


async def show_russell_map(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_base_filename = 'emotions'
    lang = context.user_data.get("language", DEFAULT_LANG)
    try:
        image_filename = plot_emotions(base_filename=image_base_filename, lang=lang)
        with open(image_filename, 'rb') as image_file:
            await update.message.reply_photo(
                photo=image_file,
                caption=bot_phases_dict["map_caption"][lang],
                parse_mode=bot_phases_dict["map_caption"]["parse_mode"]
            )
    except:
        logging.error("Cannot create image emotions map.")


async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = context.user_data.get("language", DEFAULT_LANG)
    await update.message.reply_text(
        text=bot_phases_dict["help_text"][lang],
        parse_mode=bot_phases_dict["help_text"]["parse_mode"]
    )


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> int:
    # this does not work
    # lang = context.user_data.get("language", DEFAULT_LANG)
    # so I pass lang via job name
    job = context.job
    job_name = context.job.name 
    # since job_name is always something like
    # 123123_en
    # 123555_ru_extra
    lang = job_name.split('_')[1]
    reminderText = random.choice(bot_phases_dict["reminders_list"][lang])
    await context.bot.send_message(
        job.chat_id,
        text=reminderText,
        reply_markup=keyboard_mood_markup
    )
    return ConversationHandler.END


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
    if context.user_data.get("reminders", "on") == "on":
        lang = context.user_data.get("language", DEFAULT_LANG)
        chat_id = update.effective_chat.id

        job_removed = remove_job_if_exists(str(chat_id) + "_" + lang, context)
        job_removed_extra = remove_job_if_exists(str(chat_id) + "_" + lang + "_extra", context)
        
        hour2sec = 60 * 60  # [h -> s]
        low  = context.user_data.get("REMINDER_DUE_MINIMAL_H", DUE_MINIMAL_H) * hour2sec
        high = context.user_data.get("REMINDER_DUE_MAXIMAL_H", DUE_MAXIMAL_H) * hour2sec
        
        due = np.random.uniform(low=low, high=high)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id) + "_" + lang, data=due)
        # second reminder
        context.job_queue.run_once(alarm, 2*due, chat_id=chat_id, name=str(chat_id) + "_" + lang + "_extra", data=due)


async def unknown_emotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    chat_id = update.effective_chat.id
    message_text = update.message.text
    keyboard_emotion_markup = get_emotions_keyboard_markup(lang=lang)
    await update.message.reply_text(
        text=bot_phases_dict["dont_know_emotion"][lang],
        reply_markup=keyboard_emotion_markup,
        parse_mode=bot_phases_dict["dont_know_emotion"]["parse_mode"]
    )
    return STATE_SELECT_EMOTIONS


async def get_mood_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    chat_id = update.effective_chat.id
    message_text = update.message.text
    mode_score = float(message_text)

    context.chat_data.clear()
    context.chat_data['mood_score'] = mode_score

    keyboard_emotion_markup = get_emotions_keyboard_markup(lang=lang)
    await update.message.reply_text(
        text=bot_phases_dict["got_your_mood_score"][lang],
        reply_markup=keyboard_emotion_markup,
        parse_mode=bot_phases_dict["got_your_mood_score"]["parse_mode"]
    )
    return STATE_SELECT_EMOTIONS


async def get_emotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
    chat_id = update.effective_chat.id
    message_text = translated_emotion_to_key(translated_emotion=update.message.text)

    context.chat_data[message_text] = emotions_list[message_text]

    keyboard_emotion_markup = get_emotions_keyboard_markup(lang=lang)
    
    await update.message.reply_text(
        text=bot_phases_dict["anything_else"][lang],
        reply_markup=keyboard_emotion_markup,
        parse_mode=bot_phases_dict["anything_else"]["parse_mode"]
    )
    return STATE_SELECT_EMOTIONS
    

def calculate_emotion_average(selected_emotions):
    valence_values = np.array([], dtype=float)
    arousal_values = np.array([], dtype=float)

    selected_emotions_keys = []
    for selected_emotion in selected_emotions:
        selected_emotions_keys.append(translated_emotion_to_key(selected_emotion))

    are_emotions_valid = any(emotion in emotions_list.keys() for emotion in selected_emotions_keys)
    if are_emotions_valid:
        for emotion_name in selected_emotions_keys:
            emotion_data = emotions_list.get(emotion_name)
            if emotion_data:
                valence_values = np.append(valence_values, emotion_data["valence"])
                arousal_values = np.append(arousal_values, emotion_data["arousal"])

        mean_valence = np.mean(valence_values)
        mean_arousal = np.mean(arousal_values)
        #print(valence_values)
        #print(arousal_values)
        return mean_valence, mean_arousal
    else:
        return 0.0, 0.0


async def timeout_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto-save mood data when conversation times out."""
    if "mood_score" not in context.chat_data:
        return

    # Default to Neutral if no emotions were selected
    selected_emotions = [k for k in context.chat_data.keys() if k != "mood_score"]
    if not selected_emotions:
        context.chat_data["Neutral"] = emotions_list["Neutral"]

    await done(update, context)


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", DEFAULT_LANG)
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
        .time(datetime.now(timezone.utc))
    )
    
    points = []
    points.append(point)
    for emotion in selected_emotions:
        points.append(
            Point('selected_emotions')
            .tag('user', update.effective_chat.id)
            .tag('emotion', emotion)
            .field('value', 1)
            .time(datetime.now(timezone.utc))
        )

    write_api.write(bucket=INFLUXDB_BUCKET, record=points)
    if context.user_data.get("reminders", "on") == "on":
        done_text = bot_phases_dict["done_text"][lang]
    else:
        done_text = bot_phases_dict["done_text_no_reminders"][lang]

    if chat_id == lilya_id:
        done_text = "Хорошо, " + random.choice(namesForLilya) + "! Я записал. Потом спрошу еще!"
    message = update.effective_message
    if message is not None:
        await message.reply_text(
            text=done_text,
            reply_markup=keyboard_mood_markup
        )
    await set_timer(update=update, context=context)
    return ConversationHandler.END


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
        application.job_queue.run_once(alarm, due, chat_id=int(chat_id), name=str(chat_id)+ "_" + DEFAULT_LANG, data=due)


def get_regex_done_string(bot_phases_dict=bot_phases_dict):
    dressed_values = []
    for value in bot_phases_dict["done"].values():
        if value is not None:
            dressed_values.append("^" + value + "$")

    regex_string = "|".join(dressed_values)
    return regex_string


def main() -> None:
    # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/persistentconversationbot.py
    #persistence = JSONPersistence(file_path="data.json")
    persistence = PicklePersistence(filepath="data_pickle")
    application = Application.builder().token(token=TOKEN).concurrent_updates(False).persistence(persistence).build()
    #application = Application.builder().token(token=TOKEN).persistence(persistence).build()

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

    regex_done_string = get_regex_done_string()
    done_handler = MessageHandler(filters.Regex(regex_done_string), done)
    cancel_handler = CommandHandler("cancel", cancel)

    timeout_handler = MessageHandler(filters.ALL, timeout_done)

    conv_handler = ConversationHandler(
        entry_points=[start_handler, mood_handler],
        states={
            STATE_GET_MOOD_SCORE: [
                mood_handler
            ],
            STATE_SELECT_EMOTIONS: [
                emotion_handler
            ],
            ConversationHandler.TIMEOUT: [
                timeout_handler
            ]
        },
        fallbacks=[done_handler, cancel_handler],
        conversation_timeout=0.9*DUE_MINIMAL_H * 3600,  # auto-end before first possible reminder
    )

    show_settings_handler = CommandHandler("settings", show_settings)

    settings_conv_handler = ConversationHandler(
        entry_points=[show_settings_handler],
        states={
            STATE_SETTINGS_CHOOSING: [
                CallbackQueryHandler(handle_settings_choice)
            ],
            STATE_SETTINGS_TOGGLE_REMINDERS: [
                CallbackQueryHandler(handel_toggle_reminders)
            ],
            STATE_SETTINGS_LANGUAGE: [
                CallbackQueryHandler(handel_language_change)
            ],
            STATE_SETTINGS_DUE: [
                CallbackQueryHandler(handel_due_settings)
            ],
        },
        fallbacks=[cancel_handler]
    )
    
    stats_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("get_stats", get_stats_choosing)],
        states={
            STATE_STATS_CHOOSING: [
                CallbackQueryHandler(handel_stats_choice)
            ]
        },
        fallbacks=[cancel_handler]
    )
    
    application.add_handlers([
        conv_handler,
        settings_conv_handler,
        stats_conv_handler,
        CommandHandler("help", get_help),
        CommandHandler("show_russell_map", show_russell_map),
        CommandHandler("setup_reminder_due_max", setup_reminder_due_max),
        CommandHandler("setup_reminder_due_min", setup_reminder_due_min)
    ])
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
