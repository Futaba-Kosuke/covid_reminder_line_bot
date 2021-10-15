from typing import List, Any, Final, Dict
import json
import copy

from linebot.models \
    import FlexSendMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction

from covid_data_getter import PatientsType, prefectures_dict


def get_patients_message(
        patients: PatientsType,
        target_prefectures: List[str],
        month: int,
        day: int,
        now: Any
) -> FlexSendMessage:
    with open('messages/templates/flex_message.json') as f:
        flex_message = json.load(f)

    with open('messages/templates/prefecture_row.json') as f:
        prefecture_row = json.load(f)

    with open('messages/templates/reference_content.json') as f:
        reference_content = json.load(f)

    flex_message['header']['contents'][0]['contents'][0]['text'] \
        = f'{month}月{day}日 COVID-19 感染状況'

    month_now = str(now.month).zfill(2)
    day_now = str(now.day).zfill(2)
    hour_now = str(now.hour).zfill(2)
    minute_now = str(now.minute).zfill(2)
    flex_message['header']['contents'][0]['contents'][1]['text'] \
        = f'{month_now}月{day_now}日 {hour_now}:{minute_now} 時点'

    for prefecture in target_prefectures:

        if prefecture == 'ALL':
            # 全国データの更新
            flex_message['body']['contents'][2]['contents'][1]['text'] \
                = f'{str(patients[prefecture]["patients"])}人'
            flex_message['body']['contents'][2]['contents'][2]['text'] \
                = f'{str(patients[prefecture]["severe"])}人'
            continue

        # 各県データの追加
        prefecture_row['contents'][1]['contents'][0]['text'] = prefectures_dict[prefecture]
        prefecture_row['contents'][1]['contents'][1]['text'] \
            = f'{str(patients[prefecture]["patients"])}人'
        prefecture_row['contents'][1]['contents'][2]['text'] \
            = f'{str(patients[prefecture]["severe"])}人'

        flex_message['body']['contents'].append(copy.deepcopy(prefecture_row))

    flex_message['body']['contents'].append(reference_content)

    return FlexSendMessage(alt_text=f'{month}月{day}日 COVID-19 感染者数', contents=flex_message)


def get_quick_reply_buttons(prefix: str, values: List[str]) -> QuickReply:
    items = [
        QuickReplyButton(
            action=MessageAction(label=value, text=f'{prefix} {value}')
        ) for value in values
    ]
    return QuickReply(items=items)
