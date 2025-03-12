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

bot = Bot(token=config.token_mainbot)
reshalbot = Bot(token=config.token_reshalbot)
dp = Dispatcher()

users_list, = functions.import_lists_from_db(["users_list"])


#   СТАРТ
@dp.message(CommandStart())
async def start(message: Message):
    bg_photo_id = users_list[message.chat.id].other_data.bg_photo_id if message.chat.id in list(users_list.keys()) else classes.OtherData.bg_photo_id

    markup = InlineKeyboardBuilder()
    markup.button(text="1 курс", callback_data=Callback_Data(key="year_confirmation", value="1"))
    markup.button(text="2 курс", callback_data=Callback_Data(key="year_confirmation", value="2"))

    await message.delete()
    await message.answer_photo(bg_photo_id, content.text_start(message.from_user.first_name), reply_markup=markup.as_markup())

    functions.register_user(message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, users_list)

@dp.callback_query(Callback_Data.filter(F.key == "year_confirmation"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    year = callback_data.value
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
    markup.button(text="🛠️ Услуги", callback_data=Callback_Data(key=f"subjects", value=""))
    #markup.button(text="Полезные материалы", callback_data=Callback_Data(key=f"useful_subjects", value=""))
    markup.button(text="📡 Помощь", callback_data=Callback_Data(key="help", value=""))
    markup.button(text="🌚 О нас", callback_data=Callback_Data(key="about_us", value=""))
    markup.button(text="📋 История заказов", callback_data=Callback_Data(key="order_history", value=""))
    markup.button(text="⚙️ Настройки", callback_data=Callback_Data(key="settings", value=""))
    markup.adjust(1, 2, 1, 1)

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
    markup.button(text="🖼️ Изменить фон сообщения", callback_data=Callback_Data(key="background", value=""))
    markup.button(text="🔄 Изменить курс обучения", callback_data=Callback_Data(key="start", value=""))
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="main", value=""))
    markup.adjust(1, 1, 1)

    await callback.message.edit_caption(caption="Выберите нужную вам настройку.", reply_markup=markup.as_markup())


    #   НАСТРОЙКИ >>> ОТПРАВИТЬ ФОТО
@dp.callback_query(Callback_Data.filter(F.key == "background"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="❌ Отмена", callback_data=Callback_Data(key="settings", value=""))

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
    orders_list, = functions.import_lists_from_db(["orders_list"])

    markup = InlineKeyboardBuilder()
    markup.button(text="🔄 Настроить фильтры", callback_data=Callback_Data(key="order_history_filters", value="none_none"))
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="main", value=""))

    sorted_data = db_connection.sql_SELECT('public."Sorted_Data"', "object", "orders", ["data"])[0][0]

    for order_id in sorted_data["chat_id"][str(callback.message.chat.id)]:
        if orders_list[order_id].work in users_list[callback.message.chat.id].config.order_history_filters.work:
            text = f"Заказ № {order_id}"
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
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="order_history", value=""))
    for parameter in dir(filters):
        if not parameter.startswith("__"):
            for argument in getattr(filters, parameter):
                if argument in getattr(data, parameter):
                    argument_name = content.dictionary[argument]
                    text = f"✅ {argument_name}"
                else:
                    argument_name = content.dictionary[argument]
                    text = f"{argument_name}"
                markup.button(text=text, callback_data=Callback_Data(key=f"order_history_filters", value=f"{parameter}_{argument}"))
    markup.adjust(1, 2)

    await callback.message.edit_caption(caption=content.text_orders_filters, reply_markup=markup.as_markup())

    users_list[callback.message.chat.id].config.order_history_filters = data

    db_connection.sql_UPDATE('public."Users"', "chat_id", callback.message.chat.id, ["config"], *[users_list[callback.message.chat.id].config.instance_to_json()])


