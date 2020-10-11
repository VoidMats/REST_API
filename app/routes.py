#! /usr/bin/python3

from datetime import datetime
import os
import re
import subprocess
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
    get_jwt_identity,
    decode_token
)
from flask_cors import CORS, cross_origin
from werkzeug.exceptions import HTTPException
from app.apiexception import (
    APIexception, 
    APImissingParameter, 
    APIfaultyParameter,
    APIreturnError,
    APIsqlError,
    APIonewireError
)
from gpiozero import (
    LED
)
from app.db_sqlite import DB_sqlite as db
from app.handlers import Const
from app.eventpool import EventPool as EventServer
from app.mitigate import Mitigate

#if not current_app.config['TESTING']:
#    os.system('modprobe w1-gpio')
#    os.system('modprobe w1-therm')

# ====== CONST STRING VALUES ======
# =================================

c_queries = Const(
    GET_TEMP = "SELECT id, int_sensor, real_value, str_date FROM " + current_app.config['TBL_TEMPERATURE'] + " WHERE str_date BETWEEN ? AND ?",
    DELETE_TEMP = "DELETE FROM " + current_app.config['TBL_TEMPERATURE'] + " WHERE id = ?",
    CREATE_SENSOR = "INSERT INTO " + current_app.config['TBL_SENSOR'] + 
        " (str_name, str_folder, str_position, str_unit, str_date_created, str_comment) VALUES (?, ?, ?, ?, ?, ?)",
    GET_SENSOR = "SELECT * FROM " + current_app.config['TBL_SENSOR'] + " WHERE id = ?",
    GET_SENSOR_ALL = "SELECT * FROM " + current_app.config['TBL_SENSOR'],
    DELETE_SENSOR = "DELETE FROM " + current_app.config['TBL_SENSOR'] + " WHERE id = ?",
    GET_SIGNAL = "SELECT * FROM " + current_app.config['TBL_SIGNAL'] + " WHERE id = ?",
    GET_SIGNAL_ALL = "SELECT * FROM " + current_app.config['TBL_SIGNAL'],
    DELETE_SIGNAL = "DELETE FROM " + current_app.config['TBL_SIGNAL'] + " WHERE id = ?",
    GET_USER = "SELECT * FROM " + current_app.config['TBL_USER'] + " WHERE str_user_name = ?",
    ADD_TOKEN = "INSERT INTO " + current_app.config['TBL_TOKEN'] + 
        " (str_jti, str_token_type, str_username, str_date_expires) VALUES (?, ?, ?, ?)",
    DELETE_TOKEN = "DELETE FROM " + current_app.config['TBL_TOKEN'] + " WHERE str_username = ?",
    UPDATE_TOKEN = "UPDATE " + current_app.config['TBL_TOKEN'] + 
        " SET str_jti=?, str_token_type=?, str_date_expires=? WHERE str_username=?"
)

c_folders = Const(
    BASE_DIR = "/sys/bus/w1/devices/"
)

jwt = JWTManager(current_app)
conn_test = None
#CORS(current_app) // TODO this could be removed 

# Mitigate the database
try:
    # Create the table if needed
    mitigate_obj = None
    if current_app.config['TESTING']:
        mitigate_obj = Mitigate(current_app.config['APP_DATABASE'], testing=True)
    else:
        mitigate_obj = Mitigate(current_app.config['APP_DATABASE'])
    
    conn_test = mitigate_obj.create_tables()

except APIsqlError as e:
    print("Error when mitigating the database")
    raise 

# Start the signal_pool
signal_pool = {}
try:
    # Get output data for node

    if current_app.config['TESTINNG']:
        pass
    else:
        conn = db(current_app.config['APP_DATABASE'])
        signals = conn.run_query_result_many(c_queries.GET_SIGNAL_ALL)
        for signal in signals:
            if signal.type.lower() == 'output':
                signal_pool[signal.pin] = LED(signal.pin)
            elif signal.type.lower() == 'input':
                pass
            else:
                raise APIsqlError(500, "Faulty signal type in SQL server") 


except APIsqlError as e:
    print("Error during setup of the signal pool")
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

@current_app.errorhandler(Exception)
def generic_exception(e):
    #Return JSON instead of HTML for HTTP errors.

    if isinstance(e, HTTPException):
        print("Got an HTTPException that has to be converted to general response")
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description
        })
        response.content_type = "application/json"
        return response
    else:
        code = None
        try:
            if e.code:
                code = e.code
        except AttributeError:
            code = 500
        msg = {
            "code": code,
            "name": e.name,
            "description": e.msg
        }
        return jsonify(msg), e.code

# ====== ROUTES START HERE ======
# ===============================

