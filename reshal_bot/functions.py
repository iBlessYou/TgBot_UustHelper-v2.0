import datetime
import json
import config

from db_connection import connection
import classes
def import_lists_from_db(values_list):
    con, cur = connection()
    lists = []

    if "executors_list" in values_list:
        cur.execute('SELECT * FROM public."Executors"')
        executors_table = cur.fetchall()
        executors_list = {}
        for row in executors_table:
            config = classes.Config()
            config.selected_services.current = row[5]["selected_services"]["current"]
            config.selected_services.append = row[5]["selected_services"]["append"]
            config.selected_services.remove = row[5]["selected_services"]["remove"]
            config.order_filters.work = row[5]["order_filters"]["work"]
            config.order_filters.status = row[5]["order_filters"]["status"]
            config.order_history_filters.work = row[5]["order_history_filters"]["work"]
            config.order_history_filters.status = row[5]["order_history_filters"]["status"]

            other_data = classes.OtherData()
            other_data.temporary_data = row[6]["temporary_data"]
            other_data.bg_photo_id = row[6]["bg_photo_id"]
            other_data.message_id = row[6]["message_id"]

            executors_list[row[0]] = classes.Executor(row[1], row[2], row[3], row[4], config, other_data)

        lists.append(executors_list)

    if "orders_list" in values_list:
        cur.execute('SELECT * FROM public."Orders"')
        orders_table = cur.fetchall()
        orders_list = {}
        for row in orders_table:
            orders_list[row[0]] = classes.Order(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15])
        lists.append(orders_list)

    if "sorted_data_orders_list" in values_list:
        cur.execute('SELECT data FROM public."Sorted_Data" WHERE object = %s', ("orders",))
        sorted_data_orders = cur.fetchall()[0][0]
        lists.append(sorted_data_orders)

    if "sorted_data_apps_list" in values_list:
        cur.execute('SELECT sorted_data FROM public."Sort_Data" WHERE object = %s', ("applications",))
        sorted_data_apps = cur.fetchall()[0][0]
        lists.append(sorted_data_apps)

    if "main_registry_list" in values_list:
        cur.execute('SELECT data FROM public."Registry_Data" WHERE registry_name = %s', ("main_registry",))
        main_registry_list = cur.fetchall()[0][0]
        lists.append(main_registry_list)

    if "active_registry_list" in values_list:
        cur.execute('SELECT data FROM public."Registry_Data" WHERE registry_name = %s', ("active_registry",))
        active_registry_list = cur.fetchall()[0][0]
        lists.append(active_registry_list)

    con.commit(); con.close()
    return lists


def register_executor(chat_id, username, first_name, last_name, executors_list):
    con, cur = connection()
    cur.execute(f'SELECT EXISTS (SELECT 1 FROM public."Executors" WHERE chat_id = %s)', (chat_id,))
    exists = cur.fetchone()[0] == 1
    if exists:
        cur.execute('UPDATE public."Executors" SET username=%s, first_name=%s, last_name=%s WHERE chat_id = %s',
                    (username, first_name, last_name, chat_id))
    else:
        executors_list[chat_id] = classes.Executor(username, first_name, last_name, datetime.date, classes.Config(), classes.OtherData())
        cur.execute('INSERT INTO public."Executors" (chat_id, username, first_name, last_name, config, other_data) VALUES (%s, %s, %s, %s, %s, %s)',
            (chat_id, username, first_name, last_name, classes.Config.class_to_json(), classes.OtherData.class_to_json()))
        cur.execute(f'SELECT data FROM public."Sorted_Data" WHERE object = %s', ("orders",))
        sorted_data_orders = cur.fetchall()[0][0]
        sorted_data_orders["executor_chat_id"][chat_id] = []
        cur.execute(f'UPDATE public."Sorted_Data" SET data = %s WHERE object = %s',
                    (json.dumps(sorted_data_orders), "orders"))
    con.commit(); con.close()


def status_mark(status):
    if status == "begin":
        mark = "🔵"
    elif status == "waiting":
        mark = "🌕"
    elif status == "execution":
        mark = "▶️"
    elif status == "stopped":
        mark = "⏸️"
    elif status == "cancelled":
        mark = "❌"
    elif status == "completed":
        mark = "✅"
    else: mark = "❓"
    return mark

def retrieve_from_instance(instance, attribute_list):
    value_list = []
    for attribute in attribute_list:
        value_list.append(getattr(instance, attribute))
    return value_list