@dp.callback_query(Callback_Data.filter(F.key == "order"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    orders_list, = functions.import_lists_from_db(["orders_list"])
    order_id = int(callback_data.value)
    chat_id, username, year, subject_name, work, work_name, work_id, work_id_name, specific_data, price = functions.retrieve_from_instance(
        orders_list[order_id],
        ["chat_id", "username", "year", "subject_name", "work", "work_name", "work_id", "work_id_name", "specific_data", "price"])
    markup = InlineKeyboardBuilder()
    text, markup, file_path = functions.order_info_user(order_id, chat_id, year, subject_name, work, work_name, work_id,
                                                        work_id_name, specific_data, price, markup)
    markup.adjust(1)

    if file_path == None:
        await callback.message.answer(text=text, reply_markup=markup.as_markup(), parse_mode="html")
    else:
        await callback.message.answer_document(FSInputFile(file_path), caption=text,
                                               reply_markup=markup.as_markup(), parse_mode="html")

    #   ПРЕДМЕТЫ
@dp.callback_query(Callback_Data.filter(F.key == "subjects"))
async def callback(callback: CallbackQuery):
    year = users_list[callback.message.chat.id].year
    main_registry_list, active_registry_list = functions.import_lists_from_db(["main_registry_list", "active_registry_list"])

    markup = InlineKeyboardBuilder()

    if year in list(active_registry_list.keys()):
        for subject in list(active_registry_list[year].keys()):
            button_text = main_registry_list[year][subject]["subject_name"]
            markup.button(text=button_text, callback_data=Callback_Data(key="services", value=f"{subject}"))
        markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="main", value="")); markup.adjust(1)
        await callback.message.edit_caption(caption=content.text_subject, reply_markup=markup.as_markup())
    else:
        markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="main", value="")); markup.adjust(1)
        await callback.message.edit_caption(caption=content.text_subject_exception, reply_markup=markup.as_markup())

    #   ПРЕДМЕТЫ >>> УСЛУГИ
@dp.callback_query(Callback_Data.filter(F.key=="services"))
async def callback(callback: CallbackQuery, callback_data=Callback_Data):
    subject = callback_data.value
    year = users_list[callback.message.chat.id].year
    main_registry_list, active_registry_list = functions.import_lists_from_db(["main_registry_list", "active_registry_list"])

    markup = InlineKeyboardBuilder()
    text = "📌 Актуальные цены:\n\n"
    for work in list(active_registry_list[year][subject].keys()):
        work_name = main_registry_list[year][subject]["work"][work]["work_name"]
        if active_registry_list[year][subject][work] != {}:
            price_lab = []
            for work_id in list(active_registry_list[year][subject][work].keys()):
                price_lab.append(main_registry_list[year][subject]["work"][work]["work_id"][work_id]["price"])
            min_price = min(price_lab)
            max_price = max(price_lab)
            if min_price == max_price:
                text += f"✅ {work_name}     <b><em>{min_price} р.</em></b>\n\n"
            else:
                text += f"✅ {work_name}     <b><em>{min_price}-{max_price} р.</em></b>\n\n"
            markup.button(text=work_name, callback_data=Callback_Data(key="work_ids", value=f"{subject}_{work}"))

    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="subjects", value="")); markup.adjust(1)
    text += "\n❗ Чтобы начать оформление, выберите нужную услугу."

    await callback.message.edit_caption(caption=text, reply_markup=markup.as_markup(), parse_mode="HTML")

