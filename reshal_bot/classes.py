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
    manual_file = State()
    additional_info = State()

class OrderHistoryFilters:
    def __init__(self):
        self.work = ["sdo", "lab"]
        self.status = ["begin", "waiting", "execution", "stopped", "cancelled", "completed"]

class SelectedServices:
    def __init__(self):
        self.current = {}
        self.append = {}
        self.remove = {}

class OrderFilters:
    def __init__(self):
        self.work = ["sdo", "lab"]
        self.status = ["begin", "waiting", "execution", "stopped", "cancelled", "completed"]


class Config:
    selected_services = SelectedServices()
    order_filters = OrderFilters()
    order_history_filters = OrderHistoryFilters()

    def __init__(self):
        self.selected_services = Config.selected_services
        self.order_filters = Config.order_filters
        self.order_history_filters = Config.order_history_filters

    def instance_to_object(self):
        return {"selected_services": {
            "current": self.selected_services.current,
            "append": self.selected_services.append,
            "remove": self.selected_services.remove
            },
            "order_filters": {
            "work": self.order_filters.work,
            "status": self.order_filters.status
            },
            "order_history_filters": {
            "work": self.order_history_filters.work,
            "status": self.order_history_filters.status
            }
        }

    @classmethod
    def class_to_object(cls):
        return {"selected_services": {
            "current": cls.selected_services.current,
            "append": cls.selected_services.append,
            "remove": cls.selected_services.remove
            },
            "order_filters": {
            "work": cls.order_filters.work,
            "status": cls.order_filters.status
            },
            "order_history_filters": {
            "work": cls.order_history_filters.work,
            "status": cls.order_history_filters.status
            }
        }

    def instance_to_json(self):
        return json.dumps(self.instance_to_object())
    @classmethod
    def class_to_json(cls):
        return json.dumps(cls.class_to_object())

class OtherData:
    temporary_data = []
    bg_photo_id = "AgACAgIAAxkBAAID8mcP_IxahT-2AgGZQzgB2E5ae_aJAAI8_DEbu4iBSGKhe0Jq4jOPAQADAgADeAADNgQ"
    message_id = None
    def __init__(self):
        self.temporary_data = OtherData.temporary_data
        self.bg_photo_id = OtherData.bg_photo_id
        self.message_id = OtherData.message_id

    def instance_to_object(self):
        return {"temporary_data": self.temporary_data,
                "bg_photo_id": self.bg_photo_id,
                "message_id": self.message_id}
    @classmethod
    def class_to_object(cls):
        return {"temporary_data": cls.temporary_data,
                "bg_photo_id": cls.bg_photo_id,
                "message_id": cls.message_id}
    def instance_to_json(self):
        return json.dumps(self.instance_to_object())
    @classmethod
    def class_to_json(cls):
        return json.dumps(cls.class_to_object())


class Order:
    def __init__(self, chat_id, username, year, subject, subject_name, work, work_name, work_id, work_id_name, date_reg, status, price, executor_chat_id, executor_username, specific_data):
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
        self.status = status
        self.price = price
        self.executor_chat_id = executor_chat_id
        self.executor_username = executor_username
        self.specific_data = specific_data

class Executor:
    def __init__(self, username, first_name, last_name, date_reg, config, other_data):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.date_reg = date_reg
        self.config = config
        self.other_data = other_data







