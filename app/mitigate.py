
from app.db_sqlite import DB_sqlite as db
from app.handlers import Const

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
            # TODO hash password
            CREATE_TABLE_USER = (
                "CREATE TABLE IF NOT EXISTS tbl_user ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "str_first_name CHAR(50), "
                "str_second_name CHAR(50), "
                "str_user_name CHAR(50) NOT NULL UNIQUE, "
                "str_password CHAR(250) NOT NULL UNIQUE)"
            ),
            INSERT_TEST_USER = (
                "INSERT INTO tbl_user ("
                "str_first_name, "
                "str_second_name, "
                "str_user_name, "
                "str_password) VALUES (?,?,?,?)"
            )
        )

    def create_tables(self) -> db:

        #print(self.queries.CREATE_TABLE_TEMP)
        #print(self.queries.CREATE_TABLE_USER)
        #print(self.database)

        if self.testing:
            self.conn = db(self.database, memory=True)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_TEMP)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_SENSOR)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_USER)
            values = ('test_first', 'test_second', 'test', 'test')
            self.conn.run_query_non_result(self.queries.INSERT_TEST_USER, values)
        else:
            self.conn = db(self.database)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_TEMP)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_SENSOR)
            self.conn.mitigate_database(self.queries.CREATE_TABLE_USER)

        return self.conn
