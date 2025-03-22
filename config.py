import os

token_mainbot = "7430718515:AAHwV2026gadCUfE8wtcUOwwh4ZRN0uWWiI"
token_reshalbot = "7420922837:AAFgkS3qKx__qPTosvy4JiBm7FyCQ-DDchM"

admin_id="1328304100"

db_host = os.getenv("DATABASE_HOST", "localhost")

class DataBaseConnection:
    def __init__(self):
        self.hostname = db_host
        self.database = "DB_UustHelper v2.0"
        self.username = "postgres"
        self.password = "qazokn102wsxijb_PS"
        self.port = 5432
postgresql_config = DataBaseConnection()

chat_id_access_list=[1328304100, 7446688671]
username_access_list=["BlessYou_GG"]


boss_username = "BlessYou_GG"
boss_chat_id = 1328304100

