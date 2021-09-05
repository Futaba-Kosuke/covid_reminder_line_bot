import os
import random
from typing import Final, NoReturn

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client


class Firebase:

    def __init__(self) -> NoReturn:
        FIREBASE_CRED_ID: Final[str] = os.getenv("COVID19_REMINDER_FIREBASE_CRED_ID")
        cred: credentials.Certificate \
            = credentials.Certificate("./db_connector/cred.json")
        self.db: Client = firestore.client(
            firebase_admin.initialize_app(cred, name=str(random.random())))

    def get_user_prefecture(self, user_id: str) -> str:
        users_collection = self.db.collection("users")
        return \
            list(users_collection.where(u'userid', u'==', user_id).stream())[0] \
            .to_dict()['prefectureid']

    def register_user(self, user_id: str, prefecture_id: str) -> NoReturn:
        users_collection = self.db.collection("users")
        users_collection.add({"userid": user_id, "prefectureid": prefecture_id})

    def search_user(self, user_id: str) -> NoReturn:
        users_collection = self.db.collection("users")
        return list(users_collection.where(u'userid', u'==', user_id).stream())

    def update_user_prefecture_id(self, user_id: str, prefecture_id: str) -> NoReturn:
        users_collection = self.db.collection("users")
        users_doc = list(users_collection.where(u'userid', u'==', user_id).stream())[0]
        users_doc_dict = users_doc.to_dict()

        users_doc_dict["prefectureid"] = prefecture_id
        self.db.collection("users").document(users_doc.id).set(users_doc_dict)

    def update_prefecture_userid_list(
            self, prefecture_id: str, user_id: str, action: str) -> NoReturn:
        prefecture_collection = self.db.collection("prefectures")
        prefecture_doc = list(prefecture_collection.where(u'id', u'==', prefecture_id).stream())[0]
        prefecture_doc_dict = prefecture_doc.to_dict()

        if action == 'add':
            prefecture_doc_dict['userid'].append(user_id)
        elif action == 'remove':
            prefecture_doc_dict['userid'].remove(user_id)

        self.db.collection("prefectures").document(prefecture_doc.id).set(prefecture_doc_dict)
