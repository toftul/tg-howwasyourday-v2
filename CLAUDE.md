# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot that tracks users' mood scores and emotions over time. Users rate their mood (-10 to +10), select emotions from Russell's circumplex model of affect (valence/arousal), and the data is stored in InfluxDB. The bot periodically reminds users to log their mood.

## Running

**With Poetry (development):**
```shell
# Install poetry-dotenv-plugin for .env support
poetry self add poetry-dotenv-plugin
# Create howwasyourdaybot/.env with required env vars (see README.md)
poetry run python howwasyourdaybot/bot.py
```

**With Podman (production):**
```shell
podman build -t howwasyourday-bot .
# Run with env vars (see README.md for full list)
```

**Export requirements for container builds:**
```shell
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Required Environment Variables

`TELEGRAM_BOT_TOKEN`, `ALLOWED_CHAT_IDS` (comma-separated), `LILYA_ID`, `INFLUXDB_TOKEN`, `INFLUXDB_URL`, `INFLUXDB_ORG`, `INFLUXDB_BUCKET`, `DUE_MINIMAL_H`, `DUE_MAXIMAL_H`, `NAMES_FOR_LILYA_JSON`, `DEFAULT_LANG` (optional, defaults to "en").

## Architecture

All source code is in `howwasyourdaybot/`. The bot entry point is `bot.py`.

- **bot.py** — Main bot logic. Uses `python-telegram-bot` v20 with `ConversationHandler` for three conversation flows:
  1. Mood tracking: `/start` or mood score entry → emotion selection → "Done" → writes to InfluxDB
  2. Settings: `/settings` → reminder interval, toggle reminders, language
  3. Stats: `/get_stats` → choose time range → generates plot from InfluxDB data

  Also manages reminder jobs via `job_queue` (APScheduler). After each mood entry, a randomized reminder is scheduled within the user's configured time window.

- **config.py** — Loads all configuration from environment variables.

- **emotions.py** — Emotion definitions with valence/arousal coordinates from Russell (1980). Each emotion is a dict with `valence` and `arousal` float values in [-1, 1].

- **phrases_multilang.py** — All bot text strings, emotion translations, and plot labels in English and Russian. The `bot_phases_dict` is the central translation dictionary. Contains `translated_emotion_to_key()` to reverse-lookup emotion keys from translated names.

- **filters.py** — Custom `MessageFilter` subclasses: `FilterAllowedChats` (restricts by chat ID), `FilterEmotions` (validates emotion names), `FilterIsDigit` (checks if message is a number).

- **get_stats_plots.py** — Queries InfluxDB and generates a multi-panel matplotlib stats plot (Russell map with confidence ellipses, mood score time series, mood histogram, valence/arousal time series).

- **plot_emotions.py** — Generates a static scatter plot of the Russell emotion map.

- **JSONPersistence.py** — Custom JSON-based persistence for `python-telegram-bot` (currently unused; `PicklePersistence` is used instead in `bot.py`).

## Key Patterns

- Multilingual support (en/ru): user language stored in `context.user_data["language"]`, defaulting to `DEFAULT_LANG`. All user-facing strings go through `bot_phases_dict` with `[lang]` lookup.
- InfluxDB writes use two measurements: `emotion_measurement` (mood_score, mean_valence, mean_arousal, emotions) and `selected_emotions` (individual emotion tags).
- Imports within `howwasyourdaybot/` use bare module names (not package-relative), so the working directory must be `howwasyourdaybot/` when running directly.
