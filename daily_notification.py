import os
from typing import Final, List
from datetime import datetime

from aiolinebot import AioLineBotApi

from covid_data_getter import get_daily_patients
from db_connector import Firebase, UserDataType
from messages import get_patients_message

LINE_ACCESS_TOKEN: Final[str] = os.getenv('COVID19_REMINDER_LINE_ACCESS_TOKEN')
line_api = AioLineBotApi(channel_access_token=LINE_ACCESS_TOKEN)

firebase = Firebase()


def main() -> None:
    now = datetime.now()
    daily_patients, month, day = get_daily_patients()
    all_users: List[UserDataType] = firebase.get_all_users()

    for user in all_users:
        user_id: str = user['user_id']
        prefecture_en_list: List[str] = user['prefecture_en_list']

        message = get_patients_message(daily_patients, prefecture_en_list, month, day, now)

        line_api.push_message(to=user_id, messages=message)

    return


if __name__ == '__main__':
    main()
