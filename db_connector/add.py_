import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from covid_data_getter import prefectures_dict

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
    ref.add({"id": id, "name": name})
