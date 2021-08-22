import os
import sys
from typing import Final, List, NoReturn

import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks
from linebot import WebhookParser, exceptions
from linebot.models import TextMessage, events
from aiolinebot import AioLineBotApi

from covid_data_getter import PatientsType, get_daily_patients, mock_get_target_prefectures

LINE_ACCESS_TOKEN: Final[str] = os.getenv('COVID19_REMINDER_LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET: Final[str] = os.getenv('COVID19_REMINDER_LINE_CHANNEL_SECRET')

if LINE_ACCESS_TOKEN is None:
    sys.exit("Environment variable not found ‘COVID19_REMINDER_LINE_ACCESS_TOKEN’")
if LINE_CHANNEL_SECRET is None:
    sys.exit("Environment variable not found ‘COVID19_REMINDER_LINE_CHANNEL_SECRET’")

# create line api client
line_api = AioLineBotApi(channel_access_token=LINE_ACCESS_TOKEN)

# create parser
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# startup FastAPI
app = FastAPI()

# definite peculiar types
LineMessageEventType = events.MessageEvent
LineTextMessageEventType = events.TextMessage


# body of echo
async def echo_body(event: LineTextMessageEventType) -> NoReturn:
    daily_patients: PatientsType = get_daily_patients()
    target_prefectures: List[str] = mock_get_target_prefectures()

    reply_message: str = f'{target_prefectures[0]}の新規感染者数: {daily_patients[target_prefectures[0]]}'

    await line_api.reply_message_async(
        event.reply_token,
        TextMessage(text=reply_message)
    )
    return


@app.post("/messaging_api/echo")
async def echo(request: Request, background_tasks: BackgroundTasks) -> Response:
    # parse request and get events
    try:
        request_events: List[LineMessageEventType] = parser.parse(
            (await request.body()).decode("utf-8"),
            request.headers.get("X-Line-Signature", "")
        )
    except exceptions.InvalidSignatureError:
        print("Error: failed to parse events")
        # return 500
        return Response(content="Internal Server Error", status_code=500)

    # process each event
    for request_event in request_events:
        if isinstance(request_event.message, TextMessage):
            background_tasks.add_task(echo_body, event=request_event)

    # return response
    return Response(content="OK", status_code=200)


def main():
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=2)


if __name__ == '__main__':
    main()
