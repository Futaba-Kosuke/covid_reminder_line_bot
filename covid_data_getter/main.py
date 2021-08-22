from typing import List, Tuple, TypedDict, Final

import pandas as pd

OPEN_DATA_URL: Final[str] \
    = 'https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv'

prefectures: Final[Tuple[str, ...]] = (
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
