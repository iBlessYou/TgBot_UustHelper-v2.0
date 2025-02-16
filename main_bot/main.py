import asyncio
import config
import content
import functions
import db_connection
import classes

from classes import Callback_Data
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

bot = Bot(token=config.token_mainbot)
reshalbot = Bot(token=config.token_reshalbot)
dp = Dispatcher()

users_list, sorted_data_orders = functions.import_lists_from_db(["users_list", "sorted_data_orders_list"])
print(users_list[1328304100].config.instance_to_object())
print(sorted_data_orders)

#   СТАРТ
@dp.message(CommandStart())
async def start(message: Message):
    bg_photo_id = users_list[message.chat.id].other_data.bg_photo_id if message.chat.id in list(users_list.keys()) else classes.OtherData.bg_photo_id

    markup = InlineKeyboardBuilder()
    markup.button(text="1 курс", callback_data=Callback_Data(key="year_confirmation", value="1"))
    markup.button(text="2 курс", callback_data=Callback_Data(key="year_confirmation", value="2"))

    await message.delete()
    await message.answer_photo(bg_photo_id, content.text_start(message.from_user.first_name), reply_markup=markup.as_markup())

    functions.register_user(message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, users_list, sorted_data_orders)

@dp.callback_query(Callback_Data.filter(F.key == "year_confirmation"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    year = int(callback_data.value)
    first_name = users_list[callback.message.chat.id].first_name

    markup = InlineKeyboardBuilder()
    markup.button(text="✅ Подтвердить", callback_data=Callback_Data(key="main", value=""))
    markup.button(text="🔄 Изменить", callback_data=Callback_Data(key="start", value=""))
    markup.adjust(1, 1)

    await callback.message.edit_caption(caption=content.text_year_confirmation(first_name, year), reply_markup=markup.as_markup())

    users_list[callback.message.chat.id].other_data.message_id = callback.message.message_id
    users_list[callback.message.chat.id].year = year
    db_connection.sql_UPDATE('public."Users"', "chat_id", callback.message.chat.id, ["year", "other_data"], *[year, users_list[callback.message.chat.id].other_data.instance_to_json()])

@dp.callback_query(Callback_Data.filter(F.key == "start"))
async def start(callback: CallbackQuery):
    first_name = users_list[callback.message.chat.id].first_name

    markup = InlineKeyboardBuilder()
    markup.button(text="1 курс", callback_data=Callback_Data(key="year_confirmation", value="1"))
    markup.button(text="2 курс", callback_data=Callback_Data(key="year_confirmation", value="2"))

    await callback.message.edit_caption(caption=content.text_start(first_name), reply_markup=markup.as_markup())

@dp.callback_query(Callback_Data.filter(F.key == "main"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Услуги", callback_data=Callback_Data(key=f"subjects", value=""))
    markup.button(text="Полезные материалы", callback_data=Callback_Data(key=f"useful_subjects", value=""))
    markup.button(text="📡 Помощь", callback_data=Callback_Data(key="help", value=""))
    markup.button(text="О нас", callback_data=Callback_Data(key="about_us", value=""))
    markup.button(text="📋 История заказов", callback_data=Callback_Data(key="order_history", value=""))
    markup.button(text="⚙️ Настройки", callback_data=Callback_Data(key="settings", value=""))
    markup.adjust(1, 1, 2, 1, 1)

    await callback.message.edit_caption(caption=content.text_main, reply_markup=markup.as_markup())

#   ГЛАВНОЕ МЕНЮ

    #   ПОМОЩЬ
@dp.callback_query(Callback_Data.filter(F.key=="help"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="main", value=""))

    await callback.message.edit_caption(caption=content.text_help, reply_markup=markup.as_markup())


    #   О НАС
@dp.callback_query(Callback_Data.filter(F.key=="about_us"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="main", value=""))

    await callback.message.edit_caption(caption=content.text_about_us, reply_markup=markup.as_markup())

    #   НАСТРОЙКИ
@dp.callback_query(Callback_Data.filter(F.key == "settings"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Изменить фон сообщения", callback_data=Callback_Data(key="background", value=""))
    markup.button(text="Изменить курс обучения", callback_data=Callback_Data(key="start", value=""))
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="main", value=""))
    markup.adjust(1, 1, 1)

    await callback.message.edit_caption(caption="Выберите нужную вам настройку.", reply_markup=markup.as_markup())


    #   НАСТРОЙКИ >>> ОТПРАВИТЬ ФОТО
@dp.callback_query(Callback_Data.filter(F.key == "background"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Отмена", callback_data=Callback_Data(key="settings", value=""))

    await callback.message.edit_caption(caption=content.text_settings_bg, reply_markup=markup.as_markup())


    #   НАСТРОЙКИ >>> ОТПРАВИТЬ ФОТО >>> ОБНОВИТЬ ФОН
@dp.message(F.photo)
async def photo_handle(message: Message):
    if message.reply_to_message and message.reply_to_message.caption == content.text_settings_bg:
        message_id = users_list[message.chat.id].other_data.message_id
        bg_photo_id = message.photo[-1].file_id

        markup = InlineKeyboardBuilder()
        markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="settings", value=""))

        await message.delete()
        await bot.edit_message_media(types.InputMediaPhoto(media=bg_photo_id, caption=content.text_new_bg), chat_id=message.chat.id, message_id=message_id, reply_markup=markup.as_markup())

        users_list[message.chat.id].other_data.bg_photo_id = bg_photo_id
        db_connection.sql_UPDATE('public."Users"', "chat_id", message.chat.id, ["other_data"], *[users_list[message.chat.id].other_data.instance_to_json()])


    #   ИСТОРИЯ ЗАКАЗОВ
@dp.callback_query(Callback_Data.filter(F.key == "order_history"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Настроить фильтры", callback_data=Callback_Data(key="order_history_filters", value="none_none"))
    markup.button(text="Назад", callback_data=Callback_Data(key="main", value=""))

    sorted_data = db_connection.sql_SELECT('public."Sorted_Data"', "object", "orders", ["data"])[0][0]

    for status in users_list[callback.message.chat.id].config.order_history_filters.status:
        for work in users_list[callback.message.chat.id].config.order_history_filters.work:
            data = list(set(sorted_data["chat_id"][str(callback.message.chat.id)]) & set(sorted_data["status"][status]) & set(sorted_data["work"][work]))
            for order_id in data:
                mark = functions.status_mark(status)
                text = f"{mark} Заказ № {order_id}"
                markup.button(text=text, callback_data=Callback_Data(key="order", value=f"{order_id}"))
    markup.adjust(1, 1)

    await callback.message.edit_caption(caption=content.text_order_history, reply_markup=markup.as_markup())


@dp.callback_query(Callback_Data.filter(F.key == "order_history_filters"))
async def callback(callback: CallbackQuery, callback_data=Callback_Data):
    filters = classes.OrderHistoryFilters()
    parameter = callback_data.value.split("_")[0]
    argument = callback_data.value.split("_")[1]
    data = users_list[callback.message.chat.id].config.order_history_filters

    def register_filters():
        if argument in getattr(data, parameter):
            getattr(data, parameter).remove(argument)
        elif argument not in getattr(data, parameter):
            getattr(data, parameter).append(argument)

    if parameter != "none":
        register_filters()

    markup = InlineKeyboardBuilder()
    markup.button(text="Назад", callback_data=Callback_Data(key="order_history", value=""))
    for parameter in dir(filters):
        if not parameter.startswith("__"):
            for argument in getattr(filters, parameter):
                if argument in getattr(data, parameter):
                    text = f"✅ {argument}"
                else:
                    text = f"{argument}"
                markup.button(text=text, callback_data=Callback_Data(key=f"order_history_filters", value=f"{parameter}_{argument}"))
    markup.adjust(1, 2)

    await callback.message.edit_caption(caption=content.text_orders_filters, reply_markup=markup.as_markup())

    users_list[callback.message.chat.id].config.order_history_filters = data

    db_connection.sql_UPDATE('public."Users"', "chat_id", callback.message.chat.id, ["config"], *[users_list[callback.message.chat.id].config.instance_to_json()])
































async def main():
    await dp.start_polling(bot)

asyncio.run(main())


