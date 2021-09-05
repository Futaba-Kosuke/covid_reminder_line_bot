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

from covid_data_getter \
    import prefectures_dict, PatientsType, get_daily_patients
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


# body of echo
async def echo_body(event: LineTextMessageEventType, user_id: str) -> NoReturn:
    message_text = event.message.text.split()
    if message_text[0] == "登録" and len(message_text) >= 1:
        # registration
        prefectures_list = {"全国": "ALL"}
        prefectures_list |= ((name, prefecture_id)
                             for prefecture_id, name in list(prefectures_dict.items())[1:])
        prefectures_list |= ((name[:-1], prefecture_id)
                             for prefecture_id, name in list(prefectures_dict.items())[1:])

        if message_text[1] in prefectures_list.keys():
            # able to register, get previous prefecture
            new_prefecture_id = prefectures_list[message_text[1]]
            search_user = firebase.search_user(user_id)

            if len(search_user):
                previous_prefecture_id = search_user[0].to_dict()['prefectureid']
                firebase.update_prefecture_userid_list(previous_prefecture_id, user_id, 'remove')
                firebase.update_user_prefecture_id(user_id, new_prefecture_id)
                await line_api.reply_message_async(
                    event.reply_token,
                    TextMessage(text="都道府県の変更が完了しました。")
                )
            else:
                # register
                firebase.register_user(user_id, prefectures_list[message_text[1]])
                await line_api.reply_message_async(
                    event.reply_token,
                    TextMessage(text="都道府県の登録が完了しました。")
                )

            firebase.update_prefecture_userid_list(new_prefecture_id, user_id, 'add')

        else:
            # not able to register
            await line_api.reply_message_async(
                event.reply_token,
                TextMessage(text="都道府県名の指定が正しくありません。")
            )
        pass
    else:
        # send today's number of new infected
        daily_patients: PatientsType = get_daily_patients()
        # target_prefectures: List[str] = mock_get_target_prefectures()
        target_prefectures: str = firebase.get_user_prefecture(user_id)

        reply_message: str = f'{prefectures_dict[target_prefectures]}の新規感染者数: {daily_patients[target_prefectures]}'

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
            background_tasks.add_task(echo_body,
                                      event=request_event,
                                      user_id=request_event.source.user_id)

    # return response
    return Response(content="OK", status_code=200)


def main():
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=2)


if __name__ == '__main__':
    main()
