import os
import json

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
#ALLOWED_CHAT_IDS_JSON = os.environ.get("ALLOWED_CHAT_IDS_JSON")
#ALLOWED_CHAT_IDS = json.loads(ALLOWED_CHAT_IDS_JSON)
ALLOWED_CHAT_IDS = os.environ.get("ALLOWED_CHAT_IDS", default="").split(",")
lilya_id = os.environ.get("LILYA_ID")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUXDB_URL = os.environ.get("INFLUXDB_URL")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")

DUE_MINIMAL_H = os.environ.get("DUE_MINIMAL_H")
DUE_MAXIMAL_H = os.environ.get("DUE_MAXIMAL_H")

namesForLilya_JSON = os.environ.get("NAMES_FOR_LILYA_JSON")
namesForLilya = json.loads(namesForLilya_JSON)

remindersList_JSON = os.environ.get("REMINDERS_LIST_JSON")
remindersList = json.loads(remindersList_JSON)
