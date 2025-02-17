import asyncio
import config
import content
import functions
import db_connection
import classes
import json
import os

from classes import Callback_Data
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

bot = Bot(token=config.token_reshalbot)
mainbot = Bot(token=config.token_mainbot)
dp = Dispatcher()

executors_list = functions.import_lists_from_db(["executors_list"])

# СТАРТ
@dp.message(CommandStart())
async def start(message: Message):
    if message.from_user.username not in config.username_access_list:

        await message.delete()
        await message.answer(content.text_not_access)

    else:
        bg_photo_id = executors_list[message.chat.id].other_data if message.chat.id in list(
            executors_list.keys()) else classes.OtherData.bg_photo_id

        markup = InlineKeyboardBuilder()
        markup.button(text="Заказы", callback_data=Callback_Data(key="orders", value=""))
        markup.button(text="Запросы", callback_data=Callback_Data(key="application", value=""))
        markup.button(text="История заказов", callback_data=Callback_Data(key="order_history", value=""));
        markup.adjust(1)

        await message.delete()
        await message.answer_photo(bg_photo_id, caption=content.text_main, reply_markup=markup.as_markup())

        functions.register_executor(message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, executors_list)