@dp.callback_query(Callback_Data.filter(F.key=="work_ids"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    year = users_list[callback.message.chat.id].year
    subject = callback_data.value.split("_")[0]
    work = callback_data.value.split("_")[1]
    main_registry_list, active_registry_list = functions.import_lists_from_db(["main_registry_list", "active_registry_list"])

    markup = InlineKeyboardBuilder()
    text = "📌 Актуальные цены:\n\n"
    for work_id in list(active_registry_list[year][subject][work].keys()):
        work_id_name = main_registry_list[year][subject]["work"][work]["work_id"][work_id]["work_id_name"]
        price = main_registry_list[year][subject]["work"][work]["work_id"][work_id]["price"]
        text += f"✅ {work_id}. {work_id_name}     <b><em>{price} р.</em></b>\n\n"
        button_text = f"{work_id}. {work_id_name}"
        markup.button(text=button_text, callback_data=Callback_Data(key=f"order_{work}", value=f"{subject}_{work_id}"))

    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="services", value=f"{subject}")); markup.adjust(1)
    text += "\n❗ Чтобы начать оформление, выберите нужную услугу."

    await callback.message.edit_caption(caption=text, reply_markup=markup.as_markup(), parse_mode="HTML")

    #   ПРЕДМЕТЫ >>> УСЛУГИ >>> ТЕСТ СДО
        #   ИНФО
@dp.callback_query(Callback_Data.filter(F.key=="order_sdo"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    subject = callback_data.value.split("_")[0]
    work_id = callback_data.value.split("_")[1]

    markup = InlineKeyboardBuilder()

    markup.button(text="➡️ Ввести персональные данные", callback_data=Callback_Data(key=f"order_sdo_1-1", value=f"{subject}_{work_id}"))
    markup.button(text="➡️ Перейти к оформлению", callback_data=Callback_Data(key=f"order_sdo_1-3", value=f"{subject}_{work_id}"))
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="services", value=f"{subject}")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_order_SDO, reply_markup=markup.as_markup())

        #   ПЕРЕЙТИ К ОФОРМЛЕНИЮ
