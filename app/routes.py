#! /usr/bin/python3

from datetime import datetime
import os
import re
from flask import (
    Flask, 
    abort, 
    jsonify,
    json, 
    request, 
    current_app
)
from flask_jwt_extended import (
    JWTManager, 
    jwt_required, 
    create_access_token,
    get_jwt_identity
)
from werkzeug.exceptions import HTTPException
from app.apiexception import (
    APIexception, 
    APImissingParameter, 
    APIreturnError,
    APIsqlError
)
from app.db_sqlite import DB_sqlite as db
from app.handlers import Const
from app.eventpool import EventPool as EventServer

if not current_app.config['TESTING']:
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

# ====== CONST STRING VALUES ======
# =================================

c_queries = Const(
    CREATE_TABLE_TEMP = (
        "CREATE TABLE IF NOT EXISTS tbl_temperature ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "int_sensor INT NOT NULL, "
        "real_value REAL NOT NULL, "
        "str_date CHAR(30), "
        "str_comment CHAR(50)"
    ),
    CREATE_TABLE_SENSOR = (
        "CREATE TABKE IF NOT EXISTS tbl_sensor ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "str_name CHAR(50), "
        "str_folder CHAR(50), "
        "str_postition CHAR(50), "
        "str_unit CHAR(1), "
        "str_date_created CHAR(30), "
        "str_comment CHAR(50)"
    ),
    GET_TEMP = "SELECT * FROM " + current_app.config['TBL_TEMPERATURE'] + " WHERE str_date BETWEEN ? AND ?",
    DELETE_TEMP = "DELETE FROM " + current_app.config['TBL_TEMPERATURE'] + " WHERE id = ?",
    CREATE_SENSOR = "INSERT INTO " + current_app.config['TBL_SENSOR'] + 
        " (str_name, str_folder, str_position, str_unit, str_date_created, str_comment) VALUES (?, ?, ?, ?, ?, ?)",
    GET_SENSOR = "SELECT * FROM " + current_app.config['TBL_SENSOR'] + " WHERE id = ?",
    GET_SENSOR_ALL = "SELECT * FROM " + current_app.config['TBL_SENSOR'],
    DELETE_SENSOR = "DELETE FROM " + current_app.config['TBL_SENSOR'] + " WHERE id = ?"
)

c_folders = Const(
    BASE_DIR = "/sys/bus/w1/devices/"
)

jwt = JWTManager(current_app)

# Mitigate the database
if not current_app.config['TESTING']:
    try:
        # Create the table if needed
        conn = db(current_app.config['APP_DATABASE'])
        db.mitigate_database(c_queries.CREATE_TABLE_TEMP)
        db.mitigate_database(c_queries.CREATE_TABLE_SENSOR)

    except APIsqlError as e:
        print("Error when mitigating the database")
        raise 

# Start the EventServer
pool = EventServer(
    current_app.config['INTERVAL_TIME'], 
    current_app.config['DEBUG'], 
    current_app.config['TESTING'] 
)
pool.setup_db(
    current_app.config['APP_DATABASE'], 
    current_app.config['TBL_TEMPERATURE'], 
    current_app.config['TBL_SENSOR'], 
    current_app.config['TBL_TEMP_MAX']
)


# ====== ERROR HANDLER HERE ======
# ================================

@current_app.errorhandler(HTTPException)
def generic_exception(e):
    #Return JSON instead of HTML for HTTP errors.
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.msg,
    })
    response.content_type = "application/json"
    return response

# ====== ROUTES START HERE ======
# ===============================

