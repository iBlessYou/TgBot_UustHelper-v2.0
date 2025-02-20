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

executors_list, = functions.import_lists_from_db(["executors_list"])

# СТАРТ
@dp.message(CommandStart())
async def start(message: Message):
    if message.chat.id not in config.chat_id_access_list:

        await message.delete()
        await message.answer(content.text_not_access)

    else:
        bg_photo_id = executors_list[message.chat.id].other_data.bg_photo_id if message.chat.id in list(executors_list.keys()) else classes.OtherData.bg_photo_id

        markup = InlineKeyboardBuilder()
        markup.button(text="Заказы", callback_data=Callback_Data(key="orders", value=""))
        markup.button(text="Услуги", callback_data=Callback_Data(key="services", value=""))
        markup.button(text="История заказов", callback_data=Callback_Data(key="order_history", value=""))
        markup.adjust(1)

        await message.delete()
        await message.answer_photo(bg_photo_id, caption=content.text_main, reply_markup=markup.as_markup())

        functions.register_executor(message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, executors_list)


    #   ГЛАВНОЕ МЕНЮ
@dp.callback_query(Callback_Data.filter(F.key == "main"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Заказы", callback_data=Callback_Data(key="orders", value=""))
    markup.button(text="Услуги", callback_data=Callback_Data(key="services", value=""))
    markup.button(text="История заказов", callback_data=Callback_Data(key="order_history", value="")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_main, reply_markup=markup.as_markup())

    #   ЗАКАЗЫ
@dp.callback_query(Callback_Data.filter(F.key == "orders"))
async def callback(callback: CallbackQuery):
    markup = InlineKeyboardBuilder()
    if callback.message.chat.id in config.chat_id_access_list:
        markup.button(text="Все заказы", callback_data=Callback_Data(key="orders=all", value=""))
    markup.button(text="Выборочные заказы", callback_data=Callback_Data(key="orders=selective", value=""))
    markup.button(text="Назад", callback_data=Callback_Data(key="main", value="")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_main, reply_markup=markup.as_markup())


    #   ЗАКАЗЫ >>> ВСЕ ЗАКАЗЫ
@dp.callback_query(Callback_Data.filter(F.key == "orders=all"))
async def callback(callback: CallbackQuery):
    markup = InlineKeyboardBuilder()
    markup.button(text="Настроить фильтры", callback_data=Callback_Data(key="order_filters", value="none_none"))
    markup.button(text="Назад", callback_data=Callback_Data(key="orders", value=""))

    sorted_data = db_connection.sql_SELECT('public."Sorted_Data"', "object", "orders", ["data",])[0][0]

    for status in executors_list[callback.message.chat.id].config.order_filters.status:
        for work in executors_list[callback.message.chat.id].config.order_filters.work:
            data = list(set(sorted_data["status"][status]) & set(sorted_data["work"][work]))
            for order_id in data:
                mark = functions.status_mark(status)
                text = f"{mark} Заказ № {order_id}"
                markup.button(text=text, callback_data=Callback_Data(key="order", value=f"{order_id}"))

    markup.adjust(1)
    await callback.message.edit_caption(caption=content.text_orders_all, reply_markup=markup.as_markup())


    #   ЗАКАЗЫ >>> ВСЕ ЗАКАЗЫ >>> ФИЛЬТРЫ
@dp.callback_query(Callback_Data.filter(F.key == "order_filters"))
async def callback(callback: CallbackQuery, callback_data=Callback_Data):
    filters = classes.OrderFilters()
    parameter = callback_data.value.split("_")[0]
    argument = callback_data.value.split("_")[1]
    data = executors_list[callback.message.chat.id].config.order_filters

    def register_filters():
        if argument in getattr(data, parameter):
            getattr(data, parameter).remove(argument)
        elif argument not in getattr(data, parameter):
            getattr(data, parameter).append(argument)

    if parameter != "none":
        register_filters()

    markup = InlineKeyboardBuilder()
    markup.button(text="Назад", callback_data=Callback_Data(key="orders=all", value=""))
    for parameter in dir(filters):
        if not parameter.startswith("__"):
            for argument in getattr(filters, parameter):
                if argument in getattr(data, parameter):
                    text = f"✅ {argument}"
                else:
                    text = f"{argument}"
                markup.button(text=text, callback_data=Callback_Data(key=f"order_filters", value=f"{parameter}_{argument}"))
    markup.adjust(1, 2)

    await callback.message.edit_caption(caption=content.text_orders_filters, reply_markup=markup.as_markup())

    executors_list[callback.message.chat.id].config.order_filters = data

    db_connection.sql_UPDATE('public."Executors"', "chat_id", callback.message.chat.id, ["config"],
                             *[executors_list[callback.message.chat.id].config.instance_to_json()])




    #   ЗАКАЗ
@dp.callback_query(Callback_Data.filter(F.key == "order"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    orders_list, = functions.import_lists_from_db(["orders_list"])
    order_id = int(callback_data.value)

    chat_id, username, year, subject_name, work, work_name, work_id_name, specific_data, status = functions.retrieve_from_instance(
        orders_list[order_id],["chat_id", "username", "year", "subject_name", "work", "work_name", "work_id_name", "specific_data", "status"])
    markup = InlineKeyboardBuilder()
    text, markup, file_path = functions.order_info(order_id, chat_id, username, year, subject_name, work, work_name, work_id_name, specific_data, status, markup, callback.message.chat.id)
    markup.adjust(1)
    if file_path == None:
        await callback.message.answer(text, reply_markup=markup.as_markup(), parse_mode="html")
    else:
        await callback.message.answer_document(FSInputFile(file_path), caption=text, reply_markup=markup.as_markup(), parse_mode="html")

    #   ЗАКАЗ по ручному запросу
@dp.message(F.text.startswith("o"))
async def message(message: Message):
    orders_dict, = functions.import_lists_from_db(["orders_dict"])
    order_id = int(message.text.split("c")[0][1:])

    if order_id not in list(orders_dict.keys()):
        markup = InlineKeyboardBuilder()
        markup.button(text="Скрыть", callback_data=Callback_Data(key="delete", value=""))
        await message.delete()
        await message.answer("Данного заказа не существует", reply_markup=markup.as_markup())

    else:
        chat_id, username, year, subject_name, work, work_name, work_id_name, specific_data, status = functions.retrieve_from_instance(
            orders_dict[order_id],["chat_id", "username", "year", "subject_name", "work", "work_name", "work_id_name", "specific_data", "status"])
        markup = InlineKeyboardBuilder()
        text, markup, file_path = functions.order_info(order_id, chat_id, username, year, subject_name, work, work_name, work_id_name, specific_data, status, markup, message.chat.id)
        markup.adjust(1)
        if file_path == None:
            await message.answer(text, reply_markup=markup.as_markup(), parse_mode="html")
        else:
            await message.answer_document(FSInputFile(file_path), caption=text, reply_markup=markup.as_markup(), parse_mode="html")
        await message.delete()

        #   ИСТОРИЯ ЗАКАЗОВ

@dp.callback_query(Callback_Data.filter(F.key == "order_history"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Настроить фильтры", callback_data=Callback_Data(key="order_history_filters", value="none_none"))
    markup.button(text="Назад", callback_data=Callback_Data(key="main", value=""))

    sorted_data = db_connection.sql_SELECT('public."Sorted_Data"', "object", "orders", ["data"])[0][0]

    for status in executors_list[callback.message.chat.id].config.order_history_filters.status:
        for work in executors_list[callback.message.chat.id].config.order_history_filters.work:
            data = list(set(sorted_data["executor_chat_id"][str(callback.message.chat.id)]) & set(sorted_data["status"][status]) & set(sorted_data["work"][work]))
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
    data = executors_list[callback.message.chat.id].config.order_history_filters

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

    executors_list[callback.message.chat.id].config.order_history_filters = data

    db_connection.sql_UPDATE('public."Executors"', "chat_id", callback.message.chat.id, ["config"],
                             *[executors_list[callback.message.chat.id].config.instance_to_json()])


    #   УСЛУГИ
@dp.callback_query(Callback_Data.filter(F.key == "services"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Выбрать услуги", callback_data=Callback_Data(key="select_services_year", value=""))
    markup.button(text="Посмотреть мои услуги", callback_data=Callback_Data(key=f"services_form_view", value=""))
    markup.button(text="Назад", callback_data=Callback_Data(key="main", value=""))
    markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_services, reply_markup=markup.as_markup())

    #   ЗАПРОС (ВЫБРАТЬ УСЛУГИ) >>> КУРС
@dp.callback_query(Callback_Data.filter(F.key == "select_services_year"))
async def callback(callback: CallbackQuery):

    markup = InlineKeyboardBuilder()
    markup.button(text="Курс 1", callback_data=Callback_Data(key="select_services_subject", value="1"))
    markup.button(text="Курс 2", callback_data=Callback_Data(key="select_services_subject", value="2"))
    markup.button(text="Назад", callback_data=Callback_Data(key="services", value="")); markup.adjust(2, 1)

    await callback.message.edit_caption(caption=content.text_select_services_year, reply_markup=markup.as_markup())


    #   ЗАПРОС (ВЫБРАТЬ УСЛУГИ) >>> КУРС >>> ПРЕДМЕТ
@dp.callback_query(Callback_Data.filter(F.key == "select_services_subject"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    year = callback_data.value
    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])

    markup = InlineKeyboardBuilder()
    try:
        for subject_id in main_registry_list[year].keys():
            button_text = main_registry_list[year][subject_id]["subject_name"]
            markup.button(text=button_text, callback_data=Callback_Data(key="select_services_work", value=f"{subject_id}_{year}_none"))

    except Exception:
        markup.button(text="Назад", callback_data=Callback_Data(key="select_services_year", value=""))

        await callback.message.edit_caption(caption="На данном курсе пока нет предметов", reply_markup=markup.as_markup())
    else:
        markup.button(text="Назад", callback_data=Callback_Data(key="select_services_year", value=""))
        markup.adjust(1)
        await callback.message.edit_caption(caption=content.text_select_services_subject, reply_markup=markup.as_markup())


    #   ЗАПРОС (ВЫБРАТЬ УСЛУГИ) >>> КУРС >>> ПРЕДМЕТ >>> РАБОТА
@dp.callback_query(Callback_Data.filter(F.key == "select_services_work"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    year = callback_data.value.split("_")[1]
    subject = callback_data.value.split("_")[0]
    chat_id = callback.message.chat.id
    work = callback_data.value.split("_")[2]

    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])
    data = executors_list[chat_id].config.selected_services

    def select_work_callback():

            functions.check_keys(data.current, [year, subject])
            if work in list(data.current[year][subject].keys()):

                del data.current[year][subject][work]
                functions.delete_keys(data.current, [year, subject])

                if work not in list(data.append.get(year, {}).get(subject, {}).keys()):
                    functions.check_keys(data.remove, [year, subject])
                    data.remove[year][subject][work] = {}

                if work in list(data.append.get(year, {}).get(subject, {}).keys()):
                    del data.append[year][subject][work]
                    functions.delete_keys(data.append, [year, subject])

            else:
                data.current[year][subject][work] = {}

                if work not in list(data.remove.get(year, {}).get(subject, {}).keys()):
                    functions.check_keys(data.append, [year, subject])
                    data.append[year][subject][work] = {}

                if work in list(data.remove.get(year, {}).get(subject, {}).keys()):
                    del data.remove[year][subject][work]
                    functions.delete_keys(data.remove, [year, subject])

    if work != "none":
        select_work_callback()

    markup = InlineKeyboardBuilder()

    work_list = list(main_registry_list[year][subject]["work"].keys())
    for work in work_list:
        button_text = main_registry_list[year][subject]["work"][work]["work_name"]
        if data.current.get(year, {}).get(subject, {}).get(work) == {}:
                button_text = f"✅ {button_text}"
        if main_registry_list[year][subject]["work"][work].get("work_id"):
            markup.button(text=button_text, callback_data=Callback_Data(key="select_services_lab", value=f"{subject}_{year}_{work}_none"))
        else:
            markup.button(text=button_text, callback_data=Callback_Data(key="select_services_work", value=f"{subject}_{year}_{work}"))
    markup.button(text="Назад", callback_data=Callback_Data(key="select_services_subject", value=f"{year}")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_select_services_work, reply_markup=markup.as_markup())

    executors_list[chat_id].config.selected_services = data
    db_connection.sql_UPDATE('public."Executors"', "chat_id", chat_id, ["config"], *[executors_list[callback.message.chat.id].config.instance_to_json()])


    #   ЗАПРОС (ВЫБРАТЬ УСЛУГИ) >>> КУРС >>> ПРЕДМЕТ >>> РАБОТА >>> ЛАБОРАТОРНЫЕ РАБОТЫ
@dp.callback_query(Callback_Data.filter(F.key == "select_services_lab"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    year = callback_data.value.split("_")[1]
    subject = callback_data.value.split("_")[0]
    chat_id = callback.message.chat.id
    work = callback_data.value.split("_")[2]
    work_id = callback_data.value.split("_")[3]

    main_registry_list, = functions.import_lists_from_db(["main_registry_list"])
    data = executors_list[chat_id].config.selected_services

    def select_lab_callback():

        functions.check_keys(data.current, [year, subject, work])
        if work_id in list(data.current[year][subject][work].keys()):

            del data.current[year][subject][work][work_id]
            functions.delete_keys(data.current, [year, subject, work])

            if work_id not in list(data.append.get(year, {}).get(subject, {}).get(work, {}).keys()):
                functions.check_keys(data.remove, [year, subject, work])
                data.remove[year][subject][work][work_id] = {}

            if work_id in list(data.append.get(year, {}).get(subject, {}).get(work, {}).keys()):
                del data.append[year][subject][work][work_id]
                functions.delete_keys(data.append, [year, subject, work])

        else:
            data.current[year][subject][work][work_id] = {}

            if work_id not in list(data.remove.get(year, {}).get(subject, {}).get(work, {}).keys()):
                functions.check_keys(data.append, [year, subject, work])
                data.append[year][subject][work][work_id] = {}

            if work_id in list(data.remove.get(year, {}).get(subject, {}).get(work, {}).keys()):
                del data.remove[year][subject][work][work_id]
                functions.delete_keys(data.remove, [year, subject, work])


    if work_id != "none":
        select_lab_callback()

    markup = InlineKeyboardBuilder()
    lab_list = list(main_registry_list[year][subject]["work"][work]["work_id"].keys())
    for work_id in lab_list:
        button_text = main_registry_list[year][subject]["work"][work]["work_id"][work_id]["work_id_name"]
        if data.current.get(year, {}).get(subject, {}).get(work, {}).get(work_id) == {}:
            button_text = f"✅ {button_text}"
        markup.button(text=button_text, callback_data=Callback_Data(key=f"select_services_lab", value=f"{subject}_{year}_{work}_{work_id}"))

    markup.button(text="Назад", callback_data=Callback_Data(key=f"select_services_work", value=f"{subject}_{year}_none")); markup.adjust(1)

    await callback.message.edit_caption(caption=content.text_select_services_work, reply_markup=markup.as_markup())

    executors_list[chat_id].config.selected_services = data
    db_connection.sql_UPDATE('public."Executors"', "chat_id", chat_id, ["config"], *[executors_list[callback.message.chat.id].config.instance_to_json()])


    #   ЗАПРОС (ПОСМОТРЕТЬ ФОРМУ) >>> ФОРМА
@dp.callback_query(Callback_Data.filter(F.key == "services_form_view"))
async def callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    username = callback.from_user.username
    main_registry_list, = functions.import_lists_from_db(["main_registry_list",])

    text_application_form = ("📌Данные заявки:""\n\n"
     f"chat_id: {chat_id}\nusername: {username}\n\n"
     "✅Выбранные услуги:\n")
    for year in list(executors_list[chat_id].config.selected_services.current.keys()):
        text = f"Курс {year}\n"
        for subject_id in list(executors_list[chat_id].config.selected_services.current[year].keys()):
            subject_name = main_registry_list[year][subject_id]["subject_name"]
            text += f"{subject_name}: "
            for work in executors_list[chat_id].config.selected_services.current[year][subject_id]:
                work_name = main_registry_list[year][subject_id]["work"][work]["work_name"]
                text += f"{work_name}, "
            text = text[:-2] + "\n"
        text_application_form += text + "\n"

    markup = InlineKeyboardBuilder()
    markup.button(text="Назад", callback_data=Callback_Data(key=f"services", value=""))
    markup.button(text="Отправить", callback_data=Callback_Data(key=f"application_form_send", value=f"{chat_id}")); markup.adjust(1)

    await callback.message.edit_caption(caption=text_application_form, reply_markup=markup.as_markup())

"""
    #   ЗАПРОС (ПОСМОТРЕТЬ ФОРМУ) >>> ФОРМА >>> ОТПРАВИТЬ ФОРМУ
@dp.callback_query(Callback_Data.filter(F.key == "application_form_send"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    ex_chat_id = int(callback_data.value)
    chat_id = callback.message.chat.id
    username = callback.from_user.username
    main_registry_list, = r_functions.import_in_dict_from_db(["main_registry_list"])

    markup = InlineKeyboardBuilder()
    markup.button(text="На главную", callback_data=Callback_Data(key=f"application", value=""))

    await callback.message.edit_caption(caption=r_content.text_application_form_callback, reply_markup=markup.as_markup())

    text_application_form = ("📌Данные заявки:""\n\n"
                             f"chat_id: {chat_id}\nusername: {username}\n\n"
                             "✅Выбранные услуги:\n")
    for year in list(executors_dict[chat_id]["config"]["selected_services"].current.keys()):
        year_number = year[5:]
        text = f"Курс {year_number}\n"
        for subject in list(executors_dict[chat_id]["config"]["selected_services"].current[f"year_{year_number}"].keys()):
            subject_name = main_registry_list[f"year_{year_number}"][subject]["subject_name"]
            text += f"{subject_name}: "
            for work in executors_dict[chat_id]["config"]["selected_services"].current[f"year_{year_number}"][subject]:
                work_name = main_registry_list[f"year_{year_number}"][subject]["work"][work]["work_name"]
                text += f"{work_name}, "
            text = text[:-2] + "\n"
        text_application_form += text + "\n\n"

    phone_number = executors_dict[chat_id]["payment"]["phone_number"]
    bank = executors_dict[chat_id]["payment"]["bank"]
    text_application_form += (f"Номер телефона: {phone_number}\nБанк: {bank}")

    markup2 = InlineKeyboardBuilder()
    markup2.button(text="✅Подтвердить", callback_data=Callback_Data(key="application_form_confirm", value=f"{ex_chat_id}"))
    markup2.button(text="❌Отклонить", callback_data=Callback_Data(key="application_form_reject", value=f"{ex_chat_id}"))

    await callback.message.answer(text_application_form, reply_markup=markup2.as_markup())


    #   ЗАПРОС (ПОСМОТРЕТЬ ФОРМУ) >>> ФОРМА >>> ОТПРАВИТЬ ФОРМУ >>> ПОДТВЕРДИТЬ со стороны босса
@dp.callback_query(Callback_Data.filter(F.key =="application_form_confirm"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    chat_id = int(callback_data.value)
    main_registry_list, active_registry_dict = r_functions.import_in_dict_from_db(["main_registry_list", "active_registry_dict"])

    markup = InlineKeyboardBuilder()
    markup.button(text="Скрыть", callback_data=Callback_Data(key=f"delete", value=""))

    await callback.message.delete()
    await callback.message.answer(r_content.text_application_form_confirm, reply_markup=markup.as_markup())

    data = executors_dict[chat_id]["config"]["selected_services"]
    for year in list(data.append.keys()):
        for subject in list(data.append[year].keys()):
            for work in list(data.append[year][subject].keys()):

                if data.append[year][subject][work] == {}:
                    main_registry_list[year][subject]["work"][work]["executors"].append(chat_id)
                    if len(main_registry_list[year][subject]["work"][work]["executors"]) == 1:
                        functions.check_keys(active_registry_dict, [year, subject])
                        active_registry_dict[year][subject][work] = {}

                else:
                    for work_id in list(data.append[year][subject][work].keys()):
                        main_registry_list[year][subject]["work"][work]["work_id"][work_id]["executors"].append(chat_id)
                        if len(main_registry_list[year][subject]["work"][work]["work_id"][work_id]["executors"]) == 1:
                            functions.check_keys(active_registry_dict, [year, subject, work])
                            active_registry_dict[year][subject][work][work_id] = {}


    for year in list(data.remove.keys()):
        for subject in list(data.remove[year].keys()):
            for work in list(data.remove[year][subject].keys()):

                if data.remove[year][subject][work] == {}:
                    main_registry_list[year][subject]["work"][work]["executors"].remove(chat_id)
                    if len(main_registry_list[year][subject]["work"][work]["executors"]) == 0:
                        del active_registry_dict[year][subject][work]
                        functions.delete_keys(active_registry_dict, [year, subject])

                else:
                    for work_id in list(data.remove[year][subject][work].keys()):
                        main_registry_list[year][subject]["work"][work]["work_id"][work_id]["executors"].remove(chat_id)
                        if len(main_registry_list[year][subject]["work"][work]["work_id"][work_id]["executors"]) == 0:
                            del active_registry_dict[year][subject][work][work_id]
                            functions.delete_keys(active_registry_dict, [year, subject, work])

    executors_dict[chat_id]["config"]["selected_services"] = data
    executors_dict[chat_id]["config"]["selected_services"].append = {}
    executors_dict[chat_id]["config"]["selected_services"].remove = {}

    con, cur = r_functions.connection()
    cur.execute('UPDATE public."Executors" SET config = %s WHERE chat_id = %s', (json.dumps(executors_dict[chat_id]["config"]), chat_id))
    cur.execute('UPDATE public."Registry_Data" SET registry = %s WHERE registry_name = %s', (json.dumps(main_registry_list), "main_registry"))
    cur.execute('UPDATE public."Registry_Data" SET registry = %s WHERE registry_name = %s', (json.dumps(active_registry_dict), "active_registry"))

    con.commit(); con.close()


        #   ЗАПРОС (ПОСМОТРЕТЬ ФОРМУ) >>> ФОРМА >>> ОТПРАВИТЬ ФОРМУ >>> ОТКЛОНИТЬ со стороны босса
@dp.callback_query(Callback_Data.filter(F.key == "application_form_reject"))
async def callback(callback: CallbackQuery, callback_data: Callback_Data):
    chat_id = int(callback_data.value)

    markup = InlineKeyboardBuilder()
    markup.button(text="Скрыть", callback_data=Callback_Data(key="delete", value=""))

    await callback.message.delete()
    await bot.send_message(chat_id, r_content.text_application_form_reject, reply_markup=markup.as_markup())


"""

    #   СКРЫТЬ
@dp.callback_query(Callback_Data.filter(F.key == "delete"))
async def callback(callback: CallbackQuery):
    await callback.message.delete()

async def main():
    await dp.start_polling(bot)

asyncio.run(main())