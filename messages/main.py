from typing import List
import json
import copy
from datetime import datetime

from linebot.models import FlexSendMessage

from covid_data_getter import PatientsType, prefectures_dict


def get_patients_message(
        patients: PatientsType,
        target_prefectures: List[str],
        month: int,
        day: int
) -> FlexSendMessage:
    with open('messages/templates/flex_message.json') as f:
        flex_message = json.load(f)

    with open('messages/templates/prefecture_row.json') as f:
        prefecture_row = json.load(f)

    with open('messages/templates/reference_content.json') as f:
        reference_content = json.load(f)

    flex_message['header']['contents'][0]['contents'][0]['text'] \
        = f'{month}月{day}日 COVID-19 感染者数'

    now = datetime.now()
    flex_message['header']['contents'][0]['contents'][1]['text'] \
        = f'{now.month}月{now.day}日 {now.hour}:{now.minute} 時点'

    for prefecture in target_prefectures:

        if prefecture == 'ALL':
            # 全国データの更新
            flex_message['body']['contents'][0]['contents'][1]['text'] \
                = patients[target_prefectures[0]]
            continue

        # 各県データの追加
        prefecture_row['contents'][1]['contents'][0]['text'] = prefectures_dict[prefecture]
        prefecture_row['contents'][1]['contents'][1]['text'] = f'{str(patients[prefecture])}人'

        flex_message['body']['contents'].append(copy.deepcopy(prefecture_row))

    flex_message['body']['contents'].append(reference_content)

    return FlexSendMessage(alt_text=f'{month}月{day}日 COVID-19 感染者数', contents=flex_message)
