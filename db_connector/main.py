import random
from typing import List, NoReturn, TypedDict, Optional

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client

UserDataType = TypedDict('UserDataType', {
    'user_id': str,
    'prefecture_en_list': List[str]
})

PrefectureDataType = TypedDict('PrefectureDataType', {
    'name_en': str,
    'name_ja': str,
    'user_id_list': List[str]
})


class Firebase:

    def __init__(self, cred_path: str = './db_connector/cred.json') -> NoReturn:
        cred = credentials.Certificate(cred_path)
        app = firebase_admin.initialize_app(cred, name=str(random.random()))
        self.db: Client = firestore.client(app)

    def get_user_data(self, user_id: str) -> UserDataType:
        user_data: UserDataType = self.db.collection('users').document(user_id).get().to_dict()
        if user_data is None:
            return {
                'user_id': user_id,
                'prefecture_en_list': []
            }
        return user_data

    def get_prefecture_data(self, prefecture_en: str) -> Optional[PrefectureDataType]:
        prefecture_data: PrefectureDataType \
            = self.db.collection('prefectures').document(prefecture_en).get().to_dict()
        if prefecture_data is None:
            return {
                'name_en': '',
                'name_ja': '',
                'user_id_list': []
            }
        return prefecture_data

    def set_user_data(self, user_id: str, prefecture_en_list: List[str]) -> NoReturn:
        user_doc_ref = self.db.collection('users').document(user_id)
        user_data: UserDataType = {
            'user_id': user_id,
            'prefecture_en_list': prefecture_en_list
        }
        user_doc_ref.set(user_data)

    def set_prefecture_data(
            self, prefecture_en: str, prefecture_ja: str, user_id_list: List[str]) -> NoReturn:
        prefecture_doc_ref = self.db.collection('prefectures').document(prefecture_en)
        prefecture_data: PrefectureDataType = {
            'name_en': prefecture_en,
            'name_ja': prefecture_ja,
            'user_id_list': user_id_list
        }
        prefecture_doc_ref.set(prefecture_data)

    def get_user_prefectures_en(self, user_id: str) -> List[str]:
        user_data: UserDataType = self.get_user_data(user_id=user_id)
        if user_data is None:
            return ['ALL']
        return ['ALL'] + user_data['prefecture_en_list']

    def add_user_prefecture(self, user_id: str, prefecture_en: str) -> bool:
        # get previous data
        user_data: UserDataType = self.get_user_data(user_id=user_id)
        prefecture_data: PrefectureDataType = self.get_prefecture_data(prefecture_en=prefecture_en)

        if prefecture_en in user_data['prefecture_en_list']:
            return False

        # variable update
        user_data['prefecture_en_list'].append(prefecture_en)
        prefecture_data['user_id_list'].append(user_id)

        # db update
        self.set_user_data(
            user_id=user_id,
            prefecture_en_list=user_data['prefecture_en_list']
        )
        self.set_prefecture_data(
            prefecture_en=prefecture_en,
            prefecture_ja=prefecture_data['name_ja'],
            user_id_list=prefecture_data['user_id_list']
        )
        return True

    def remove_user_prefecture(self, user_id: str, prefecture_en: str) -> bool:
        # get previous data
        user_data: UserDataType = self.get_user_data(user_id=user_id)
        prefecture_data: PrefectureDataType = self.get_prefecture_data(prefecture_en=prefecture_en)

        if prefecture_en not in user_data['prefecture_en_list']:
            return False

        # variable update
        user_data['prefecture_en_list'].remove(prefecture_en)
        prefecture_data['user_id_list'].remove(user_id)

        # db update
        self.set_user_data(
            user_id=user_id,
            prefecture_en_list=user_data['prefecture_en_list']
        )
        self.set_prefecture_data(
            prefecture_en=prefecture_en,
            prefecture_ja=prefecture_data['name_ja'],
            user_id_list=prefecture_data['user_id_list']
        )
        return True
