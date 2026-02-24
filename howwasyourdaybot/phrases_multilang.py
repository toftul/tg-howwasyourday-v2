from telegram.constants import ParseMode

# to send number via callback functionality
index_to_words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
word_to_index = {word: index for index, word in enumerate(index_to_words)}


# range_start, range_stop
stats_time_ranges = {
    "zero": {
        "range_start": "-7d",
        "range_stop": "now()",
        "label": {
            "en": "last week",
            "ru": "последняя неделя",
            "parse_mode": None,
        },
    },
    "one": {
        "range_start": "-14d",
        "range_stop": "-7d",
        "label": {
            "en": "previous week",
            "ru": "прошлая неделя",
            "parse_mode": None,
        },
    },
    "two": {
        "range_start": "-14d",
        "range_stop": "now()",
        "label": {
            "en": "last 2 weeks",
            "ru": "последние 2 недели",
            "parse_mode": None,
        },
    },
    "three": {
        "range_start": "-28d",
        "range_stop": "-14d",
        "label": {
            "en": "previous 2 weeks",
            "ru": "предыдущие 2 недели",
            "parse_mode": None,
        },
    },
    "four": {
        "range_start": "-28d",
        "range_stop": "now()",
        "label": {
            "en": "last month",
            "ru": "последний месяц",
            "parse_mode": None,
        },
    },
    "five": {
        "range_start": "-60d",
        "range_stop": "-30d",
        "label": {
            "en": "previous month",
            "ru": "прошлый месяц",
            "parse_mode": None,
        },
    },
    "six": {
        "range_start": "-10y",
        "range_stop": "now()",
        "label": {
            "en": "all time",
            "ru": "за всё время",
            "parse_mode": None,
        },
    },
}



range_due_options_in_hours = [
    [2, 4],
    [3, 6],
    [5, 8],
    [8, 12]
]

