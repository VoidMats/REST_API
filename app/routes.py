#! /usr/bin/python3

from flask import (
    Flask, 
    abort, 
    jsonify, 
    request, 
    current_app
)
from flask_jwt_extended import (
    JWTManager, 
    jwt_required, 
    create_access_token,
    get_jwt_identity
)
from app.apiexception import APIexception, APImissingParameter 
from app.db_sqlite import DB_sqlite as db

jwt = JWTManager(current_app)

# ====== ROUTES START HERE ======
# ===============================

@current_app.route('/', methods=['GET'])
def index():
    pass


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

@current_app.route('/settings', methods=['POST', 'OPTIONS'])
@jwt_required
def setup_temp():
    pass

# curl -d '{"sensor":"1", "start_date":"2020-07-01", "end_date":"2020-07-4"}' -H "Content-Type: application/json" -X GET http://localhost:5000/temperature
@current_app.route('/temperature', methods=['GET'])
@jwt_required
def get_temp():
    if (not request.is_json or 
        request.json['sensor'] or
        request.json['start_date'] or
        request.json['end_date']):
        raise APImissingParameter(400, "Missing parameters in request")

    sensor_id = request.json.get('sensor', None)
    start_date = request.json.get('start_date', None)
    end_date = request.json.get('end_date', None)

    str_values = ", ".join('id', 'int_sensor', 'real_value', 'str_date', 'str_comment')
    query = "SELECT " + str_values + " FROM " + current_app.config['APP_DATABASE'] 
    query += " WHERE str_date BETWEEN ? AND ?"
    print(query)
    conn = db(current_app.config['APP_DATABASE'])
    lst = db.run_query_result_many(query, (start_date, end_date))
    
    result = [(lambda x: x[1] == sensor_id)(row) for row in lst]
    return jsonify(result), 200

@current_app.route('/temperature', methods=['DELETE'])
@jwt_required
def delete_temp():
    
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200