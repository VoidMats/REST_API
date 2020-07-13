#! /usr/bin/python3

import re
import datetime
from threading import Timer
from time import sleep
from app.db_sqlite import DB_sqlite as db

class ProcessPool():

    def __init__(self, sensors, time, database, table):
        super().__init__()
        self.sensors = sensors
        self.time = time
        self.running = False
        self.database = database
        self.table = table
        self.t_timer = Timer(interval=self.time, target=run)

    def start(self):
        self.running = True
        while self.running:
            self.t_timer.start()

    def stop(self):
        self.running = False
        self.t_timer.cancel()

    def run(self, time):
        # Run through all sensors and record there values
        for sensor in self.sensors:
            result = self.read_temperature(sensor)
            # Enter result into database
            QUERY = "INSERT INTO " + self.table + " (int_sensor, real_value, str_date, str_comment) VALUES (?, ?, ?, ?)"
            str_date = datetime.now().date()
            str_time = datetime.now().time()
            date = ' '.join(str_date, str_time)

            conn = db(self.database)
            return_id = db.run_query_non_result(QUERY, (result[0], result[1], date, "Temperature reading from interval recording"))
            if return_id != None:
                print("Save temperature value {} from sensor {} into database".format(result[1], result[0]))
            

    def read_temperature(self, sensor) -> tuple:
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
