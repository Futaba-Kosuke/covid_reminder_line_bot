import os
from typing import Final

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1.collection import CollectionReference


class Firebase:
    FIREBASE_CRED_ID: Final[str] = os.getenv("COVID19_REMINDER_FIREBASE_CRED_ID")

    cred: credentials.Certificate \
        = credentials.Certificate(os.path.dirname(__file__)
                                  + "\\covid-reminder-line-bot-firebase-adminsdk-"
                                  + FIREBASE_CRED_ID + ".json")
    firebase_app: firebase_admin.App = firebase_admin.initialize_app(cred)
    db: Client = firestore.client(firebase_app)

    def get_reference(self, collection_name: str) -> CollectionReference:
        return self.db.collection(collection_name)

    def register_user(self, user_id: str, prefecture_id: str):
        users_collection = self.db.collection("users")
        users_collection.add({"userid": user_id, "prefectureid": prefecture_id})

    def update_user_prefecture_id(self, user_id: str, prefecture_id: str):
        users_collection = self.db.collection("users")
        users_doc = list(users_collection.where(u'userid', u'==', user_id).stream())[0]
        users_doc_dict = users_doc.to_dict()

        users_doc_dict["prefectureid"] = prefecture_id
        self.db.collection("users").document(users_doc.id).set(users_doc_dict)

    def update_prefecture_userid_list(self, prefecture_id: str, user_id: str, action='add'):
        prefecture_collection = self.db.collection("prefectures")
        prefecture_doc = list(prefecture_collection.where(u'id', u'==', prefecture_id).stream())[0]
        prefecture_doc_dict = prefecture_doc.to_dict()

        if action == 'add':
            prefecture_doc_dict['userid'].append(user_id)
        elif action == 'remove':
            prefecture_doc_dict['userid'].remove(user_id)

        self.db.collection("prefectures").document(prefecture_doc.id).set(prefecture_doc_dict)
