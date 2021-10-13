import os
from typing import Final, List

from linebot.models import TextSendMessage
from aiolinebot import AioLineBotApi

from covid_data_getter import prefectures_dict, PatientsType, get_daily_patients
from db_connector import Firebase, UserDataType

LINE_ACCESS_TOKEN: Final[str] = os.getenv('COVID19_REMINDER_LINE_ACCESS_TOKEN')
line_api = AioLineBotApi(channel_access_token=LINE_ACCESS_TOKEN)

firebase = Firebase()


def main() -> None:
    daily_patients, date = get_daily_patients()
    all_users: List[UserDataType] = firebase.get_all_users()

    for user in all_users:
        user_id: str = user['user_id']
        prefecture_en_list: List[str] = user['prefecture_en_list']

        all_patients: PatientsType = daily_patients['ALL']
        message = f'{date}\n全国の新規感染者数: {all_patients}\n'
        for prefecture_en in prefecture_en_list:
            patients: PatientsType = daily_patients[prefecture_en]
            prefecture_ja: str = prefectures_dict[prefecture_en]
            message += f'{prefecture_ja}の新規感染者数: {patients}\n'

        line_api.push_message(to=user_id, messages=TextSendMessage(message[:-1]))

    return


if __name__ == '__main__':
    main()
