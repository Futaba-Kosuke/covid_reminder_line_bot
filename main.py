import os
import sys
from typing import Final, List, Dict, NoReturn
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks
from linebot import WebhookParser, exceptions
from linebot.models import TextMessage, TextSendMessage, FlexSendMessage
from linebot.models.events \
    import MessageEvent as LineMessageEventType, TextMessage as LineTextMessageEventType
from aiolinebot import AioLineBotApi

from covid_data_getter import prefectures_dict, get_daily_patients
from db_connector import Firebase
from messages \
    import get_patients_message, get_quick_reply_buttons

LINE_ACCESS_TOKEN: Final[str] = os.getenv('COVID19_REMINDER_LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET: Final[str] = os.getenv('COVID19_REMINDER_LINE_CHANNEL_SECRET')

if LINE_ACCESS_TOKEN is None:
    sys.exit("Environment variable not found ‘COVID19_REMINDER_LINE_ACCESS_TOKEN’")
if LINE_CHANNEL_SECRET is None:
    sys.exit("Environment variable not found ‘COVID19_REMINDER_LINE_CHANNEL_SECRET’")

region_to_prefectures: Final[Dict[str, List[str]]] = {
    '北海道, 東北': ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県'],
    '関東': ['茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県'],
    '中部': ['新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県'],
    '近畿': ['三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県'],
    '中国': ['鳥取県', '島根県', '岡山県', '広島県', '山口県'],
    '四国': ['徳島県', '香川県', '愛媛県', '高知県'],
    '九州': ['福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']
}

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


def get_daily_patients_message(user_id: str) -> FlexSendMessage:
    now = datetime.now()
    daily_patients, month, day = get_daily_patients()
    target_prefectures: List[str] = firebase.get_user_prefectures_en(user_id)

    return get_patients_message(daily_patients, target_prefectures, month, day, now)


# body of echo
async def echo_body(event: LineTextMessageEventType, user_id: str) -> NoReturn:
    message_text: List[str] = event.message.text.split(' ', 1)

    # 都道府県追加／地方のクイックリプライを送信
    if message_text[0] == '通知地域を追加する':
        text = 'どの地方の都道府県を追加しますか？'
        quick_reply = get_quick_reply_buttons(
            prefix='追加',
            values=list(region_to_prefectures.keys())
        )
        await line_api.reply_message_async(
            event.reply_token,
            TextSendMessage(text=text, quick_reply=quick_reply)
        )

    # 都道府県追加／都道府県のクイックリプライを送信
    elif message_text[0] == '追加' and message_text[1] in list(region_to_prefectures.keys()):
        text = 'どの都道府県を追加しますか？'
        quick_reply = get_quick_reply_buttons(
            prefix='追加',
            values=region_to_prefectures[message_text[1]]
        )
        await line_api.reply_message_async(
            event.reply_token,
            TextSendMessage(text=text, quick_reply=quick_reply)
        )

    # 都道府県の追加／実行
    elif message_text[0] == '追加' and len(message_text) == 2:
        reply_message: str = add_user_prefecture(
            user_id=user_id,
            new_prefecture=message_text[1]
        )
        await line_api.reply_message_async(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    # 都道府県の削除／都道府県のクイックリプライを送信
    elif message_text[0] == '通知地域を削除する':
        prefectures_en = firebase.get_user_prefectures_en(user_id=user_id)
        prefectures_ja = [prefectures_dict[prefecture_en] for prefecture_en in prefectures_en[1:]]

        text = 'どの都道府県を削除しますか？'
        quick_reply = get_quick_reply_buttons(
            prefix='削除',
            values=prefectures_ja
        )
        await line_api.reply_message_async(
            event.reply_token,
            TextSendMessage(text=text, quick_reply=quick_reply)
        )

    # 都道府県の削除／実行
    elif message_text[0] == '削除' and len(message_text) == 2:
        reply_message: str = remove_user_prefecture(
            user_id=user_id,
            new_prefecture=message_text[1]
        )
        await line_api.reply_message_async(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

    # その他／データ取得
    else:
        await line_api.reply_message_async(
            event.reply_token,
            get_daily_patients_message(user_id)
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