@current_app.route('/auth/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            raise APImissingParameter(400, "Missing json object in request")
    
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if not username:
            raise APImissingParameter(400, "Missing username parameter in payload")
        if not password:
            raise APImissingParameter(400, "Missing password parameter in payload")

        if username != 'test' or password != 'test':
            return jsonify({"msg": "Bad username or password"}), 401

    except APIexception as e:
        abort(e.code, description=e.msg)

    access_token = create_access_token(identity=username)
    msg = {
        'token' : access_token
    }
    return jsonify(msg), 200

@current_app.route('/auth/logout', methods=['GET', 'OPTIONS'])
def logout():
    try:
        pass
    except APIexception as e:
        print("Something")

@current_app.route('/temperature/sensor', methods=['POST'])
@jwt_required
def add_sensor():
    
    if (not request.is_json or 
        request.json['name'] or
        request.json['folder'] or
        request.json['postition'] or
        request.json['unit'] or
        request.json['comment']):
        raise APImissingParameter(400, name="Bad request", description="Missing parameters in request")
    
    name = request.json.get('name', None)
    folder = request.json.get('folder', None)
    position = request.json.get('position', None)
    unit = request.json.get('unit', None)
    comment = request.json.get('comment', None)
    str_date = datetime.now().date()
    str_time = datetime.now().time()
    date = ' '.join(str_date, str_time)

    conn = db(current_app.config['APP_DATABASE'])
    return_id = db.run_query_non_result(c_queries.CREATE_SENSOR, (name, folder, position, unit, date, comment))
    if return_id != id:
        raise APIreturnError(404, name='Not found', description='Return Id from the sql database is not correct')
    
    return jsonify(return_id), 201

@current_app.route('/temperature/sensor', methods=['GET'])
@jwt_required
def get_sensor():
    
    conn = db(current_app.config['APP_DATABASE'])
    return_id = db.run_query_non_result(c_queries.GET_SENSOR, ())
    if return_id != id:
        raise APIreturnError(404, name='Not found', description='Return Id from the sql database is not correct')
    
    return jsonify(return_id), 201

@current_app.route('/temperature/sensor/<int:id>', methods=['DELETE'])
@jwt_required
def delete_sensor(id):
    pass


@current_app.route('/temperature/start/<int:seconds>', methods=['GET'])
@jwt_required
def start_temp(seconds):
    
    if seconds == None or seconds == '':
        raise APImissingParameter(400, name="Bad request", description="Missing parameters in request")

    pool.start()

@current_app.route('/temperature/stop', methods=['GET', 'OPTIONS'])
@jwt_required
def stop_temp():
    
    pool.stop()


@current_app.route('/temperature/read/<int:sensor>', methods=['GET'])
@jwt_required
def read_temp(sensor):

    if sensor == None or sensor == '':
        raise APImissingParameter(400, name="Bad request", description="Missing parameters in request")

    print(c_queries.GET_SENSOR)
    conn = db(current_app.config['APP_DATABASE'])
    sensor = db.run_query_result_many(c_queries.GET_SENSOR, (sensor, ))

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
        msg = {
            'Sensor' : sensor,
            'Temperature' : temp_c
        }
        return jsonify(msg), 200
    elif sensor[4] == 'F' or sensor[4] == 'f':
        msg = {
            'Sensor' : sensor,
            'Temperature' : temp_f
        }
        return jsonify(msg), 200
    else:
        abort(404, name="Not found", description="Sensor setting has an unknown unit")


# curl -d '{"sensor":"1", "start_date":"2020-07-01", "end_date":"2020-07-4"}' -H "Content-Type: application/json" -X GET http://localhost:5000/temperature
@current_app.route('/temperature', methods=['GET'])
@jwt_required
def get_temp():

    if (not request.is_json or 
        request.json['sensor'] or
        request.json['start_date'] or
        request.json['end_date']):
        raise APImissingParameter(400, name="Bad request", description="Missing parameters in request")

    sensor_id = request.json.get('sensor', None)
    start_date = request.json.get('start_date', None)
    end_date = request.json.get('end_date', None)

    print(c_queries.GET_TEMP)
    conn = db(current_app.config['APP_DATABASE'])
    lst = db.run_query_result_many(c_queries.GET_TEMP, (start_date, end_date))
    
    result = [(lambda x: x[1] == sensor_id)(row) for row in lst]
    return jsonify(result), 200

@current_app.route('/temperature/<int:id>', methods=['DELETE'])
@jwt_required
def delete_temp(id):

    if id == None or id == '':
        raise APImissingParameter(400, "Missing parameters in request")

    print(c_queries.DELETE_TEMP)
    conn = db(current_app.config['APP_DATABASE'])
    return_id = db.run_query_non_result(c_queries.DELETE_TEMP, (id, ))
    if return_id != id:
        raise APIreturnError(404, name='Not found', description='Return Id from the sql database is not correct')
    
    return jsonify(return_id), 200

# current_user = get_jwt_identity()
# logged_in_as=current_user