bot_phases_dict = {
    "dont_know_emotion": {
        "en": "I don't recognize this emotion. Anything else?",
        "ru": "Я такой эмоции не знаю. Может что-нибудь ещё?",
        "parse_mode": None,
    },
    "generating_stats_fail": {
        "en": "Generating plot for you... Ups! Something went wrong :(",
        "ru": "Строю график... Упс! Что-то пошло не так :(",
        "parse_mode": None,
    },
    "generating_stats": {
        "en": "Generating plot for you...",
        "ru": "Строю график...",
        "parse_mode": None,
    },
    "choose_stats_range": {
        "en": "Choose time range to gather and analyse the statistics",
        "ru": "Выбери интервал за который собрать статистику",
        "parse_mode": None,
    },
    "language_name_ru": {
        "en": "Russian (Русский)",
        "ru": "Русский",
        "parse_mode": None,
    },
    "language_name_en": {
        "en": "English",
        "ru": "Английский",
        "parse_mode": None,
    },
    "change_language": {
        "en": "Choose language",
        "ru": "Выбери язык",
        "parse_mode": None,
    },
    "start_hello": {
        "en": "Hi! Glad to see you! I will help you to track your emotions. Write /help for more.",
        "ru": "Привет! Рад тебя видеть! Я буду тебе помогать следить за своими эмоциями. Напиши /help, чтобы узнать больше.",
        "parse_mode": None,
    },
    "back": {
        "en": "Back",
        "ru": "Назад",
        "parse_mode": None,
    },
    "change_due_message": {
        "en": "Choose reminder due window from the ranges below",
        "ru": "Выбери диапазон времени в течение которого я буду тебе напоминать",
        "parse_mode": None,
    },
    "range_due": {
        "en": "{due_min:.0f} - {due_max:.0f} h",
        "ru": "{due_min:.0f} - {due_max:.0f} ч",
        "parse_mode": None,
    },
    "reminders_are_set": {
        "en": "Reminder window is set to {due_min:.0f} - {due_max:.0f} h",
        "ru": "Окно напоминаний теперь {due_min:.0f} - {due_max:.0f} ч",
        "parse_mode": None,
    },
    "cancel": {
        "en": "Cancel",
        "ru": "Отмена",
        "parse_mode": None,
    },
    "map_caption": {
        "en": "Map of emotions based on the [\(Russel, 1980\)](https://doi.org/10.1037/h0077714)\.",
        "ru": "Карта эмоций основанная на работе [\(Russel, 1980\)](https://doi.org/10.1037/h0077714)\.",
        "parse_mode": ParseMode.MARKDOWN_V2,
    },
    "okay": {
        "en": "Okay!",
        "ru": "Хорошо!",
        "parse_mode": None,
    },
    "canceled": {
        "en": "Okay. Canceled!",
        "ru": "Ок! Отменил.",
        "parse_mode": None,
    },
    "help_text": {
        "en": """
*How Was Your Day Bot*

This bot helps you in tracking your mood score and emotions\. Emotional measurements are based on Russell's arousal\-valence [theory](https://doi.org/10.1037/h0077714) from 1980\. The bot prompts you to:

\- Provide your mood score on a scale from \-10 to \+10\.
\- Share your current emotional state\. Feel free to pick as many emotions as you are feeling at the moment\.

The bot will ask you again 3\-8 hours later, and you can customize the reminder window\.

*Commands*

\- /get\_stats \- get statistics
\- /settings \- bot settings
\- /show\_russell\_map \- show Russell map of emotions
\- /feedback \- send feedback to the admin
\- /help \- show this message
\- /cancel \- cancel current operation, could help if bot does not respond

Created by Ivan Toftul @toftl
        """,
        "ru": """
*How Was Your Day Bot*

Этот бот поможет отслеживать уровень твоего настроения и какие эмоции ты испытываешь\. Измерения эмоций основаны на теории аффективных состояний Рассела по ароусал\-валентности [теории](https://doi.org/10.1037/h0077714) 1980 года\. Бот предложит тебе:

\- Оценить своё настроение по шкале от \-10 до \+10\.
\- Поделиться текущим эмоциональным состоянием\. Ты можешь выбрать столько эмоций, сколько чувствуешь в данный момент\.

Бот повторно спросит тебя через 3\-8 часов\. Можно настроить время напоминалок\.

*Команды*

\- /get\_stats \- получить статистику
\- /settings \- настройки бота
\- /show\_russell\_map \- показать карту эмоций по Расселу
\- /feedback \- отправить отзыв администратору
\- /help \- показать это сообщение
\- /cancel \- отмеить текущее действие, иногда помогает, если бот завис

Автор Иван Тофтул @toftl
        """,
        "parse_mode": ParseMode.MARKDOWN_V2,
    },
    "got_your_mood_score": {
        "en": "Thanks, I got your mood score. What's your emotion?",
        "ru": "Спасибо, понял. Какие эмоции сейчас ощущаешь?",
        "parse_mode": None,
    },
    "anything_else": {
        "en": "Anything else?",
        "ru": "Что-нибудь ещё?",
        "parse_mode": None,
    },
    "done_text": {
        "en": "Writing down your mood score and emotions. I will ask you again later. See ya!",
        "ru": "Спасибо, я записал. Я ещё спрошу как ты потом. Пока!",
        "parse_mode": None,
    },
    "done_text_no_reminders": {
        "en": "Writing down your mood score and emotions. Keep in touch. See ya!",
        "ru": "Спасибо, я записал. Не забывай меня. Пока!",
        "parse_mode": None,
    },
    "done": {
        "en": "Done",
        "ru": "Это всё",
        "parse_mode": None,
    },
    "reminders_due": {
        "en": "Reminders due",
        "ru": "Интервал напоминалок",
        "parse_mode": None,
    },
    "on": {
        "en": "Turn on",
        "ru": "Включить",
        "parse_mode": None,
    },
    "off": {
        "en": "Turn off",
        "ru": "Выключить",
        "parse_mode": None,
    },
    "toggle_reminders": {
        "en": "Turn on/off reminders",
        "ru": "ВКЛ или ВЫКЛ напоминания",
        "parse_mode": None,
    },
    "change_language": {
        "en": "Language (язык)",
        "ru": "Язык (language)",
        "parse_mode": None,
    },
    "choose_settings": {
        "en": "Choose settings",
        "ru": "Выбери настройку",
        "parse_mode": None,
    },
    "language_is_set_to_en": {
        "en": "Language is set to English",
        "ru": "Язык переключен на английский",
        "parse_mode": None,
    },
    "language_is_set_to_ru": {
        "en": "Language is set to Russian",
        "ru": "Язык переключен на русский",
        "parse_mode": None,
    },
    "reminders_on": {
        "en": "Reminders are turned on",
        "ru": "Напоминалки включены",
        "parse_mode": None,
    },
    "reminders_off": {
        "en": "Reminders are turned off",
        "ru": "Напоминалки выключены",
        "parse_mode": None,
    },
    "reminders_list": {
        "en": ["а?", "wasup?", "sup?", "How are you?", "It's been a while! I miss you. How are you?", "Whats up?"],
        "ru": ["а?", "ну че как там?", "sup?", "Как ты?", "Как делишки?", "Давно не было от тебя вестей, я соскучился!"],
        "parse_mode": None,
    },
    "toggle_weekly_summary": {
        "en": "Weekly summary",
        "ru": "Еженедельный отчёт",
        "parse_mode": None,
    },
    "weekly_summary_on": {
        "en": "Weekly summary is turned on",
        "ru": "Еженедельный отчёт включен",
        "parse_mode": None,
    },
    "weekly_summary_off": {
        "en": "Weekly summary is turned off",
        "ru": "Еженедельный отчёт выключен",
        "parse_mode": None,
    },
    "weekly_summary_text": {
        "en": "Your week in review:\n\nAverage mood: {avg_mood:.1f}\nEntries: {count}\nTop emotions: {top_emotions}\nTrend: {trend}",
        "ru": "Твоя неделя:\n\nСреднее настроение: {avg_mood:.1f}\nЗаписей: {count}\nЧастые эмоции: {top_emotions}\nТренд: {trend}",
        "parse_mode": None,
    },
    "weekly_summary_no_data": {
        "en": "No data for this week",
        "ru": "Нет данных за эту неделю",
        "parse_mode": None,
    },
    "trend_improving": {
        "en": "improving ↗",
        "ru": "улучшение ↗",
        "parse_mode": None,
    },
    "trend_declining": {
        "en": "declining ↘",
        "ru": "ухудшение ↘",
        "parse_mode": None,
    },
    "trend_stable": {
        "en": "stable →",
        "ru": "стабильно →",
        "parse_mode": None,
    },
    "feedback_sent": {
        "en": "Thanks! Your feedback has been sent.",
        "ru": "Спасибо! Сообщение отправлено.",
        "parse_mode": None,
    },
    "feedback_empty": {
        "en": "Please add your message after /feedback, e.g. /feedback Great bot!",
        "ru": "Напиши сообщение после /feedback, например /feedback Отличный бот!",
        "parse_mode": None,
    },
    "admin_not_authorized": {
        "en": "This command is only for the admin.",
        "ru": "Эта команда только для администратора.",
        "parse_mode": None,
    },
    "all_reminders_on": {
        "en": "All reminders: ON",
        "ru": "Все уведомления: ВКЛ",
        "parse_mode": None,
    },
    "all_reminders_off": {
        "en": "All reminders: OFF",
        "ru": "Все уведомления: ВЫКЛ",
        "parse_mode": None,
    },
    "mood_reminders_on": {
        "en": "Mood reminders: ON",
        "ru": "Напоминания: ВКЛ",
        "parse_mode": None,
    },
    "mood_reminders_off": {
        "en": "Mood reminders: OFF",
        "ru": "Напоминания: ВЫКЛ",
        "parse_mode": None,
    },
    "weekly_summary_on_label": {
        "en": "Weekly summary: ON",
        "ru": "Еженедельный отчёт: ВКЛ",
        "parse_mode": None,
    },
    "weekly_summary_off_label": {
        "en": "Weekly summary: OFF",
        "ru": "Еженедельный отчёт: ВЫКЛ",
        "parse_mode": None,
    },
    "language_label": {
        "en": "Language: English",
        "ru": "Язык: Русский",
        "parse_mode": None,
    },
}

