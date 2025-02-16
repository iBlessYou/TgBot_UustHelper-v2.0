import datetime
import json

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
            config.order_history_filters.work = row[6]["order_history_filters"]["work"]
            config.order_history_filters.status = row[6]["order_history_filters"]["status"]

            other_data = classes.OtherData()
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
            orders_list[row[0]] = {}
            orders_list[row[0]]["chat_id"] = row[1]
            orders_list[row[0]]["username"] = row[2]
            orders_list[row[0]]["kurs"] = row[3]
            orders_list[row[0]]["subject"] = row[4]
            orders_list[row[0]]["subject_name"] = row[5]
            orders_list[row[0]]["work"] = row[6]
            orders_list[row[0]]["work_name"] = row[7]
            orders_list[row[0]]["work_id"] = row[8]
            orders_list[row[0]]["work_id_name"] = row[9]
            orders_list[row[0]]["date_reg"] = row[10]
            orders_list[row[0]]["status"] = row[11]
            orders_list[row[0]]["price"] = row[12]
            orders_list[row[0]]["executor_chat_id"] = row[13]
            orders_list[row[0]]["executor_username"] = row[14]
            orders_list[row[0]]["specific_data"] = row[15]
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
        cur.execute('SELECT registry FROM public."Registry_Data" WHERE registry_name = %s', ("main_registry",))
        main_registry_list = cur.fetchall()[0][0]
        lists.append(main_registry_list)

    if "active_registry_list" in values_list:
        cur.execute('SELECT registry FROM public."Registry_Data" WHERE registry_name = %s', ("active_registry",))
        active_registry_list = cur.fetchall()[0][0]
        lists.append(active_registry_list)

    con.commit(); con.close()
    return lists

def register_user(chat_id, username, first_name, last_name, users_list, sorted_data_orders):
    con, cur = connection()
    cur.execute(f'SELECT EXISTS (SELECT 1 FROM public."Users" WHERE chat_id = %s)', (chat_id,))
    exists = cur.fetchone()[0] == 1
    if exists:
        cur.execute('UPDATE public."Users" SET username=%s, first_name=%s, last_name=%s WHERE chat_id = %s',
                    (username, first_name, last_name, chat_id))
    else:
        users_list[chat_id] = classes.User(username, first_name, last_name, None, datetime.date, classes.Config, classes.OtherData)
        cur.execute('INSERT INTO public."Users" (chat_id, username, first_name, last_name, config, other_data) VALUES (%s, %s, %s, %s, %s, %s)',
            (chat_id, username, first_name, last_name, classes.Config.class_to_json(), classes.OtherData.class_to_json()))
        sorted_data_orders["chat_id"][chat_id] = []
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
