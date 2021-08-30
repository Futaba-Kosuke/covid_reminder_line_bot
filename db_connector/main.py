import os
from typing import Final

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1.collection import CollectionReference

FIREBASE_CRED_ID: Final[str] = os.getenv("COVID19_REMINDER_FIREBASE_CRED_ID")


def get_reference(collection_name: str) -> CollectionReference:
    cred: credentials.Certificate \
        = credentials.Certificate(os.path.dirname(__file__)
                                  + "\\covid-reminder-line-bot-firebase-adminsdk-"
                                  + FIREBASE_CRED_ID + ".json")
    app: firebase_admin.App = firebase_admin.initialize_app(cred)

    db: Client = firestore.client(app)
    return db.collection(collection_name)
