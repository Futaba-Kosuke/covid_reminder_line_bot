import os
import sys
from typing import Final, List, NoReturn

import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks
from linebot import WebhookParser, exceptions
from linebot.models import TextMessage
from linebot.models.events \
    import MessageEvent as LineMessageEventType, TextMessage as LineTextMessageEventType
from aiolinebot import AioLineBotApi

from covid_data_getter import prefectures_dict, get_daily_patients
from db_connector import Firebase

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

# firebase Instance
firebase = Firebase()


def get_prefectures_dict_reverse() -> dict[str]:
    return {
        **{
            prefecture_ja: prefecture_en
            for prefecture_en, prefecture_ja in list(prefectures_dict.items())[1:]
        },
        **{
            prefecture_ja[:-1]: prefecture_en
            for prefecture_en, prefecture_ja in list(prefectures_dict.items())[1:]
        }
    }


def add_user_prefecture(user_id: str, new_prefecture: str) -> str:
    # registration
    prefectures_dict_reverse: dict[str, str] = get_prefectures_dict_reverse()

    if new_prefecture in prefectures_dict_reverse.keys():
        is_success: bool = firebase.add_user_prefecture(
            user_id=user_id,
            prefecture_en=prefectures_dict_reverse[new_prefecture]
        )
        if is_success:
            return f'{new_prefecture}が通知する都道府県に追加されました！'
        else:
            return f'{new_prefecture}は既に登録されています！'

    return '都道府県名の指定が正しくありません！'


def remove_user_prefecture(user_id: str, new_prefecture: str) -> str:
    # registration
    prefectures_dict_reverse: dict[str, str] = get_prefectures_dict_reverse()

    if new_prefecture in prefectures_dict_reverse.keys():
        is_success: bool = firebase.remove_user_prefecture(
            user_id=user_id,
            prefecture_en=prefectures_dict_reverse[new_prefecture]
        )
        if is_success:
            return f'{new_prefecture}が通知する都道府県から削除されました！'
        else:
            return f'{new_prefecture}はまだ登録されていません！'

    return '都道府県名の指定が正しくありません！'


def get_daily_patients_message(user_id: str) -> str:
    # send today's number of new infected
    daily_patients, date = get_daily_patients()
    target_prefectures: List[str] = firebase.get_user_prefectures_en(user_id)

    reply_message: str = f'{date}\n'
    for target_prefecture in target_prefectures:
        prefecture = prefectures_dict[target_prefecture]
        patient = daily_patients[target_prefecture]
        reply_message += f'{prefecture}の新規感染者数: {patient}\n'

    return reply_message[:-1]


# body of echo
async def echo_body(event: LineTextMessageEventType, user_id: str) -> NoReturn:
    message_text: List[str] = event.message.text.split()

    if message_text[0] == '追加' and len(message_text) == 2:
        reply_message: str = add_user_prefecture(
            user_id=user_id,
            new_prefecture=message_text[1]
        )

    elif message_text[0] == '削除' and len(message_text) == 2:
        reply_message: str = remove_user_prefecture(
            user_id=user_id,
            new_prefecture=message_text[1]
        )

    else:
        reply_message: str = get_daily_patients_message(user_id=user_id)

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
            background_tasks.add_task(
                echo_body,
                event=request_event,
                user_id=request_event.source.user_id
            )

    # return response
    return Response(content="OK", status_code=200)


def main():
    port = int(os.getenv("PORT", 5000))
    uvicorn.run('main:app', host='0.0.0.0', port=port, reload=True, workers=2)


if __name__ == '__main__':
    main()
