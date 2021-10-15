from typing import Dict, Tuple, TypedDict, Final
import re

import pandas as pd

PATIENTS_DATA_URL: Final[str] \
    = 'https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv'

SEVERE_DATA_URL: Final[str] \
    = 'https://covid19.mhlw.go.jp/public/opendata/severe_cases_daily.csv'

PATIENTS_COLUMN: Final[str] = 'Newly confirmed cases'
SEVERE_COLUMN: Final[str] = 'Severe cases'

prefectures_dict: Final[Dict[str, str]] = {
    'ALL': '全国',
    'Hokkaido': '北海道',
    'Aomori': '青森県',
    'Iwate': '岩手県',
    'Miyagi': '宮城県',
    'Akita': '秋田県',
    'Yamagata': '山形県',
    'Fukushima': '福島県',
    'Ibaraki': '茨城県',
    'Tochigi': '栃木県',
    'Gunma': '群馬県',
    'Saitama': '埼玉県',
    'Chiba': '千葉県',
    'Tokyo': '東京都',
    'Kanagawa': '神奈川県',
    'Niigata': '新潟県',
    'Toyama': '富山県',
    'Ishikawa': '石川県',
    'Fukui': '福井県',
    'Yamanashi': '山梨県',
    'Nagano': '長野県',
    'Gifu': '岐阜県',
    'Shizuoka': '静岡県',
    'Aichi': '愛知県',
    'Mie': '三重県',
    'Shiga': '滋賀県',
    'Kyoto': '京都府',
    'Osaka': '大阪府',
    'Hyogo': '兵庫県',
    'Nara': '奈良県',
    'Wakayama': '和歌山県',
    'Tottori': '鳥取県',
    'Shimane': '島根県',
    'Okayama': '岡山県',
    'Hiroshima': '広島県',
    'Yamaguchi': '山口県',
    'Tokushima': '徳島県',
    'Kagawa': '香川県',
    'Ehime': '愛媛県',
    'Kochi': '高知県',
    'Fukuoka': '福岡県',
    'Saga': '佐賀県',
    'Nagasaki': '長崎県',
    'Kumamoto': '熊本県',
    'Oita': '大分県',
    'Miyazaki': '宮崎県',
    'Kagoshima': '鹿児島県',
    'Okinawa': '沖縄県'
}

PatientType = TypedDict('PatientType', {
    'patients': int,
    'severe': int
})

PatientsType = TypedDict('PatientsType', {
    prefecture: PatientType
    for prefecture in prefectures_dict.keys()
})


def get_daily_patients() -> Tuple[PatientsType, int, int]:
    patients_df = pd.read_csv(PATIENTS_DATA_URL)[-48:]
    patients_df[SEVERE_COLUMN] = pd.read_csv(SEVERE_DATA_URL)[-48:][SEVERE_COLUMN].values
    daily_patients: PatientsType = {
        row['Prefecture']: {
            'patients': row[PATIENTS_COLUMN],
            'severe': row[SEVERE_COLUMN]
        }
        for index, row in patients_df.iterrows()
    }

    month, day = re.findall('/(.*?\d+)', patients_df['Date'][patients_df.index[0]])

    return daily_patients, int(month), int(day)