@current_app.route('/auth/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():

    try:
        if not request.is_json:
            raise APImissingParameter(400, "Missing json object in request")
    
        print("we are in login")
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            raise APImissingParameter(400, "Missing username parameter in payload")
        if not password:
            raise APImissingParameter(400, "Missing password parameter in payload")

        user = None
        if current_app.config['TESTING']:
            print("Running in TESTING mode")
            user = conn_test.run_query_result_many(c_queries.GET_USER, (username, ))
        else:
            conn = db(current_app.config['APP_DATABASE'])
            user = conn.run_query_result_many(c_queries.GET_USER, (username, ))
        
        if len(user) == 1:
            access_token = create_access_token(identity=user)
            decoded_token = decode_token(access_token)
            # Get values from token to be stored
            jti = decoded_token['jti']          # unique identifier
            token_type = decoded_token['type']
            #user_id = decoded_token[username]
            expires = datetime.fromtimestamp(decoded_token['exp'])
            # Store in database
            try:
                conn = db(current_app.config['APP_DATABASE'])
                token_id = conn.run_query_non_result(c_queries.ADD_TOKEN, (jti, token_type, username, expires))
            except APIsqlError as e:
                token_id = conn.run_query_non_result(c_queries.UPDATE_TOKEN, (jti,token_type,expires,username))        
            msg = {
                'msg' : 'Success',
                'data' : access_token
            }
            return jsonify(msg), 200

    except APIexception as e:
        abort(e.code, description=e.msg)

    return jsonify({'msg': "Failed", 'data': {'error': "Bad username or password"}}), 401
    

@current_app.route('/auth/logout', methods=['GET'])
@jwt_required
def logout():

    try:
        username = get_jwt_identity()[0][3]
        # Remove token from database
        conn = db(current_app.config['APP_DATABASE'])
        token_id = conn.run_query_non_result(c_queries.DELETE_TOKEN, (username, ))
        msg = {
            'msg': 'Success'
        }
        return jsonify(msg), 200
    except APIexception as e:
        abort(e.code, description=e.msg)

@current_app.route('/temperature/devices', methods=['GET'])
@jwt_required
def get_all_w1_devices():

    tmp = subprocess.Popen(['ls', '/sys/bus/w1/devices/'], stdout = subprocess.PIPE)
    output = tmp.communicate()[0]
    output = output.decode('UTF-8')
    devices = output.split('\n')
    devices = [e for e in devices if e != '']
    try: 
        devices.remove('w1_bus_master1')
    except ValueError as e:
        pass # Can't fine w1_bus_master1. Swallow exception

    msg = {
        'msg' : 'Success',
        'data' : devices
    }
    return jsonify(msg), 200

@current_app.route('/temperature/sensor', methods=['POST'])
@jwt_required
@cross_origin()
def add_sensor():
    
    if (not request.is_json or 
        not 'name' in request.json or
        not 'folder' in request.json or
        not 'position' in request.json or
        not 'unit' in request.json or
        not 'comment' in request.json):
        raise APImissingParameter(400, name="Bad request", msg="Missing parameters in request - {}".format(request.json))

    name = request.json.get('name', None)
    folder = request.json.get('folder', None)
    position = request.json.get('position', None)
    unit = request.json.get('unit', None)
    comment = request.json.get('comment', None)
    date = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
    
    reg_unit = re.compile('^[c|C|f|F]')
    match = reg_unit.match(unit)
    if match == None:
        raise APImissingParameter(400, name="Bad request", msg="Unit has to be F or C representing Farenheit or Celsius")

    return_id = None
    if current_app.config['TESTING']:
        return_id = conn_test.run_query_non_result(c_queries.CREATE_SENSOR, (name, folder, position, match[0], date, comment))
    else:
        conn = db(current_app.config['APP_DATABASE'])
        return_id = conn.run_query_non_result(c_queries.CREATE_SENSOR, (name, folder, position, match[0], date, comment))
    
    if not isinstance(return_id, int):
        raise APIreturnError(404, name='Not found', msg='Return Id from the sql database is not correct')
    
    return jsonify({'msg': 'Success', 'data':return_id}), 201

@current_app.route('/temperature/sensor', methods=['GET'])
@jwt_required
def get_all_sensor():
    
    sensors = None
    if current_app.config['TESTING']:
        sensors = conn_test.run_query_result_many(c_queries.GET_SENSOR_ALL)
    else:
        conn = db(current_app.config['APP_DATABASE'])
        sensors = conn.run_query_result_many(c_queries.GET_SENSOR_ALL)

    if not isinstance(sensors, list):
        raise APIreturnError(404, name='Not found', msg='Sensor from the sql database is not correct')
    
    return jsonify({'msg' : 'Success', 'data' : sensors}), 200

@current_app.route('/temperature/sensor/<int:id>', methods=['GET'])
@jwt_required
def get_sensor(id):

    if id == None:
        raise APImissingParameter(400, name="Bad request", msg="Missing sensor id request")
    
    sensor = None
    if current_app.config['TESTING']:
        sensor = conn_test.run_query_result_many(c_queries.GET_SENSOR, (str(id), ))
    else:
        conn = db(current_app.config['APP_DATABASE'])
        sensor = conn.run_query_result_many(c_queries.GET_SENSOR, (str(id), ))
    
    if not isinstance(sensor, list):
        raise APIreturnError(404, name='Not found', msg='Sensor from the sql database is not correct')
    
    return jsonify({'msg': 'Success', 'data': sensor}), 200

@current_app.route('/temperature/sensor/<int:id>', methods=['DELETE'])
@jwt_required
@cross_origin()
def delete_sensor(id):
    
    if id == None:
        raise APImissingParameter(400, name="Bad request", msg="Missing sensor id request")

    sensor_id = None
    if current_app.config['TESTING']:
        sensor_id = conn_test.run_query_non_result(c_queries.DELETE_SENSOR, (str(id), ))
    else:
        conn = db(current_app.config['APP_DATABASE'])
        sensor_id = conn.run_query_non_result(c_queries.DELETE_SENSOR, (str(id), ))

    if not isinstance(sensor_id, int):
        raise APIreturnError(404, name="Not found", msg="Sensor id from SQL database is not valid")

    return jsonify({'msg': 'Success', 'data': sensor_id}), 200


@current_app.route('/temperature/start/<int:seconds>', methods=['GET'])
@jwt_required
def start_temp(seconds):
    
    if seconds == None or seconds == '':
        raise APImissingParameter(400, name="Bad request", msg="Missing parameters in request")

    result = pool.start(seconds)
    msg = {'msg':'Success' if result==True else 'Failed'}

    return jsonify(msg), 200

@current_app.route('/temperature/stop', methods=['GET'])
@jwt_required
def stop_temp():

    # TODO try/except    
    pool.stop()

    return jsonify({'msg':'Success'}), 200

@current_app.route('/temperature/active', methods=['GET'])
@jwt_required
def active_temp():
    
    result = pool.isEventpoolActive()

    return jsonify({'msg':'Success', 'data':result}), 200


@current_app.route('/temperature/read/<int:id>', methods=['GET'])
@jwt_required
def read_temp(id):

    if id == None or id == '':
        raise APImissingParameter(400, name="Bad request", msg="Missing parameters in request")

    try:
        sensor = None
        if current_app.config['TESTING']:
            # Return a mocked temperature value
            sensor = conn_test.run_query_result_many(c_queries.GET_SENSOR, (id, ))
            msg = {
                'msg' : 'Success',
                'data' : {'sensor' : sensor[0], 'temperature' : 26.54}
            }
            return jsonify(msg), 200
        else:
            # Read temperature value from DS18B20
            conn = db(current_app.config['APP_DATABASE'])
            sensors = conn.run_query_result_many(c_queries.GET_SENSOR, (id, ))
            sensor = sensors[0]
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
                print(measure_confirm)
                if measure_confirm:
                    measure_temp = reg_temp.search(lines[1])
                    print(measure_temp[1])
                    temp_c = float(measure_temp[1]) / 1000.0
                    temp_f = temp_c * 9.0 / 5.0 + 32.0

            except OSError:
                APIonewireError(500, "Hardware error", "Could not open/read file: {}".format(device_file))

            if sensor[4] == 'C' or sensor[4] == 'c':
                msg = {
                    'msg' : 'Success',
                    'data' : { 'sensor' : sensor, 'temperature' : temp_c }
                }
                return jsonify(msg), 200
            elif sensor[4] == 'F' or sensor[4] == 'f':
                msg = {
                    'msg' : 'Success',
                    'data' : {'sensor' : sensor, 'temperature' : temp_f }
                }
                return jsonify(msg), 200
            else:
                APIreturnError(404, name="Not found", msg="Sensor setting has an unknown unit")
        
    except APIexception as e:
        if not 'name' in e:
            e.name = "General fault"
        if not 'msg' in e:
            e.msg = "Server error - {}".format(e.description()) 
        abort(404, e)


# curl -d '{"sensor":"1", "start_date":"2020-07-01", "end_date":"2020-07-4"}' -H "Content-Type: application/json" -X POST http://localhost:5000/temperature
@current_app.route('/temperature', methods=['POST'])
@jwt_required
def get_temp():

    if (not request.is_json or
        not 'sensor' in request.json or
        not 'start_date' in request.json or
        not 'end_date' in request.json):
        raise APImissingParameter(400, name="Bad request", description="Missing parameters in request")

    sensor_id = request.json.get('sensor', None)
    sensor_id_checked = None
    if (isinstance(sensor_id, list)):
        sensor_id_checked = int(sensor_id[0])
    else:
        sensor_id_checked = int(sensor_id)

    start_date = request.json.get('start_date', None)
    end_date = request.json.get('end_date', None)

    conn = db(current_app.config['APP_DATABASE'])
    lst = conn.run_query_result_many(c_queries.GET_TEMP, (start_date, end_date))

    check_id = lambda x: x[1] == sensor_id_checked
    result = [row for row in lst if check_id(row)]

    msg = {
	    'msg' : 'Success',
        'data' : result
    }
    return jsonify(msg), 200

@current_app.route('/temperature/<int:id>', methods=['DELETE'])
@jwt_required
def delete_temp(id):

    if id == None or id == '':
        raise APImissingParameter(400, "Missing parameters in request")

    conn = db(current_app.config['APP_DATABASE'])
    last_row = conn.run_query_non_result(c_queries.DELETE_TEMP, (id, ))
    if not isinstance(last_row, int) or last_row == -1:
        raise APIreturnError(404, name='Not found', description='Return Id from the sql database is not correct')
    
    msg = {
        'msg' : 'Success' if last_row == 0 else 'Failed',
        'data' : id
    }
    return jsonify(msg), 200

@current_app.route('/output/', methods=['POST'])
@jwt_required
def add_output():

    if (not request.is_json or
        not 'name' in request.json or
        not 'pin' in request.json or
        not 'type' in request.json or
        not 'initial_value' in request.json or
        not 'active_high' in request.json or
        not 'comment' in request.json):
        raise APImissingParameter(400, name="Bad request", description="Missing parameters in request")

    conn = db(current_app.config['APP_DATABASE'])
    last_row = conn.run_query_non_result(c_queries.CREATE_SIGNAL, 
        ())
    if not isinstance(last_row, int) or last_row == -1:
        raise APIreturnError(404, name='Not found', description='Return Id from the sql database is not correct')
    
    signal_pool[request.json.pin] = LED(request.json.pin)  # Example "GPIO17"

    msg = {
        'msg' : 'Success' if last_row != 0 else 'Failed',
        'data' : request.json.pin
    }
    return jsonify(msg), 200

@current_app.route('/output/<string:pin>', methods=['DELETE'])
@jwt_required
def remove_output(pin):
    
    if pin == None  or pin == '':
        raise APImissingParameter(400, "Missing parameter in request")

    conn = db(current_app.config['APP_DATABASE'])
    signal = conn.run_query_result_many(c_queries.GET_SIGNAL, (id, ))
    if signal.count == 1 and signal[0].int_initial == 1:
        print(signal)
        signal_pool[pin].off()
        signal_pool[pin].close()
    elif signal.count == 1 and signal[0].int_inital == 0:
        print(signal)
        signal_pool[pin].on()
        signal_pool[pin].close()
    else:
        raise APIreturnError(404, 
            name='Not found or more then one signal', 
            description='Return Id from sql database contain zero or more than one signal')
    signal_pool.pop(pin)

    msg = {
        'msg' : 'Success',
        'data' : pin
    }
    return jsonify(msg), 200

@current_app.route('/output/state', methods=['GET'])
@jwt_required
def state_all_output():
    
    conn = db(current_app.config['APP_DATABASE'])
    signals = conn.run_query_result_many(c_queries.GET_SIGNAL_ALL)
    data = {}
    for signal in signals:
        if signal.str_type == "OUTPUT":
            tmp = (signal.name, signal.pin, signal_pool[signal.str_pin].is_lit)
            data[signal.str_pin] = tmp

    msg = {
        'msg' : 'Success',
        'data' : data
    }
    return jsonify(msg), 200

@current_app.route('/output/state/<string:pin>', methods=['GET'])
@jwt_required
def state_output(pin):
    
    if pin == None  or pin == '':
        raise APImissingParameter(400, "Missing parameter in request")

    msg = {
        'msg' : 'Success',
        'data' : {pin: signal_pool[pin].is_lit}
    }
    return jsonify(msg), 200

@current_app.route('/output/state/<string:pin>/<string:state>', methods=['PUT'])
@jwt_required
def change_state_output(pin, state):
    
    if pin == None or pin == '':
        raise APImissingParameter(400, "Missing parameter in request")

    if pin in signal_pool.keys():
        if state.lower() == 'on':
            signal_pool[pin].on()
        elif state.lower() == 'off':
            signal_pool[pin].off()
        else:
            signal_pool[pin].toggle()
    else:
        raise APIfaultyParameter(400, "Signal pin does not exist")

    msg = {
        'msg' : 'Success',
        'data' : pin
    }
    return jsonify(msg), 200
