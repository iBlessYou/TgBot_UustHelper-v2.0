import copy
import json

from db_connection import connection
from datetime import datetime
from dataclasses import dataclass
from aiogram.filters.callback_data import CallbackData

from aiogram.fsm.state import State, StatesGroup

class Callback_Data(CallbackData, prefix="my"):
    key: str
    value: str

class Form(StatesGroup):
    login = State()
    password = State()
    manual_file_lab = State()
    manual_file_kurs = State()
    additional_info_lab = State()
    additional_info_kurs = State()

class OrderHistoryFilters:
    def __init__(self):
        self.work = ["sdo", "lab", "kurs"]

class Config:
    order_history_filters = OrderHistoryFilters()
    def __init__(self):
        self.order_history_filters = OrderHistoryFilters()

    def instance_to_json(self):
        data = {"order_history_filters": {
            "work": self.order_history_filters.work}
        }
        return json.dumps(data)
    @classmethod
    def class_to_json(cls):
        data = {"order_history_filters": {
            "work": cls.order_history_filters.work}
        }
        return json.dumps(data)

class OtherData:
    temporary_data = []
    bg_photo_id = "AgACAgIAAxkBAAIXE2b5J05A4R_zpHjJLxD1mxeUrwclAALR7jEbisXJSzaV5jviuAYEAQADAgADeAADNgQ"
    message_id = None
    def __init__(self):
        self.temporary_data = OtherData.temporary_data
        self.bg_photo_id = OtherData.bg_photo_id
        self.message_id = OtherData.message_id

    def instance_to_json(self):
        data = {"temporary_data": self.temporary_data,
                "bg_photo_id": self.bg_photo_id,
                "message_id": self.message_id}
        return json.dumps(data)
    @classmethod
    def class_to_json(cls):
        data = {"temporary_data": cls.temporary_data,
                "bg_photo_id": cls.bg_photo_id,
                "message_id": cls.message_id}
        return json.dumps(data)


class User:
    def __init__(self, username, first_name, last_name, year, date_reg, config, other_data):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.year = year
        self.date_reg = date_reg
        self.config = copy.deepcopy(config)
        self.other_data = copy.deepcopy(other_data)


class Order:
    def __init__(self, chat_id, username, year, subject, subject_name, work, work_name, work_id, work_id_name, date_reg, price, executor_chat_id, executor_username, specific_data):
        self.chat_id = chat_id
        self.username = username
        self.year = year
        self.subject = subject
        self.subject_name = subject_name
        self.work = work
        self.work_name = work_name
        self.work_id = work_id
        self.work_id_name = work_id_name
        self.date_reg = date_reg
        self.price = price
        self.executor_chat_id = executor_chat_id
        self.executor_username = executor_username
        self.specific_data = specific_data