@dp.callback_query(Callback_Data.filter(F.key=="order_sdo_1-1"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    subject = callback_data.value.split("_")[0]
    work_id = callback_data.value.split("_")[1]

    markup = InlineKeyboardBuilder()
    markup.button(text="СДО", callback_data=Callback_Data(key="order_sdo_1-2", value="СДО"))
    markup.button(text="ИСУ", callback_data=Callback_Data(key="order_sdo_1-2", value="ИСУ"))
    markup.button(text="❌ Отмена", callback_data=Callback_Data(key=f"order_sdo", value=f"{subject}_{work_id}")); markup.adjust(2, 1)

    await callback.message.edit_caption(caption=content.text_order_SDO_1_1, reply_markup=markup.as_markup())

    functions.register_temporary_data(callback.message.chat.id, [subject, work_id], [0, 1], users_list)

        #   ВЫБОР ПЛАТФОРМЫ
@dp.callback_query(Callback_Data.filter(F.key=="order_sdo_1-2"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    platform = callback_data.value
    subject = users_list[callback.message.chat.id].other_data.temporary_data[0]
    work_id = users_list[callback.message.chat.id].other_data.temporary_data[1]

    markup = InlineKeyboardBuilder()
    markup.button(text="✅ Далее", callback_data=Callback_Data(key=f"order_sdo_2", value=""))
    markup.button(text="🔄 Изменить", callback_data=Callback_Data(key=f"order_sdo_1-1", value=f"{subject}_{work_id}"))
    markup.button(text="❌ Отмена", callback_data=Callback_Data(key=f"order_sdo", value=f"{subject}_{work_id}")); markup.adjust(2, 1)

    await callback.message.edit_caption(caption=content.text_order_SDO_1_2(platform), reply_markup=markup.as_markup())

    functions.register_temporary_data(callback.message.chat.id, [platform], [2], users_list)


    #   ВВЕСТИ ЛОГИН, ПАРОЛЬ
@dp.callback_query(Callback_Data.filter(F.key == "order_sdo_2"))
async def callback(callback: CallbackQuery, state: FSMContext):
    platform = users_list[callback.message.chat.id].other_data.temporary_data[2]

    await state.set_state(classes.Form.login)
    await callback.message.edit_caption(caption=content.text_order_SDO_2_1(platform))

@dp.message(classes.Form.login)
async def message(message: Message, state: FSMContext):
    platform = users_list[message.chat.id].other_data.temporary_data[2]

    message_id = users_list[message.chat.id].other_data.message_id

    await state.update_data(login=message.text)
    await state.set_state(classes.Form.password)
    await message.delete()
    await bot.edit_message_caption(caption=content.text_order_SDO_2_2(platform), chat_id=message.chat.id, message_id=message_id)

    functions.register_temporary_data(message.chat.id, [message.text], [3], users_list)

@dp.message(classes.Form.password)
async def message(message: Message, state: FSMContext):
    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])
    message_id = users_list[message.chat.id].other_data.message_id
    year = users_list[message.chat.id].year
    subject, work_id, platform, login = functions.retrieve_temporary_data(message.chat.id, [0, 1, 2, 3], users_list)
    subject_name = main_registry_list[year][subject]["subject_name"]
    work_id_name = main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["work_id_name"]
    price = main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["price"]
    password = message.text

    markup = InlineKeyboardBuilder()
    markup.button(text="✅ Сформировать заказ", callback_data=Callback_Data(key=f"order_sdo_3", value=""))
    markup.button(text="🔄 Изменить", callback_data=Callback_Data(key=f"order_sdo_1-1", value=f"{subject}_{work_id}"))
    markup.button(text="❌ Отмена", callback_data=Callback_Data(key=f"order_sdo", value=f"{subject}_{work_id}")); markup.adjust(1, 2)

    await state.update_data(login=message.text)
    await state.set_state(classes.Form.password)
    await message.delete()
    await bot.edit_message_caption(caption=content.text_order_SDO_2_3(year, subject_name, work_id, work_id_name, platform, login, password, price), chat_id=message.chat.id, message_id=message_id, reply_markup=markup.as_markup(), parse_mode="html")

    functions.register_temporary_data(message.chat.id, [message.text], [4], users_list)

@dp.callback_query(Callback_Data.filter(F.key=="order_sdo_1-3"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])
    year = users_list[callback.message.chat.id].year
    subject, work_id = callback_data.value.split("_")[0], callback_data.value.split("_")[1]
    platform, login, password = None, None, None
    subject_name = main_registry_list[year][subject]["subject_name"]
    work_id_name = main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["work_id_name"]
    price = main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["price"]

    markup = InlineKeyboardBuilder()
    markup.button(text="✅ Сформировать заказ", callback_data=Callback_Data(key=f"order_sdo_3", value=""))
    markup.button(text="❌ Отмена", callback_data=Callback_Data(key=f"order_sdo", value=f"{subject}_{work_id}"))
    markup.adjust(1, 2)

    await callback.message.edit_caption(caption=content.text_order_SDO_2_3(year, subject_name, work_id, work_id_name, platform, login, password,
                                           price), reply_markup=markup.as_markup(), parse_mode="html")

    functions.register_temporary_data(callback.message.chat.id, [subject, work_id, platform, login, password], [0, 1, 2, 3, 4], users_list)

    #   ✅ СФОРМИРОВАТЬ ЗАКАЗ
@dp.callback_query(Callback_Data.filter(F.key == "order_sdo_3"))
async def callback(callback: CallbackQuery):
    main_registry_list, active_registry_list = functions.import_lists_from_db(["main_registry_list", "active_registry_list"])
    chat_id = callback.message.chat.id
    username, year = functions.retrieve_from_instance(users_list[chat_id], ["username", "year"])
    subject, work_id, platform, login, password = functions.retrieve_temporary_data(chat_id, [0, 1, 2, 3, 4], users_list)
    subject_name = main_registry_list[year][subject]["subject_name"]
    work, work_name = "sdo", main_registry_list[year][subject]["work"]["sdo"]["work_name"]
    work_id_name = main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["work_id_name"]
    price = main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["price"]
    executor_chat_id = main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["executors"][0]
    main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["executors"].pop(0)
    main_registry_list[year][subject]["work"]["sdo"]["work_id"][work_id]["executors"].append(executor_chat_id)
    executor_username = db_connection.sql_SELECT('public."Executors"', "chat_id", executor_chat_id, ["username", ])[0][0]

    con, cur = functions.connection()
    specific_data = {}
    functions.import_in_object(specific_data, ["platform", "login", "password", "file_path"], [platform, login, password, None])

    cur.execute('INSERT INTO public."Orders" (chat_id, username, year, subject, subject_name, work, work_name, work_id, work_id_name, specific_data, price, executor_chat_id, executor_username)'
    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(chat_id, username, year, subject, subject_name, work, work_name, work_id, work_id_name, json.dumps(specific_data), price, executor_chat_id, executor_username))
    cur.execute('SELECT order_id FROM public."Orders" ORDER BY order_id DESC LIMIT 1;')
    order_id = cur.fetchall()[0][0]
    cur.execute('SELECT data FROM public."Sorted_Data" WHERE object = %s', ("orders",))
    sorted_data = cur.fetchall()[0][0]
    sorted_data["chat_id"][str(chat_id)].append(order_id)
    sorted_data["work"]["sdo"].append(order_id)
    sorted_data["executor_chat_id"][str(executor_chat_id)].append(order_id)
    cur.execute('UPDATE public."Sorted_Data" SET data = %s WHERE object = %s', (json.dumps(sorted_data), "orders"))
    cur.execute('UPDATE public."Registry_Data" SET data = %s WHERE registry_name = %s', (json.dumps(main_registry_list), "main_registry"))
    con.commit(); con.close()

    markup = InlineKeyboardBuilder()
    markup.button(text="💬 Связаться с исполнителем", url=f"https://t.me/{executor_username}")
    markup.button(text="🏠 На главную", callback_data=Callback_Data(key="main", value="")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_order_SDO_3(order_id, chat_id, year, subject_name, work_id, work_id_name, platform, login, password, price), reply_markup=markup.as_markup(), parse_mode="html")


#   ЛАБОРАТОРНЫЕ РАБОТЫ

    #   ИНФО
@dp.callback_query(Callback_Data.filter(F.key=="order_lab"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):

    subject = callback_data.value.split("_")[0]
    work_id = callback_data.value.split("_")[1]

    markup = InlineKeyboardBuilder()
    markup.button(text="➡️ Перейти к оформлению", callback_data=Callback_Data(key="order_lab_1", value=f"{subject}_{work_id}"))
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key="lab_ids", value=f"{subject}_lab")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_order_lab, reply_markup=markup.as_markup())


@dp.callback_query(Callback_Data.filter(F.key=="order_lab_1"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):

    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])
    subject = callback_data.value.split("_")[0]
    work_id = callback_data.value.split("_")[1]
    year = users_list[callback.message.chat.id].year
    url = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["manual_link"]

    markup = InlineKeyboardBuilder()
    markup.button(text="📖 Посмотреть", url=url)
    markup.button(text="➡️ Далее", callback_data=Callback_Data(key="order_lab_2", value=""))
    markup.button(text="📦 Добавить архив", callback_data=Callback_Data(key="order_lab_1-1", value=""))
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key=f"order_lab", value=f"{subject}_{work_id}")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_order_lab_1, reply_markup=markup.as_markup())

    users_list[callback.message.chat.id].other_data.temporary_data = []
    functions.register_temporary_data(callback.message.chat.id, [subject, work_id], [0, 1], users_list)

