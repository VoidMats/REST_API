#! /usr/bin/python3

import re
import datetime
from threading import Thread, Event
if __package__ == 'app':
    from app.db_sqlite import DB_sqlite
    import logging
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s')
    logging.debug('Instantiate Eventpool from app')
else:
    from db_sqlite import DB_sqlite
    import logging
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s')
    logging.debug('Instantiate Eventpool from __main__')
    from time import sleep

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
        self.stop_flag = Event()
        self.t_pool = Worker(
            event=self.stop_flag, 
            time=time,
            execute=self.__run_pool) 
        self.t_pool.setDaemon(True)

    def setup_db(self, database='temperature_db.db', tbl_temp='tbl_temperature', tbl_sensor='tbl_sensor', max_values='max_values') -> None:
        self.database = database
        self.tbl_temp = tbl_temp
        self.tbl_sensor = tbl_sensor
        self.max_values = max_values
        
    def start(self) -> bool:
        if not self.t_pool.is_alive():
            self.t_pool.start()
            return self.t_pool.is_alive()
        else:
            return self.t_pool.is_alive()

    def stop(self) -> None:
        if self.t_pool.is_alive():
            self.stop_flag.set()

    def __run_pool(self) -> None:
        if self.testing:
            if self.debug: logging.debug('We are running test function')
            self.__test_function()
        else:
            self.__execute()

    def __execute(self) -> None:

        # Get all sensors from database
        QUERY = "SELECT * FROM "  + self.tbl_sensor 
        db = DB_sqlite(self.database)
        sensors = db.run_query_result_many(query=QUERY)

        # Run through all sensors and record there values
        for sensor in sensors:
            result = self.__read_temperature(sensor)
            # Enter result into database
            QUERY = "INSERT INTO " + self.tbl_temp + " (int_sensor, real_value, str_date, str_comment) VALUES (?, ?, ?, ?)"
            str_date = datetime.now().date()
            str_time = datetime.now().time()
            date = ' '.join(str_date, str_time)

            db = DB_sqlite(self.database)
            return_id = db.run_query_non_result(QUERY, (result[0], result[1], date, "Temperature reading from interval recording"))
            if return_id != None:
                logging.debug("Save temperature value {} from sensor {} into database".format(result[1], result[0]))

        # Check how many values are in the table

    def __test_function(self) -> None:
        logging.debug("Trigger test_function")

    def __read_temperature(self, sensor) -> tuple:
        # read the temperature from the GPIO
        device_file = sensor[2] + '/w1_slave'
        reg_confirm = re.compile('YES')
        reg_temp = re.compile('t=(\d+)')
        temp_c = None
        temp_f = None
        with device_file as f:
            lines = f.readlines()
            measure_confirm = reg_confirm.match(lines)
            if measure_confirm:
                measure_temp = reg_temp.match(lines)
                temp_c = float(measure_temp[1] / 1000.0)
                temp_f = temp_c * 9.0 / 5.0 + 32.0

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
