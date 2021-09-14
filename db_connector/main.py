import random
from typing import List, NoReturn

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client


class Firebase:

    def __init__(self) -> NoReturn:
        cred = credentials.Certificate('./db_connector/cred.json')
        app = firebase_admin.initialize_app(cred, name=str(random.random()))
        self.db: Client = firestore.client(app)

    def get_user_prefecture(self, user_id: str) -> str:
        users_collection = self.db.collection('users')
        try:
            user_data = list(users_collection.where('user_id', '==', user_id).stream())[0]
            user_prefecture: str = user_data.to_dict()['prefecture_id']
        except IndexError:
            return 'Fukui'
        return user_prefecture

    def register_user(self, user_id: str, prefecture_id: str) -> NoReturn:
        users_collection = self.db.collection('users')
        users_collection.add({'user_id': user_id, 'prefecture_id': prefecture_id})

    def search_user(self, user_id: str):
        users_collection = self.db.collection('users')
        return list(users_collection.where('user_id', '==', user_id).stream())

    def update_user_prefecture_id(self, user_id: str, prefecture_id: str) -> NoReturn:
        users_collection = self.db.collection('users')
        users_doc = list(users_collection.where('user_id', '==', user_id).stream())[0]
        users_doc_dict = users_doc.to_dict()

        users_doc_dict['prefecture_id'] = prefecture_id
        self.db.collection('users').document(users_doc.id).set(users_doc_dict)

    def update_prefecture_userid_list(
            self, prefecture_id: str, user_id: str, action: str) -> NoReturn:
        prefecture_collection = self.db.collection('prefectures')
        prefecture_doc = list(prefecture_collection.where('id', '==', prefecture_id).stream())[0]
        prefecture_doc_dict = prefecture_doc.to_dict()

        if action == 'add':
            prefecture_doc_dict['user_id'].append(user_id)
        elif action == 'remove':
            prefecture_doc_dict['user_id'].remove(user_id)

        self.db.collection('prefectures').document(prefecture_doc.id).set(prefecture_doc_dict)