def send_status_text(status):
    if status == "begin":
        status_text = f"📌Статус: Заказ отправлен"
    elif status == "waiting":
        status_text = "📌Статус: Заказ ждет выполнения"
    elif status == "execution":
        status_text = f"📌Статус: Заказ выполняется"
    elif status == "waiting_completion":
        status_text = f"📌Статус: Заказ ожидает оплаты"
    elif status == "stopped":
        status_text = f"📌Статус: Заказ приостановлен"
    elif status == "cancelled":
        status_text = f"📌Статус: Заказ отменен ❌"
    elif status == "completed":
        status_text = f"📌Статус: Заказ выполнен ✅"
    else:
        status_text = "📌Статус: Нет статуса заказ"
    return status_text

def send_status_text_user(status):
    if status == "begin":
        status_text = f"📌Статус: Ваш заказ отправлен"
    elif status == "waiting":
        status_text = "📌Статус: Ваш заказ ждет выполнения"
    elif status == "execution":
        status_text = f"📌Статус: Ваш заказ выполняется"
    elif status == "stopped":
        status_text = f"📌Статус: Ваш заказ приостановлен"
    elif status == "cancelled":
        status_text = f"📌Статус: Ваш заказ отменен ❌"
    elif status == "completed":
        status_text = f"📌Статус: Ваш заказ выполнен ✅"
    else:
        status_text = "📌Статус: Нет статуса заказ"
    return status_text

def check_keys(object, key_list):
    if len(key_list) == 2:
        key_1 = key_list[0]
        key_2 = key_list[1]
        if object.get(key_1):
            if object[key_1].get(key_2) is None:
                object[key_1][key_2] = {}
        else:
            object[key_1] = {}
            object[key_1][key_2] = {}

    else:
        key_1 = key_list[0]
        key_2 = key_list[1]
        key_3 = key_list[2]
        if object.get(key_1):
            if object[key_1].get(key_2):
                if object[key_1][key_2].get(key_3) is None:
                    object[key_1][key_2][key_3] = {}
            else:
                object[key_1][key_2] = {}
                object[key_1][key_2][key_3] = {}
        else:
            object[key_1] = {}
            object[key_1][key_2] = {}
            object[key_1][key_2][key_3] = {}


def delete_keys(object, key_list):
    if len(key_list) == 2:
        key_1 = key_list[0]
        key_2 = key_list[1]
        if object[key_1][key_2] == {}:
            del object[key_1][key_2]
        if object[key_1] == {}:
            del object[key_1]
    else:
        key_1 = key_list[0]
        key_2 = key_list[1]
        key_3 = key_list[2]
        if object[key_1][key_2][key_3] == {}:
            del object[key_1][key_2][key_3]
        if object[key_1][key_2] == {}:
            del object[key_1][key_2]
        if object[key_1] == {}:
            del object[key_1]



