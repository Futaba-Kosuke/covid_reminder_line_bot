import os
import sys

import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks
from linebot import WebhookParser, exceptions
from linebot.models import TextMessage
from aiolinebot import AioLineBotApi

# get token and secret from os environment
if not (line_token := os.environ.get(
    "POETRY_COVID19_REMINDER_LINE_BOT_TOKEN")):
    sys.exit("Environment variable not found ‘LINE_BOT_TOKEN’")
if not (line_secret := os.environ.get(
    "POETRY_COVID19_REMINDER_LINE_CHANNEL_SECRET")):
    sys.exit("Environment variable not found ‘LINE_CHANNEL_SECRET’")

# create line api client
line_api = AioLineBotApi(channel_access_token=line_token)

# create parser
parser = WebhookParser(channel_secret=line_secret)

# startup FastAPI
app = FastAPI()


def main():
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=2)


# body of echo
async def echo_body(event) -> None:
    await line_api.reply_message_async(
        event.reply_token,
        TextMessage(text=f"{event.message.text}")
    )
    pass

@app.post("/messaging_api/echo")
async def echo(
    request: Request, background_tasks: BackgroundTasks) -> Response:
    # parse request and get events
    try:
        events = parser.parse(
            (await request.body()).decode("utf-8"),
            request.headers.get("X-Line-Signature", "")
        )
    except exceptions.InvalidSignatureError:
        print("Error: failed to parse events")
        # return 503
        return Response(content="Internal Server Error", status_code=503)

    # process each event
    for ev in events:
        background_tasks.add_task(echo_body, event = ev)

    # return response
    return Response(content="OK", status_code=200)


if __name__ == '__main__':
    main()
