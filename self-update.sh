#!/bin/bash

REPO_PATH="/home/ivan/bots/tg-howwasyourday-v2"
SERVICE_NAME="howwasyourdaybot.service"

cd $REPO_PATH

git fetch

# https://stackoverflow.com/a/3278427
UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
    git pull
    # restart the bot
    echo "Restarting the bot"
    systemctl --user restart $SERVICE_NAME
    echo "Done!"
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi


git add latexdiff_bot/user_settings.json
git commit -m "updated user settings"
git push