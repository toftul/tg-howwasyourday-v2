# New Bot Plan

## What Changes from v2

- **Remove** mood score (−10…+10 numeric input
- **Keep** emotion selection from Russell's circumplex (valence/arousal)
- **Expand** stats: richer analysis, trends, clustering, time-of-day patterns
- **Prepare** for multi-platform (Telegram now, Discord later)

---

## Option 1 — Simple Monorepo, Single Package

**Best for:** Getting started fast, solo developer, no immediate Discord plans.

### Structure

```
moodbot/
├── pyproject.toml
├── .env
└── src/
    └── moodbot/
        ├── main.py              # entry point
        ├── config.py            # pydantic-settings
        ├── emotions.py          # Russell circumplex data
        ├── i18n.py              # t(key, lang, **kwargs)
        ├── locales/
        │   ├── en.toml
        │   └── ru.toml
        ├── storage/
        │   ├── influx.py        # write/query mood entries
        │   └── settings.py      # aiosqlite user settings
        ├── stats/
        │   ├── queries.py       # InfluxDB query builders
        │   └── plots.py         # matplotlib figures
        ├── scheduler.py         # reminder logic (APScheduler)
        └── platforms/
            └── telegram/
                ├── bot.py       # Application setup
                ├── handlers.py  # command + conversation handlers
                └── keyboards.py # inline/reply keyboard builders
```

### Core Logic Flow

```
User selects emotions
    → adapter normalizes input
    → storage.influx.write_entry(user_id, emotions, timestamp)
    → scheduler.reschedule_reminder(user_id)
    → reply with confirmation

/stats command
    → storage.influx.query(user_id, range)
    → stats.plots.build_figure(data)
    → send image
```

### Data Model

```python
# One InfluxDB measurement per entry
# measurement: "mood_entry"
# tags:    platform, user_id
# fields:  mean_valence, mean_arousal, emotion_list (comma-sep string)
# time:    entry timestamp

# SQLite table: user_settings
# columns: user_id, platform, language, reminder_min_h,
#          reminder_max_h, reminders_on, summary_freq
```

### Pros / Cons

| + | − |
|---|---|
| Least complexity | Adding Discord means editing the same package |
| One `pyproject.toml` | No enforced boundary between core and platform |
| Easy to run and debug | Harder to extract core later |

---

## Option 2 — Monorepo with Workspace Packages ✓ Recommended

**Best for:** Clean boundaries today, Discord or other platforms added later with zero core changes.

### Structure

```
moodbot/
├── pyproject.toml               # uv/Poetry workspace root
├── docker-compose.yml
├── main.py                      # wires adapters, runs asyncio.gather()
└── packages/
    ├── core/                    # NO platform imports — ever
    │   ├── pyproject.toml
    │   └── src/moodbot_core/
    │       ├── models.py        # MoodEntry, UserSettings, NormalizedMessage
    │       ├── emotions.py      # Russell circumplex data + helpers
    │       ├── handlers.py      # record_entry(), get_reminder_delay(), etc.
    │       ├── scheduler.py     # abstract reminder logic
    │       ├── i18n.py          # t(key, lang, **kwargs)
    │       ├── locales/
    │       │   ├── en.toml
    │       │   └── ru.toml
    │       ├── storage/
    │       │   ├── base.py      # Protocol: write_entry, query, get_settings…
    │       │   ├── influx.py    # InfluxDB implementation
    │       │   └── settings.py  # aiosqlite implementation
    │       └── stats/
    │           ├── queries.py   # query builders (return raw data)
    │           └── plots.py     # matplotlib → bytes (no platform dep)
    │
    ├── telegram/                # depends on core via path
    │   ├── pyproject.toml
    │   └── src/moodbot_telegram/
    │       ├── adapter.py       # telegram.Update → NormalizedMessage
    │       ├── bot.py           # Application setup + lifecycle
    │       ├── handlers.py      # thin: parse → call core → reply
    │       └── keyboards.py
    │
    └── discord/                 # future — same shape
        ├── pyproject.toml
        └── src/moodbot_discord/
            ├── adapter.py
            ├── bot.py
            └── handlers.py
```

### NormalizedMessage (the key abstraction)

```python
# core/models.py
@dataclass
class NormalizedMessage:
    platform: str          # "telegram" | "discord"
    user_id: str           # "tg:123456" | "dc:789"
    text: str | None
    selected_emotions: list[str]
    timestamp: datetime

@dataclass
class MoodEntry:
    user_id: str
    platform: str
    emotions: list[str]
    mean_valence: float
    mean_arousal: float
    timestamp: datetime
```

### Adding Discord Later

1. Write `packages/discord/` — adapter + handlers
2. Register it in `main.py`
3. Zero changes to `packages/core/`

The package boundary (`pyproject.toml` per package, no cross-imports) enforces this.

### Deployment

```yaml
# docker-compose.yml
services:
  moodbot:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data       # SQLite lives here
    depends_on: [influxdb]

  influxdb:
    image: influxdb:2
    volumes:
      - influxdb-data:/var/lib/influxdb2
```

Single container, single asyncio process:
```python
# main.py
async def main():
    db = await SettingsDB.connect("data/settings.db")
    influx = InfluxStorage(settings)
    await asyncio.gather(
        TelegramAdapter(settings, db, influx).run(),
        # DiscordAdapter(settings, db, influx).run(),  # uncomment when ready
    )
```

### Pros / Cons

| + | − |
|---|---|
| Core boundary enforced by packaging | Slightly more setup (workspace config) |
| Atomic commits across core + platform | Two `pyproject.toml` files to maintain |
| Adding a platform = one new package | |
| Single container, no operational overhead | |

---

## Option 3 — Hub-and-Spoke (OpenClaw-inspired)

**Best for:** If platforms need to be deployed, scaled, or owned independently.

### Structure

```
moodbot/
├── gateway/                     # always-running core service
│   ├── main.py                  # HTTP/WebSocket server (FastAPI or aiohttp)
│   ├── router.py                # routes NormalizedMessages to handlers
│   ├── core/                    # same modules as Option 2's core
│   └── storage/
│
├── adapters/
│   ├── telegram/                # separate process
│   │   └── main.py              # connects to gateway, translates messages
│   └── discord/                 # separate process
│       └── main.py
│
└── docker-compose.yml
```

### How It Works

```
Telegram adapter  ──→  Gateway (HTTP POST /message)
                            └── router → core handlers → storage
                        Gateway (HTTP POST /send) ──→  Telegram adapter
```

Each adapter runs as a separate service. The gateway is platform-agnostic. Adapters connect to it over HTTP or a message queue (Redis, etc.).

### Pros / Cons

| + | − |
|---|---|
| Platforms fully independent | Significant added complexity |
| Can restart Telegram without touching Discord | Network hop for every message |
| Each adapter can be a different language | Need shared state solution (Redis/Postgres instead of SQLite) |
| Matches how OpenClaw works | Overkill for a personal bot |

---

## Stats & Analysis Modules (all options)

These live in `core/stats/` regardless of option chosen.

### Planned analyses

| Module | What it produces |
|---|---|
| `russell_map.py` | Scatter plot of selected emotions on valence/arousal axes, confidence ellipse |
| `frequency.py` | Emotion frequency bar chart, top-N over a time range |
| `trends.py` | Valence/arousal time series, rolling average |
| `time_of_day.py` | Heatmap: emotion patterns by hour-of-day / day-of-week |
| `summary.py` | Text summary: most frequent emotion, valence trend, streak |
| `clustering.py` | K-means or DBSCAN on valence/arousal to find personal emotion clusters |

### InfluxDB schema

```
measurement: mood_entry
  tag:   platform        "telegram"
  tag:   user_id         "tg:123456"
  field: mean_valence    0.62
  field: mean_arousal    0.45
  field: emotions        "Happy,Excited"   # comma-separated keys
  time:  <RFC3339>

measurement: selected_emotion   # one point per emotion per entry
  tag:   platform
  tag:   user_id
  tag:   emotion         "Happy"
  field: valence         0.826
  field: arousal         0.526
  time:  <RFC3339>
```

---

---

## SQLite Settings Schema

Use a hybrid approach: real columns for anything the scheduler queries in SQL, JSON blob for everything else.

```sql
CREATE TABLE user_settings (
    user_id      TEXT,
    platform     TEXT,
    reminders_on INTEGER DEFAULT 1,    -- queried by scheduler (WHERE reminders_on = 1)
    settings     TEXT    DEFAULT '{}', -- language, intervals, frequencies, etc.
    PRIMARY KEY (user_id, platform)
)
```

New settings need **zero migrations** — add a default in Python's `get_setting()`, existing users get it automatically. Only add a real column if you need to `WHERE` on it in SQL.

If schema changes are ever needed (e.g. renaming a column), use a `schema_version` table and append `ALTER TABLE` statements to a `MIGRATIONS` list that runs on startup.

---

## Recommendation

**Go with Option 2.** The workspace package boundary costs one extra `pyproject.toml` and pays for itself the moment Discord is added. Option 1 is fine if Discord is truly never happening; Option 3 is only justified if different people own different platforms or if scale demands it.

Immediate next steps for Option 2:
1. Init `uv` workspace (`uv init --workspace`) or Poetry workspaces
2. Create `packages/core/` — emotions, models, i18n, storage interfaces
3. Create `packages/telegram/` — thin handlers calling core
4. Wire `main.py` + `docker-compose.yml`
5. Migrate InfluxDB data (schema is mostly compatible, just drop mood_score field)
