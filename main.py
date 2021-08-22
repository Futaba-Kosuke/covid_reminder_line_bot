import os
import sys
from typing import Final, List, Tuple, NoReturn, TypedDict

import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks
from linebot import WebhookParser, exceptions
from linebot.models import TextMessage, events
from aiolinebot import AioLineBotApi


LINE_TOKEN: Final[str] = os.getenv('COVID19_REMINDER_LINE_TOKEN')
LINE_SECRET: Final[str] = os.getenv('COVID19_REMINDER_LINE_CHANNEL_SECRET')
OPEN_DATA_URL: str = 'https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv'

if LINE_TOKEN is None:
    sys.exit("Environment variable not found ‘COVID19_REMINDER_LINE_BOT_TOKEN’")
if LINE_SECRET is None:
    sys.exit("Environment variable not found ‘COVID19_REMINDER_LINE_CHANNEL_SECRET’")

# create line api client
line_api = AioLineBotApi(channel_access_token=LINE_TOKEN)

# create parser
parser = WebhookParser(channel_secret=LINE_SECRET)

# startup FastAPI
app = FastAPI()

# definite peculiar types
LineMessageEventType = events.MessageEvent
LineTextMessageEventType = events.TextMessage
prefectures: Tuple[str, ...] = (
    'ALL', 'Hokkaido', 'Aomori', 'Iwate', 'Miyagi', 'Akita', 'Yamagata', 'Fukushima', 'Ibaraki',
    'Tochigi', 'Gunma', 'Saitama', 'Chiba', 'Tokyo', 'Kanagawa', 'Niigata', 'Toyama', 'Ishikawa',
    'Fukui', 'Yamanashi', 'Nagano', 'Gifu', 'Shizuoka', 'Aichi', 'Mie', 'Shiga', 'Kyoto', 'Osaka',
    'Hyogo', 'Nara', 'Wakayama', 'Tottori', 'Shimane', 'Okayama', 'Hiroshima', 'Yamaguchi',
    'Tokushima', 'Kagawa', 'Ehime', 'Kochi', 'Fukuoka', 'Saga', 'Nagasaki', 'Kumamoto', 'Oita',
    'Miyazaki', 'Kagoshima', 'Okinawa')
PatientsType = TypedDict('PatientsType', {
    prefecture: int
    for prefecture in prefectures
})


def get_daily_patients() -> PatientsType:
    df = pd.read_csv(OPEN_DATA_URL)[-48:]
    daily_patients: PatientsType = {
        row['Prefecture']: row['Newly confirmed cases']
        for index, row in df.iterrows()
    }
    return daily_patients


def mock_get_target_prefectures() -> List[str]:
    return ['Fukui']


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
