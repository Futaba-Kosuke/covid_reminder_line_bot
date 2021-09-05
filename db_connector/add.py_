import os
from typing import Dict, Final

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot

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

FIREBASE_CRED_ID = os.getenv("COVID19_REMINDER_FIREBASE_CRED_ID")

cred: credentials.Certificate \
    = credentials.Certificate(os.path.dirname(__file__)
                              + "\\covid-reminder-line-bot-firebase-adminsdk-"
                              + FIREBASE_CRED_ID + ".json")
app: firebase_admin.App = firebase_admin.initialize_app(cred)

db: Client = firestore.client(app)
ref: CollectionReference = db.collection(u'prefectures')
docs = ref.stream()

for id, name in list(prefectures_dict.items())[1:]:
    ref.add({"id": id, "name": name, "userid": []})
