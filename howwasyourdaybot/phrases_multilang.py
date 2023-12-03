from telegram.constants import ParseMode

bot_phases_dict = {
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
    "help_text": {
        "en": """
*How Was Your Day Bot*

This bot helps you in tracking your mood score and emotions\. Emotional measurements are based on Russell's arousal\-valence [theory](https://doi.org/10.1037/h0077714) from 1980\. The bot prompts you to:

\- Provide your mood score on a scale from \-10 to \+10\.
\- Share your current emotional state\. Feel free to pick as many emotions as you are feeling at the moment\.

The bot will ask you again 3\-8 hours later, and you can customize the reminder window\.

*Commands*

\- /settings \- bot settings
\- /get\_stats \- get statistics
\- /show\_russell\_map \- show Russell map of emotions
\- /help \- show this message

Created by Ivan Toftul @toftl
        """,
        "ru": """
*How Was Your Day Bot*

Этот бот поможет отслеживать уровень твоего настроения и какие эмоции ты испытываешь\. Измерения эмоций основаны на теории аффективных состояний Рассела по ароусал-валентности [теории](https://doi.org/10.1037/h0077714) 1980 года\. Бот предложит тебе:

\- Оценить своё настроение по шкале от \-10 до \+10\.
\- Поделиться текущим эмоциональным состоянием\. Ты можете выбрать столько эмоций, сколько чувствуешь в данный момент\.

Бот повторно спросит тебя через 3\-8 часов\. Можно настроить время напоминалок\.

*Команды*

\- /settings \- настройки бота
\- /get\_stats \- получить статистику
\- /show\_russell\_map \- показать карту эмоций по Расселу
\- /help \- показать это сообщение

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
    "done": {
        "en": "Done",
        "ru": "Это всё",
        "parse_mode": None,
    },
    "name": {
        "en": "",
        "ru": "",
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
    "name": {
        "en": "",
        "ru": "",
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
}