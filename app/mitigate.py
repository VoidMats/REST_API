
from app.db_sqlite import DB_sqlite as db
from app.handlers import Const
from app.apiexception import APIexception, APIsqlError

class Mitigate():

    def __init__(self, database, testing=False):
        super().__init__()
        self.database = database
        self.testing = testing
        self.conn = None
        self.queries = Const(
            CREATE_TABLE_TEMP = (
                "CREATE TABLE IF NOT EXISTS tbl_temperature ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "int_sensor INT NOT NULL, "
                "real_value REAL NOT NULL, "
                "str_date CHAR(30), "
                "str_comment CHAR(50) )"
            ),
            CREATE_TABLE_SENSOR = (
                "CREATE TABLE IF NOT EXISTS tbl_sensor ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "str_name CHAR(50), "
                "str_folder CHAR(50), "
                "str_position CHAR(50), "
                "str_unit CHAR(1), "
                "str_date_created CHAR(30), "
                "str_comment CHAR(50) )"
            ),
            CREATE_TABLE_SIGNAL = (
                "CREATE TABLE IF NOT EXISTS tbl_signal ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "str_name CHAR(50), "
                "str_pin CHAR(6) NOT NULL UNIQUE, "
                "str_type CHAR(10) NOT NULL, "
                "int_initial_value INT DEFAULT 0, "
                "int_active_high INT DEFAULT 1, "
                "str_comment CHAR(50) )"
            ),
            # TODO hash password
            CREATE_TABLE_USER = (
                "CREATE TABLE IF NOT EXISTS tbl_user ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "str_first_name CHAR(50), "
                "str_second_name CHAR(50), "
                "str_user_name CHAR(50) NOT NULL UNIQUE, "
                "str_password CHAR(250) NOT NULL UNIQUE)"
            ),
            CREATE_TABLE_TOKENLIST = (
                "CREATE TABLE IF NOT EXISTS tbl_token ("
                "id INTEGER PRIMARY KEY, "
                "str_jti CHAR(36) NOT NULL, "
                "str_token_type CHAR(10) NOT NULL, "
                "str_username CHAR(50) NOT NULL UNIQUE, "
                "str_date_expires CHAR(30) NOT NULL)"
            ),
            INSERT_TEST_USER = (
                "INSERT INTO tbl_user ("
                "str_first_name, "
                "str_second_name, "
                "str_user_name, "
                "str_password) VALUES (?,?,?,?)"
            )
            # TODO SELECT test user
        )

    def create_tables(self) -> db:

        if self.testing:
            self.conn = db(self.database, memory=True)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_TEMP)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_SENSOR)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_SIGNAL)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_USER)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_TOKENLIST)
            values = ('test_first', 'test_second', 'test', 'test')
            self.conn.run_query_non_result(self.queries.INSERT_TEST_USER, values)
        else:
            self.conn = db(self.database)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_TEMP)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_SENSOR)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_SIGNAL)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_USER)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_TOKENLIST)

            #try:
                #values = ('test', 'test', 'test', 'test')
                #self.conn.run_query_non_result(self.queries.INSERT_TEST_USER, values)
            #except APIsqlError as e:
            #    print("Test user already exist")

        return self.conn
