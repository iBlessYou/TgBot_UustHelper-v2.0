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
            config.selected_services.new = row[5]["selected_services"]["new"]
            config.selected_services.current = row[5]["selected_services"]["current"]
            config.selected_services.append = row[5]["selected_services"]["append"]
            config.selected_services.remove = row[5]["selected_services"]["remove"]
            config.order_filters.work = row[5]["order_filters"]["work"]
            config.order_history_filters.work = row[5]["order_history_filters"]["work"]

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




def retrieve_from_instance(instance, attribute_list):
    value_list = []
    for attribute in attribute_list:
        value_list.append(getattr(instance, attribute))
    return value_list

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



def order_info(order_id, chat_id, username, year, subject_name, work, work_name, work_id, work_id_name, specific_data, price, markup):
    markup.button(text="Скрыть", callback_data=classes.Callback_Data(key="delete", value=""))
    file_path = None

    if work == "sdo":
        platform, login, password = specific_data["platform"], specific_data["login"], specific_data["password"]
        text = (f"📌 <b>Заказ № {order_id}:</b> {work_name}\n\n"
        f"ℹ️Детали заказа:\n"
        f" • <b>chat_id:</b> {chat_id}\n"
        f" • <b>username:</b> {username}\n"
        f" • <b>Курс:</b> {year}\n"
        f" • <b>Предмет:</b> {subject_name}\n"
        f" • <b>Номер теста:</b> {work_id}\n"
        f" • <b>Название теста:</b> {work_id_name}\n"
        f" • <b>Платформа:</b> {platform}\n"
        f" • <b>Логин:</b> {login}\n"
        f" • <b>Пароль:</b> {password}\n"
        f" • <b>Стоимость оплаты:</b> <b><em>{price}</em></b>")

    if work == "lab":
        manual_file_name = specific_data["manual_file_name"]
        if specific_data["manual_file_path"] != None:
            file_path = specific_data["manual_file_path"]

        text = (f"📌 <b>Заказ № {order_id}:</b> {work_name}\n\n"
        f"ℹ️Детали заказа:\n"
        f" • <b>chat_id:</b> {chat_id}\n"
        f" • <b>username:</b> {username}\n"
        f" • <b>Курс:</b> {year}\n"
        f" • <b>Предмет:</b> {subject_name}\n"
        f" • <b>Номер ЛР:</b> {work_id}\n"
        f" • <b>Название ЛР:</b> {work_id_name}\n"
        f" • <b>Название архива/документа:</b> {manual_file_name}\n"
        f" • <b>Стоимость оплаты:</b> <b><em>{price}</em></b>")

    if work == "kurs":
        manual_file_name = specific_data["manual_file_name"]
        if specific_data["manual_file_path"] != None:
            file_path = specific_data["manual_file_path"]

        text = (f"📌 <b>Заказ № {order_id}:</b> {work_name}\n\n"
        f"ℹ️Детали заказа:\n"
        f" • <b>chat_id:</b> {chat_id}\n"
        f" • <b>username:</b> {username}\n"
        f" • <b>Курс:</b> {year}\n"
        f" • <b>Предмет:</b> {subject_name}\n"
        f" • <b>Номер КР:</b> {work_id}\n"
        f" • <b>Название КР:</b> {work_id_name}\n"
        f" • <b>Название архива/документа:</b> {manual_file_name}\n"
        f" • <b>Стоимость оплаты:</b> <b><em>{price}</em></b>")

    return [text, markup, file_path]