plot_words = {
    "valence": {
        "en": "Valence",
        "ru": "Знак",
    },
    "arousal": {
        "en": "Arousal",
        "ru": "Интенсивность",
    },
    "emotions": {
        "en": "Emotions",
        "ru": "Эмоции",
    },
    "negative": {
        "en": "Negative",
        "ru": "Отрицательно",
    },
    "neutral": {
        "en": "Neutral",
        "ru": "Нейтрально",
    },
    "positive": {
        "en": "Positive",
        "ru": "Позитивно",
    },
    "weak": {
        "en": "Weak",
        "ru": "Слабо",
    },
    "strong": {
        "en": "Strong",
        "ru": "Сильно",
    },
    "mood_score": {
        "en": "Mood score",
        "ru": "Оценка настроения",
    },
    "requested": {
        "en": "Requested",
        "ru": "Недавно",
    },
    "all_time": {
        "en": "All time",
        "ru": "За всё время",
    },
}


emotions_translations = {
    "Neutral": {
        "en": "Neutral",
        "ru": "Нейтральный",
    },
    "Astonished": {
        "en": "Astonished",
        "ru": "Удивленный",
    },
    "Excited": {
        "en": "Excited",
        "ru": "Взволнованный, возбужденный",
    },
    "Happy": {
        "en": "Happy",
        "ru": "Счастливый",
    },
    "Pleased": {
        "en": "Pleased",
        "ru": "Довольный",
    },
    "Relaxed": {
        "en": "Relaxed",
        "ru": "Расслабленный",
    },
    "Peaceful": {
        "en": "Peaceful",
        "ru": "Умировотворенный",
    },
    "Calm": {
        "en": "Calm",
        "ru": "Спокойный",
    },
    "Sleepy": {
        "en": "Sleepy",
        "ru": "Сонный",
    },
    "Tired": {
        "en": "Tired",
        "ru": "Усталый",
    },
    "Bored": {
        "en": "Bored",
        "ru": "Скучающий",
    },
    "Sad": {
        "en": "Sad",
        "ru": "Грустный",
    },
    "Miserable": {
        "en": "Miserable",
        "ru": "Несчастный",
    },
    "Nervous": {
        "en": "Nervous",
        "ru": "Нервозный",
    },
    "Angry": {
        "en": "Angry",
        "ru": "Злой",
    },
    "Frustrated": {
        "en": "Frustrated",
        "ru": "Разочарованный",
    },
    "Annoyed": {
        "en": "Annoyed",
        "ru": "Раздраженный",
    },
    "Afraid": {
        "en": "Afraid",
        "ru": "Испуганный",
    },
    "Anxious": {
        "en": "Anxious",
        "ru": "Тревожный",
    },
    "Droopy": {
        "en": "Droopy",
        "ru": "Вялый",
    },
}

def translated_emotion_to_key(translated_emotion, emotions_translations=emotions_translations):
    """
        For a given emotion translation it gives back the original dict key for this emotion
    """
    for emotion_key, translation_dict in emotions_translations.items():
        for language, translation in translation_dict.items():
            if translation == translated_emotion:
                return emotion_key
    return "unknown"