def order_info(order_id, chat_id, username, year, subject_name, work, work_name, work_id, work_id_name, specific_data, status,
               markup, executor_chat_id):
    markup.button(text="Скрыть", callback_data=classes.Callback_Data(key="delete", value=""))
    file_path = None
    if work == "lab":
        manual_file_name = specific_data["manual_file_name"]
        if specific_data["manual_file_path"] != None:
            file_path = specific_data["manual_file_path"]

        text = f"{send_status_text(status)}\nЗаказ № {order_id}: {work_name}\n\n"

        if status == "begin":
            text += f"ℹ️Детали заказа:\n • chat_id: {chat_id}\n • username: {username}\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер ЛР: {work_id}\n • Название ЛР: {work_id_name}\n • Название архива/документа: {manual_file_name}"
            markup.button(text="Одобрить заказ", callback_data=classes.Callback_Data(key="order_approve", value=f"{order_id}"))

        elif status == "waiting":
            text += f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер ЛР: {work_id}\n • Название ЛР: {work_id_name}\n • Название архива/документа: {manual_file_name}"
            markup.button(text="Принять заказ", callback_data=classes.Callback_Data(key="order_take", value=f"{order_id}"))

        elif status == "stopped":
            text += f"ℹ️Детали заказа:\n • chat_id: {chat_id}\n • username: {username}\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер ЛР: {work_id}\n • Название ЛР: {work_id_name}\n • Название архива/документа: {manual_file_name}"

        elif status == "execution":
            text += (
                f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер ЛР: {work_id}\n • Название ЛР: {work_id_name}\n • Название архива/документа: {manual_file_name}"
                f"\n\n❗Если заказ выполнен, отправьте архив с документами (лаб. работа и отчет к ней) в расширении zip/rar. "
                f"Архив необходимо отправить как ответ на это сообщение.")
            markup.button(text="Отказаться от заказа",
                          callback_data=classes.Callback_Data(key="order_refuse", value=f"{order_id}"))

        elif status == "waiting_completion":
            markup.button(text="Подтвердить выполнение заказа",
                          callback_data=classes.Callback_Data(key="order_completed", value=f"{order_id}"))
            text += f"ℹ️Детали заказа:\n • chat_id: {chat_id}\n • username: {username}\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер ЛР: {work_id}\n • Название ЛР: {work_id_name}\n • Название архива/документа: {manual_file_name}"
            if specific_data["file_path"] != None:
                file_path = specific_data["file_path"]

        elif status == "completed":
            text += f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер ЛР: {work_id}\n • Название ЛР: {work_id_name}\n • Название архива/документа: {manual_file_name}"
            if specific_data["file_path"] != None:
                file_path = specific_data["file_path"]

        elif status == "cancelled":
            text += f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер ЛР: {work_id}\n • Название ЛР: {work_id_name}\n • Название архива/документа: {manual_file_name}"

    elif work == "sdo":
        platform, login, password = specific_data["platform"], specific_data["login"], specific_data["password"]
        text = f"{send_status_text(status)}\nЗаказ № {order_id}: {work_name}\n\n"

        if status == "begin":
            text += f"ℹ️Детали заказа:\n • username: {username}\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер теста: {work_id}\n • Название теста: {work_id_name}\n • Платформа: {platform}\n • Логин: {login}\n • Пароль: {password}"
            markup.button(text="Одобрить заказ", callback_data=classes.Callback_Data(key="order_approve", value=f"{order_id}"))

        elif status == "waiting":
            text += f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name} • Номер теста: {work_id}\n • Название теста: {work_id_name}\n"
            markup.button(text="Принять заказ", callback_data=classes.Callback_Data(key="order_take", value=f"{order_id}"))

        elif status == "stopped":
            text += f"ℹ️Детали заказа:\n • username: {username}\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер теста: {work_id}\n • Название теста: {work_id_name}\n • Платформа: {platform}\n • Логин: {login}\n • Пароль: {password}"
            markup.button(text="Продолжить выполнение заказа",
                          callback_data=classes.Callback_Data(key="order_continue", value=f"{order_id}"))

        elif status == "execution":
            text += (
                f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер теста: {work_id}\n • Название теста: {work_id_name}\n • Платформа: {platform}\n • Логин: {login}\n • Пароль: {password}"
                f"\n\n❗Если заказ выполнен, отправьте фотографию главной страницы. "
                f"Фото необходимо сжать и отправить как ответ на сообщение с информацией о заказе.")
            markup.button(text="Отказаться от заказа",
                          callback_data=classes.Callback_Data(key="order_refuse", value=f"{order_id}"))

        elif status == "waiting_completion":
            markup.button(text="Подтвердить выполнение заказа",
                          callback_data=classes.Callback_Data(key="order_completed", value=f"{order_id}"))
            text += f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер теста: {work_id}\n • Название теста: {work_id_name}\n • Платформа: {platform}\n • Логин: {login}\n • Пароль: {password}"
            if specific_data["file_path"] != None:
                file_path = specific_data["file_path"]

        elif status == "completed":
            text += f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер теста: {work_id}\n • Название теста: {work_id_name}\n • Платформа: {platform}\n • Логин: {login}\n • Пароль: {password}"
            if specific_data["file_path"] != None:
                file_path = specific_data["file_path"]

        elif status == "cancelled":
            text += f"ℹ️Детали заказа:\n • Курс: {year}\n • Предмет: {subject_name}\n • Номер теста: {work_id}\n • Название теста: {work_id_name}\n • Платформа: {platform}\n • Логин: {login}\n • Пароль: {password}"
    if executor_chat_id in config.chat_id_access_list:
        markup.button(text="❌ Отменить заказ", callback_data=classes.Callback_Data(key="order_cancel_1", value=f"{order_id}"))

    return [text, markup, file_path]

