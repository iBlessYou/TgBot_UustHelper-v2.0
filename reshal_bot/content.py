text_not_access = "❌ У вас нет доступа к этому чат-боту"

text_main=("📌Вы находитель на главной странице чат-бота")

text_orders = ("📌Здесь представлены все заказы, которые находятся в статусе ожидания")

text_orders_all = ("📌 Здесь представлены все существующие заказы. Перейдя в фильтры, можно отфильтровать заказы по статусу выполнения и типу работы.")

text_orders_filters = ("📌 Выберите фильтры")

text_order_history=("📌Здесь находится история выполненных вами заказов""\n\n"
"Выберите тип заказа, чтобы открыть список выполненных заказов")

text_services = ("📌Здесь вам необходимо создать заявку о предоставлении услуг по конкретным предметам и конкретным типам работы "
"(Тесты СДО, лабораторные и прочее)")

text_select_services_year = ("📌Нажмите на курс, чтобы перейти к выбору предметов")

text_application_create_service_kurs = ("📌 Выберите курс")

text_application_create_service_subject = ("📌 Напишите название предмета")

text_application_create_service_work = ("📌 Выберите уже существующий тип работы или добавьте свой")

text_application_create_service_lab_name = ("📌 Введите название лабораторной работы. Сначала укажите номер лабораторной работы, если он существует ")

text_application_create_service_manual = ("📌 Отправьте документ или архив с методическими указаниями по работе. ")

def text_application_create_service_form(argument_name_list, argument_value_list,):
    text = "📌 Сформирована заявка на добавление услуги. Проверьте перед отправкой:\n\n"
    for argument_name, argument_value in zip(argument_name_list, argument_value_list):
        text += f"{argument_name}: {argument_value}\n"
    return text

text_application_create_service_form_send_user = ("✅Ваша заявка отправлена. Скоро вы получите информацию о статусе заявки")

def text_application_create_service_form_send_boss(argument_name_list, argument_value_list,):
    text = "📌 Заявка на добавление услуги:\n\n"
    for argument_name, argument_value in zip(argument_name_list, argument_value_list):
        text += f"{argument_name}: {argument_value}\n"
    return text

text_application_create_service_work_name = ("📌 Напишите название работы")

text_application_form_callback = ("✅Ваша заявка отправлена. Скоро вы получите информацию о статусе заявки")

text_application_form_confirm = ("✅Ваша заявка одобрена. Теперь вам будут приходить заказы по указанным работам")

text_application_form_reject = ("❌Ваша заявка отклонена. С вами свяжутся для выяснения обстоятельств")


text_application_create_service_apply = ("✅Ваша заявка одобрена.\n\n"
"Ваша услуга уже добавлена в реестр услуг. Найдите эту услугу и выберите её, чтобы вам приходили заказы.\n\n"
"Имейте ввиду, что другие пользователи также могут взять эту услугу")

text_select_services_subject = ("📌Нажмите на предмет, чтобы перейти к выбору работ для этого предмета")

text_select_services_work = ("📌Выберите работы по данному предмету. Можно выбрать несколько")

text_application_add_payment_phone_number = ("📌 Введите номер телефона для оплаты")

text_application_add_payment_bank = ("📌 Введите название банка для оплаты. Можно указать несколько банков")

