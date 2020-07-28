#! /usr/bin/python3

import sqlite3
from sqlite3 import Error, DatabaseError, OperationalError
if __package__ == 'app':
    from app.apiexception import APIexception, APIsqlError
else:
    from apiexception import APIexception, APIsqlError

class DB_sqlite():

    def __init__(self, db_name, memory=False):
        super().__init__()
        self.db_name = db_name
        self.memory = memory
        self.cur = None
        self.conn = None

    def __create_conn(self):
        try:
            if self.memory:
                if self.conn == None:
                    self.conn = sqlite3.connect(':memory:')
                    self.cur = self.conn.cursor()
            else:
                self.conn = sqlite3.connect(self.db_name)
                self.cur = self.conn.cursor()

        except (Error, DatabaseError, OperationalError) as e:
            print("Error in __create_conn - ", e)
            if self.conn:
                self.__close_conn()
    
    def __close_conn(self):
        self.conn.close()
        self.cur = None
        self.conn = None

    def mitigate_database(self, query) -> None:
        try:
            self.__create_conn()
            self.cur.execute(query, ())
            id = self.cur.lastrowid
            self.conn.commit()
        except (Error, DatabaseError, OperationalError) as e:
            print("Error in run_query_non_result - ", e.args[0])
            raise APIsqlError(500, name='SQL error', msg=e)

    def run_query_non_result(self, query, values=None) -> int or None:
        id = None
        try:
            self.__create_conn()
            if values == None:
                self.cur.execute(query)
            else:
                self.cur.execute(query, values)
            id = self.cur.lastrowid
            self.conn.commit()
            if not self.memory:
                self.__close_conn()
            return id
        except (Error, DatabaseError, OperationalError) as e:
            print("Error in run_query_non_result - ", e.args[0])
            raise APIsqlError(500, name='SQL error', msg=e)
        return id

    def run_query_result_many(self, query, values=None) -> list:
        result = None
        try:
            self.__create_conn()
            if values == None:
                self.cur.execute(query)
            else:
                self.cur.execute(query, values)
            result = self.cur.fetchall()
            if not self.memory:
                self.__close_conn()
            return result
        except (Error, DatabaseError, OperationalError) as e:
            print("Error in run_query_result_many - ", e)
            raise APIsqlError(500, name='SQL error', msg=e)            