@dp.callback_query(Callback_Data.filter(F.key == "order_lab_1-1"))
async def callback(callback: CallbackQuery, state: FSMContext):

    subject, work_id = functions.retrieve_temporary_data(callback.message.chat.id, [0, 1], users_list)

    markup = InlineKeyboardBuilder()
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key=f"order_lab_1", value=f"{subject}_{work_id}"))

    await state.set_state(classes.Form.manual_file)
    await callback.message.edit_caption(caption=content.text_order_lab_1_1, reply_markup=markup.as_markup())

@dp.message(classes.Form.manual_file, F.document)
async def message(message: Message, state: FSMContext):

    subject, work_id = functions.retrieve_temporary_data(message.chat.id, [0, 1], users_list)
    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])
    message_id = users_list[message.chat.id].other_data.message_id
    manual_file_id = message.document.file_id
    manual_file_name = message.document.file_name
    year = users_list[message.chat.id].year
    url = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["manual_link"]

    markup = InlineKeyboardBuilder()
    markup.button(text="📖 Посмотреть", url=url)
    markup.button(text="➡️ Далее", callback_data=Callback_Data(key=f"order_lab_2", value=""))
    markup.button(text="🗑️ Удалить архив", callback_data=Callback_Data(key=f"order_lab_1", value=f"{subject}_{work_id}"))
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key=f"order_lab", value=f"{subject}_{work_id}")); markup.adjust(1)

    await message.delete()
    await bot.edit_message_caption(caption=content.text_order_lab_1_(manual_file_name), chat_id=message.chat.id, message_id=message_id, reply_markup=markup.as_markup())

    functions.register_temporary_data(message.chat.id, [manual_file_id, manual_file_name], [2, 3], users_list)


