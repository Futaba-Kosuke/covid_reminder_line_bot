import os
import sys

import uvicorn
from fastapi import FastAPI
from linebot import WebhookParser
from linebot.models import TextMessage
from aiolinebot import AioLineBotApi

# get token and secret from os environment
if not (line_token := os.environ.get(
    "POETRY_COVID19_REMINDER_LINE_BOT_TOKEN")):
    sys.exit("")
if not (line_secret := os.environ.get(
    "POETRY_COVID19_REMINDER_LINE_BOT_CHANNEL_SECRET")):
    sys.exit("")

# create line api client
line_api = AioLineBotApi(channel_access_token=line_token)

# create parser
parser = WebhookParser(channel_secret=line_secret)

# startup FastAPI
app = FastAPI()


def main():
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=2)


if __name__ == '__main__':
    main()
