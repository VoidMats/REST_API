#! /usr/bin/python3

import sqlite3
from sqlite3 import Error, DatabaseError, OperationalError
from app.apiexception import APIexception, APIsqlError

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
                self.conn = sqlite3.connect(':memory:')
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

    def run_query_non_result(self, query, values) -> int:
        id = None
        try:
            self.__create_conn()
            self.cur.execute(query, values)
            id = self.cur.lastrowid
            self.conn.commit()
            if not self.memory:
                self.__close_conn()
            return id
        except (Error, DatabaseError, OperationalError) as e:
            print("Error in run_query_non_result - ", e)
            raise APIsqlError(500, e)
        return id

    def run_query_result_many(self, query, values) -> tuple:
        result = None
        try:
            self.__create_conn()
            self.cur.execute(query)
            result = self.cur.fetchall()
            if not self.memory:
                self.__close_conn()
            return result
        except (Error, DatabaseError, OperationalError) as e:
            print("Error in run_query_result_many - ", e)
            raise APIsqlError(500, e)            

