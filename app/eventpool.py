#! /usr/bin/python3

import re
from datetime import datetime
from threading import Thread, Event
from time import sleep

if __package__ == 'app':
    from app.db_sqlite import DB_sqlite
    from app.handlers import Const
    from app.apiexception import APIonewireError, APIsqlError
    import logging
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s')
    logging.debug('Instantiate Eventpool from app')
else:
    from db_sqlite import DB_sqlite
    from handlers import Const
    from apiexception import APIonewireError, APIsqlError
    import logging
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s')
    logging.debug('Instantiate Eventpool from __main__')

c_folders = Const(
    BASE_DIR = "/sys/bus/w1/devices/"
)

class Worker(Thread):

    def __init__(self, event, time, execute, *args, **kwargs):
        Thread.__init__(self)
        self.stopped = event
        self.time = time
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def run(self):
        while not self.stopped.wait(self.time):
            logging.debug("Execute thread program")
            self.execute(*self.args, **self.kwargs)

class EventPool():

    def __init__(self, time, debug=False, testing=False):
        super().__init__()
        self.database = None
        self.tbl_temp = None
        self.tbl_sensor = None
        self.max_values = None
        self.time = time
        self.debug = debug
        self.testing = testing
        self.t_pool = None
        self.stop_flag = Event()

    def setup_db(self, database='temperature_db.db', tbl_temp='tbl_temperature', tbl_sensor='tbl_sensor', max_values='max_values') -> None:
        self.database = database
        # Check the table name for faulty character
        reg_sqlinjection = re.compile('\W')
        sqlinjection = reg_sqlinjection.findall(tbl_temp)
        if sqlinjection:
            raise APIsqlError(500, "Internal server error", "Attempt to inject SQL query")
        self.tbl_temp = tbl_temp
        sqlinjection = reg_sqlinjection.findall(tbl_sensor)
        if sqlinjection:
            raise APIsqlError(500, "Internal server error", "Attempt to inject SQL query")
        self.tbl_sensor = tbl_sensor
        self.max_values = max_values
        
    def start(self) -> bool:
        # Create the  worker if needed
        if self.t_pool == None:
            logging.debug("Create new worker")
            self.t_pool = Worker(
                event=self.stop_flag, 
                time=self.time,
                execute=self.__run_pool) 
            self.t_pool.setDaemon(True)
            logging.debug(self.t_pool.isAlive())
        # If worker is running check if its alive
        if not self.t_pool.isAlive():
            logging.debug("Start the worker")
            self.stop_flag.clear()
            self.t_pool.start()
            return self.t_pool.isAlive()
        else:
            return self.t_pool.isAlive()

    def stop(self) -> None:
        if self.t_pool.isAlive():
            logging.debug("Stop the worker")
            self.stop_flag.set()
        self.t_pool = None

    def __run_pool(self) -> None:
        if self.testing:
            if self.debug: logging.debug('We are running test function')
            self.__test_function()
        else:
            self.__execute()

    def __execute(self) -> None:

        # Get all sensors from database
        QUERY = "SELECT * FROM "  + self.tbl_sensor 
        conn = DB_sqlite(self.database)
        sensors = conn.run_query_result_many(query=QUERY)

        # Run through all sensors and record there values
        for sensor in sensors:
            result = self.__read_temperature(sensor)
            # Enter result into database
            QUERY = "INSERT INTO " + self.tbl_temp + " (int_sensor, real_value, str_date, str_comment) VALUES (?, ?, ?, ?)"
            str_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            #conn = DB_sqlite(self.database)
            return_id = conn.run_query_non_result(QUERY, (result[0], result[1], str_date, "Temperature reading from interval recording"))

            if return_id != None:
                logging.debug("Save temperature value {} from sensor {} into database".format(result[1], result[0]))
        
        # Check how many values are in the table and remove if above limit
        QUERY = ("DELETE FROM " + self.tbl_temp + 
                " WHERE ROWID IN (SELECT ROWID FROM " + self.tbl_temp + 
                " ORDER BY ROWID DESC LIMIT -1 OFFSET ?)")
        result = conn.run_query_non_result(QUERY, (self.max_values, ))
        print(result)

    def __test_function(self) -> None:
        logging.debug("Trigger test_function")

    def __read_temperature(self, sensor) -> tuple:
        # read the temperature from the DS18B20
        device_file = c_folders.BASE_DIR + sensor[2] + '/w1_slave'
        reg_confirm = re.compile('YES')
        reg_temp = re.compile('t=(\d+)')
        temp_c = None
        temp_f = None

        try:
            # NB with device_file as f: -> Does not work
            f = open(device_file, 'r')
            lines = f.readlines()
            f.close()
            
            measure_confirm = reg_confirm.search(lines[0])
            if measure_confirm:
                measure_temp = reg_temp.search(lines[1])
                temp_c = float(measure_temp[1]) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0

        except OSError:
            APIonewireError(500, "Hardware error", "Could not open/read file: {}".format(device_file))

        if sensor[4] == 'C' or sensor[4] == 'c':
            return (sensor[0], temp_c)
        elif sensor[4] == 'F' or sensor[4] == 'f':
            return (sensor[0], temp_f)
        else:
            return (sensor[0], 0.0)



if __name__ == '__main__':
    pool = EventPool(time=3, debug=True, testing=True)
    logging.debug('Start the Eventpool with 3 sec interval')
    pool.start()
    sleep(15)
    logging.debug('Stop the eventpool')
    pool.stop()
    sleep(5)
    logging.debug('Start the Eventpool with 3 sec interval')
    pool.start()
    sleep(15)
    logging.debug('Stop the eventpool')
    pool.stop()
    sleep(5)
