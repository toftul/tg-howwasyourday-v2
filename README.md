# tg-howwasyourday-v2
How was your day?


## Running with podman 

Build image
```shell
podman build -t howwasyourday-bot .
```
Run
```shell
podman run -d\
    --env TELEGRAM_BOT_TOKEN=''\
    --env ALLOWED_CHAT_IDS="123, 124"\
    --env LILYA_ID=\
    --env INFLUXDB_TOKEN=''\
    --env INFLUXDB_URL='http://localhost:8086'\
    --env INFLUXDB_ORG='home'\
    --env INFLUXDB_BUCKET='howwasyourday_testing'\
    --env DUE_MINIMAL_H=3\
    --env DUE_MAXIMAL_H=8\
    --env NAMES_FOR_LILYA_JSON="['', '', '']"\
    --env REMINDERS_LIST_JSON="['а? а? а? А? ААА? ААААА? а?!', 'ну че как там', 'sup?', 'How are you?', 'Как делишки?', 'Давно не было от тебя вестей, я соскучился!', 'Damn. Damn-damn!! Whats up!?']"
    localhost/howwasyourday-bot
```

Containers and poetry are not good frieds, so its easier to live with `requirements.txt`:
```shell
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Running with poetry
Or it can be run with just poetry but one needs to install [this plugin](https://github.com/mpeteuil/poetry-dotenv-plugin)
```shell
poetry self add poetry-dotenv-plugin
```
and create `.env` file
```shell
TELEGRAM_BOT_TOKEN='token'  
ALLOWED_CHAT_IDS='123, 1234' 
LILYA_ID=123
INFLUXDB_TOKEN='token'  
INFLUXDB_URL='http://localhost:8086'  
INFLUXDB_ORG='home'  
INFLUXDB_BUCKET='bucket'  
DUE_MINIMAL_H=3  
DUE_MAXIMAL_H=8  
NAMES_FOR_LILYA_JSON='["name1", "name2", "name3"]'  
REMINDERS_LIST_JSON='["а? а? а? А? ААА? ААААА? а?!", "ну че как там", "sup?", "How are you?", "Как делишки?", "Давно не было от тебя вестей, я соскучился!", "Damn. Damn-damn!! Whats up!?"]'
```