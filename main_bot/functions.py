import datetime
import json
import config

from db_connection import connection
import classes
def import_lists_from_db(values_list):
    con, cur = connection()
    lists = []

    if "users_list" in values_list:
        cur.execute('SELECT * FROM public."Users"')
        users_table = cur.fetchall()
        users_list = {}

        for row in users_table:
            config = classes.Config()
            other_data = classes.OtherData()
            config.order_history_filters.work = row[6]["order_history_filters"]["work"]

            other_data.temporary_data = row[7]["temporary_data"]
            other_data.bg_photo_id = row[7]["bg_photo_id"]
            other_data.message_id = row[7]["message_id"]

            users_list[row[0]] = classes.User(row[1], row[2], row[3], row[4], row[5], config, other_data)
        lists.append(users_list)

    if "orders_list" in values_list:
        cur.execute('SELECT * FROM public."Orders"')
        orders_table = cur.fetchall()
        orders_list = {}
        for row in orders_table:
            orders_list[row[0]] = classes.Order(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14])
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

def register_user(chat_id, username, first_name, last_name, users_list):
    con, cur = connection()
    cur.execute(f'SELECT EXISTS (SELECT 1 FROM public."Users" WHERE chat_id = %s)', (chat_id,))
    exists = cur.fetchone()[0] == 1
    if exists:
        cur.execute('UPDATE public."Users" SET username=%s, first_name=%s, last_name=%s WHERE chat_id = %s',
                    (username, first_name, last_name, chat_id))
    else:
        users_list[chat_id] = classes.User(username, first_name, last_name, None, None, classes.Config(), classes.OtherData())
        cur.execute('INSERT INTO public."Users" (chat_id, username, first_name, last_name, date_reg, config, other_data) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (chat_id, username, first_name, last_name, None, classes.Config.class_to_json(), classes.OtherData.class_to_json()))
        cur.execute(f'SELECT data FROM public."Sorted_Data" WHERE object = %s', ("orders",))
        sorted_data_orders = cur.fetchall()[0][0]
        sorted_data_orders["chat_id"][chat_id] = []
        cur.execute(f'UPDATE public."Sorted_Data" SET data = %s WHERE object = %s',
                    (json.dumps(sorted_data_orders), "orders"))
    con.commit(); con.close()

def register_temporary_data(chat_id, argument_value_list, index_list, list):
    con, cur = connection()

    for argument_value, index in zip(argument_value_list, index_list):
        if 0 <= index < len(list[chat_id].other_data.temporary_data):
            list[chat_id].other_data.temporary_data[index] = argument_value
        else:
            list[chat_id].other_data.temporary_data.append(argument_value)

    cur.execute(f'UPDATE public."Users" SET other_data = %s WHERE chat_id = %s', (list[chat_id].other_data.instance_to_json(), chat_id))

    con.commit(); con.close()

def delete_temporary_data(chat_id, index_list, list):
    con, cur = connection()
    for index in index_list:
        if 0 <= index < len(list[chat_id].other_data.temporary_data):
            del list[chat_id].other_data.temporary_data[index]

    cur.execute(f'UPDATE public."Users" SET other_data = %s WHERE chat_id = %s', (list[chat_id].other_data.instance_to_json(), chat_id))
    con.commit(); con.close()

def retrieve_temporary_data(chat_id, index_list, list):
    values_list = []
    for index in index_list:
        values_list.append(list[chat_id].other_data.temporary_data[index])
    return values_list

def retrieve_from_instance(instance, attribute_list):
    value_list = []
    for attribute in attribute_list:
        value_list.append(getattr(instance, attribute))
    return value_list

def retrieve_from_object(object, key_list):
    value_list = []
    for subkey in key_list:
        value_list.append(object[subkey])
    return value_list

def import_in_object(object, key_list, value_list):
    for key, value in zip(key_list, value_list):
        object[key] = value


def order_info_user(order_id, chat_id, year, subject_name, work, work_name, work_id, work_id_name, specific_data, price, markup):
    markup.button(text="🧹 Скрыть",  callback_data=classes.Callback_Data(key="delete", value=""))

    if work == "sdo":
        platform, login, password = specific_data["platform"], specific_data["login"], specific_data["password"]
        text = (f"📌 <b>Заказ № {order_id}:</b> {work_name}\n\n"
        f"ℹ️Детали заказа:\n"
        f" • <b>Курс:</b> {year}\n"
        f" • <b>Предмет:</b> {subject_name}\n"
        f" • <b>Номер теста:</b> {work_id}\n"
        f" • <b>Название теста:</b> {work_id_name}\n"
        f" • <b>Платформа:</b> {platform}\n"
        f" • <b>Логин:</b> {login}\n"
        f" • <b>Пароль:</b> {password}\n"
        f" • <b>Стоимость оплаты:</b> <b><em>{price} р.</em></b>"
        "\n\n❗Cвяжитесь с исполнителем для получения инструкций по оплате. "
        "Для этого нажмите 💬 Связаться с исполнителем, после чего вас перекинет в личный чат с исполнителем, "
        "а затем отправьте идентификатор заказа.\n\n"
        f"Ваш идентификатор заказа: <code>o{order_id}c{chat_id}</code>")
        markup.button(text="💬 Связаться с менеджером", url=f"https://t.me/{config.boss_username}")

        file_path = None

    elif work == "lab":

        manual_file_path, manual_file_name = specific_data["manual_file_path"], specific_data["manual_file_name"]
        text = (f"📌 <b>Заказ № {order_id}:</b> {work_name}\n\n"
                f"ℹ️Детали заказа:\n"
                f" • <b>Курс:</b> {year}\n"
                f" • <b>Предмет:</b> {subject_name}\n"
                f" • <b>Номер ЛР:</b> {work_id}\n"
                f" • <b>Название ЛР:</b> {work_id_name}\n"
                f" • <b>Название архива/документа:</b> {manual_file_name}\n"
                f" • <b>Стоимость оплаты:</b> <b><em>{price} р.</em></b>"
                "\n\n❗Cвяжитесь с менеджером для получения инструкций по оплате. "
                "Для этого нажмите 💬 Связаться с менеджером, после чего вас перекинет в личный чат с менеджером, "
                "а затем отправьте идентификатор заказа.\n\n"
                f"Ваш идентификатор заказа: <code>o{order_id}c{chat_id}</code>")
        markup.button(text="💬 Связаться с менеджером", url=f"https://t.me/{config.boss_username}")

        if manual_file_path != None:
            file_path = manual_file_path
        else:
            file_path = None

    elif work == "kurs":

        manual_file_path, manual_file_name = specific_data["manual_file_path"], specific_data["manual_file_name"]
        text = (f"📌 <b>Заказ № {order_id}:</b> {work_name}\n\n"
                f"ℹ️Детали заказа:\n"
                f" • <b>Курс:</b> {year}\n"
                f" • <b>Предмет:</b> {subject_name}\n"
                f" • <b>Номер КР:</b> {work_id}\n"
                f" • <b>Название КР:</b> {work_id_name}\n"
                f" • <b>Название архива/документа:</b> {manual_file_name}\n"
                f" • <b>Стоимость оплаты:</b> <b><em>{price} р.</em></b>"
                "\n\n❗Cвяжитесь с менеджером для получения инструкций по оплате. "
                "Для этого нажмите 💬 Связаться с менеджером, после чего вас перекинет в личный чат с менеджером, "
                "а затем отправьте идентификатор заказа.\n\n"
                f"Ваш идентификатор заказа: <code>o{order_id}c{chat_id}</code>")
        markup.button(text="💬 Связаться с менеджером", url=f"https://t.me/{config.boss_username}")

        if manual_file_path != None:
            file_path = manual_file_path
        else:
            file_path = None
    return [text, markup, file_path]