@dp.callback_query(Callback_Data.filter(F.key == "order_lab_2"))
async def callback(callback: CallbackQuery, state: FSMContext):
    subject, work_id = functions.retrieve_temporary_data(callback.message.chat.id, [0, 1], users_list)

    markup = InlineKeyboardBuilder()
    markup.button(text="⬅️ Назад", callback_data=Callback_Data(key=f"order_lab_1", value=f"{subject}_{work_id}"))

    await state.set_state(classes.Form.additional_info)
    await callback.message.edit_caption(caption=content.text_order_lab_2_1, reply_markup=markup.as_markup())

@dp.message(classes.Form.additional_info, F.text)
async def message(message: Message, state: FSMContext):
    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])
    additional_info = message.text
    message_id = users_list[message.chat.id].other_data.message_id
    year = users_list[message.chat.id].year
    subject, work_id = functions.retrieve_temporary_data(message.chat.id, [0, 1], users_list)
    subject_name = main_registry_list[year][subject]["subject_name"]
    work_id_name = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["work_id_name"]
    price = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["price"]

    if len(users_list[message.chat.id].other_data.temporary_data) == 4:
        manual_file_id, manual_file_name = functions.retrieve_temporary_data(message.chat.id, [2, 3], users_list)
        functions.register_temporary_data(message.chat.id, [additional_info], [4], users_list)
    else:
        manual_file_name = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["manual_link"]
        functions.register_temporary_data(message.chat.id, [additional_info], [2], users_list)

    markup = InlineKeyboardBuilder()
    markup.button(text="✅ Сформировать заказ", callback_data=Callback_Data(key="order_lab_3", value=""))
    markup.button(text="🔄 Изменить", callback_data=Callback_Data(key=f"order_lab_1", value=f"{subject}_{work_id}"))
    markup.button(text="❌ Отмена", callback_data=Callback_Data(key=f"order_lab=", value=f"{subject}_{work_id}")); markup.adjust(1, 2)

    await message.delete()
    await bot.edit_message_caption(caption=content.text_order_lab_2_2(year, subject_name, work_id_name, manual_file_name, additional_info, price), chat_id=message.chat.id, message_id=message_id, reply_markup=markup.as_markup(), parse_mode="html")


    #   ✅ СФОРМИРОВАТЬ ЗАКАЗ
@dp.callback_query(Callback_Data.filter(F.key == "order_lab_3"))
async def call(callback: CallbackQuery):
    main_registry_list, active_registry_list = functions.import_lists_from_db(["main_registry_list", "active_registry_list"])
    chat_id = callback.message.chat.id
    username, year = functions.retrieve_from_instance(users_list[chat_id], ["username", "year"])
    subject, work_id = functions.retrieve_temporary_data(chat_id, [0, 1], users_list)
    subject_name = main_registry_list[year][subject]["subject_name"]
    work, work_name = "lab", main_registry_list[year][subject]["work"]["lab"]["work_name"]
    work_id_name = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["work_id_name"]
    price = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["price"]
    executor_chat_id = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["executors"][0]
    main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["executors"].pop(0)
    main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["executors"].append(executor_chat_id)
    executor_username = db_connection.sql_SELECT('public."Executors"', "chat_id", executor_chat_id, ["username",])[0][0]


    if len(users_list[callback.message.chat.id].other_data.temporary_data) == 5:
        manual_file_id, manual_file_name = functions.retrieve_temporary_data(chat_id, [2, 3], users_list)
        manual_file = await bot.get_file(manual_file_id)

        manual_file_path = f"..\\storage\\documents\\Лабораторные работы\\Методички\\{manual_file_name}"
        #base_dir = os.path.dirname(os.path.abspath(__file__))
        #storage_dir = os.path.join(base_dir, '..', 'storage', 'documents', 'Лабораторные работы', 'Методички')
        #os.makedirs(storage_dir, exist_ok=True)
        #manual_file_path = os.path.join(storage_dir, manual_file_name)
        await bot.download_file(manual_file.file_path, manual_file_path)

        additional_info, = functions.retrieve_temporary_data(chat_id, [4], users_list)
    else:
        manual_file_path = None
        manual_file_name = main_registry_list[year][subject]["work"]["lab"]["work_id"][work_id]["manual_link"]
        additional_info, = functions.retrieve_temporary_data(chat_id, [2], users_list)

    con, cur = functions.connection()
    specific_info = {}
    functions.import_in_object(specific_info, ["manual_file_path", "manual_file_name", "additional_info", "file_path"],
                             [manual_file_path, manual_file_name, additional_info, None])

    cur.execute('INSERT INTO public."Orders" (chat_id, username, year, subject, subject_name, work, work_name, work_id, work_id_name, specific_data, price, executor_chat_id, executor_username)'
    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(chat_id, username, year, subject, subject_name, work, work_name, work_id, work_id_name, json.dumps(specific_info), price, executor_chat_id, executor_username))
    cur.execute('SELECT order_id FROM public."Orders" ORDER BY order_id DESC LIMIT 1;')
    order_id = cur.fetchall()[0][0]
    cur.execute(f'SELECT data FROM public."Sorted_Data" WHERE object = %s', ("orders",))
    sorted_data = cur.fetchall()[0][0]
    sorted_data["chat_id"][str(chat_id)].append(order_id)
    sorted_data["executor_chat_id"][str(executor_chat_id)].append(order_id)
    sorted_data["work"]["lab"].append(order_id)
    cur.execute('UPDATE public."Sorted_Data" SET data = %s WHERE object = %s', (json.dumps(sorted_data), "orders"))
    cur.execute('UPDATE public."Registry_Data" SET data = %s WHERE registry_name = %s', (json.dumps(main_registry_list), "main_registry"))
    con.commit(); con.close()

    markup = InlineKeyboardBuilder()
    markup.button(text="💬 Связаться с исполнителем", url=f"https://t.me/{executor_username}")
    markup.button(text="🏠 На главную", callback_data=Callback_Data(key="main", value="")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_order_lab_3(order_id, chat_id, year, subject_name, work_id, work_id_name, manual_file_name, price), reply_markup=markup.as_markup(), parse_mode="html")

@dp.message(Command("user"))
async def user_profile(message):
    await bot.send_message(message.chat.id, f"chat_id: {message.chat.id}\nusername: {message.from_user.username}\n"
                                      f"first_name: {message.from_user.first_name}\nlast_name: {message.from_user.last_name}")

@dp.callback_query(Callback_Data.filter(F.key == "delete"))
async def callback_data(callback: CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)




















async def main():
    await dp.start_polling(bot)

asyncio.run(main())


