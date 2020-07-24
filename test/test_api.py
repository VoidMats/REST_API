
#! /bin/python3
# -*- coding: utf-8 -*-

# Adding temporarily path to enviroment
import sys
sys.path.append("../")
# Third part imports
import unittest
import requests
import time
# Our written python scripts
#from config import TestingConfig

endpoint = 'http://192.168.0.102:5045/'
#endpoint = 'http://localhost:5045/'

"""
Important note Gunicorn and Flask developement server uses different errror codes
during an error. For example wrong header will create a 404 code in Flask while in 
gunicorn it will be a 401 code.
"""

sensor_id = None
sensor_id2 = None

class TestAPI(unittest.TestCase):

     # Setup and teardown
    def setUp(self):
        print("\n===========================================")
        print("  RUNNING METHOD ", self.id().split('.')[-1])
        print("===========================================\n")
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    #===============================================================
    # RUN TESTS
    #===============================================================

    def test_0_Login(self):

        # ===== TEST WRONG METHOD =====
        url = endpoint + "auth/login"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'username':'test',
            'password':'test'
        }
        req = requests.put(url, headers=headers, json=payload)
        print("*** Answer testLogin : WRONG METHOD ***")
        print("URL: ", url)
        print("PAYLOAD: ", payload)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "auth/login"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'username':'test',
            'password':'test'
        }
        req = requests.post(url, headers=headers, json=payload)
        print("\n*** Answer testLogin : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("PAYLOAD: ", payload)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)


    def test_1_AddSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        url = endpoint + "temperature/sensor"
        req = requests.post(url)
        print("*** Answer testAddSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = endpoint + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        payload = {
            'name':'test1',
            'folder':'28-0516b501daff',
            'position':'test_position',
            'unit':'c',
            'comment':'test sensor - first'
        }
        req = requests.put(url, headers=headers, json=payload)
        print("*** Answer testAddSensor : WRONG METHOD ***")
        print("URL: ", url)
        print("PAYLOAD: ", payload)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        payload = {
            'name':'test1',
            'folder':'28-0516b501daff',
            'position':'test_position',
            'unit':'c',
            'comment':'test sensor - first'
        }
        req = requests.post(url, headers=headers, json=payload)
        print("\n*** Answer testAddSensor : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("PAYLOAD: ", payload)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 422, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.login('test', 'test')
        token = req.json()['token']

        url = endpoint + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            'name':'test1',
            'folder':'28-0516b501daff',
            'position':'test_position',
            'unit':'c',
            'comment':'test sensor - first'
        }
        req = requests.post(url, headers=headers, json=payload)
        print("*** Answer testAddSensor : WITH TOKEN ***")
        print("URL: ", url)
        print("PAYLOAD: ", payload)
        print("HEADERS: ", headers)
        print(req.text)
        global sensor_id 
        sensor_id = req.json()['sensor_id']
        self.assertEqual(req.status_code, 201, msg=req.status_code)

    def test_2_GetSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        url = endpoint + "/temperature/sensor/" + str(sensor_id)
        req = requests.get(url)
        print("*** Answer testGetSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = endpoint + "temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testGetSensor : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.get(url, headers=headers)
        print("\n*** Answer testGetSensor : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 422, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.login('test', 'test')
        token = req.json()['token']

        url = endpoint + "temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testGetSensor : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)


    def test_3_GetAllSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        url = endpoint + "/temperature/sensor"
        req = requests.get(url)
        print("*** Answer testGetAllSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = endpoint + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testGetAllSensor : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.get(url, headers=headers)
        print("\n*** Answer testGetAllSensor : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 422, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.login('test', 'test')
        token = req.json()['token']
        
        # Adding one more sensor
        url = endpoint + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            'name':'test2',
            'folder':'28-0516b501daff',
            'position':'test_position',
            'unit':'c',
            'comment':'test sensor - second'
        }
        req = requests.post(url, headers=headers, json=payload)
        global sensor_id2 
        sensor_id2 = req.json()['sensor_id']
        
        # Get all sensors
        url = endpoint + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testGetAllSensor : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)
        #self.assertEqual(req.json()['sensor'][0][0], sensor_id, req.json()['sensor'][0])
        #self.assertEqual(req.json()['sensor'][1][0], sensor_id2, req.json()['sensor'][1])

    def test_4_DeleteSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        global sensor_id
        global sensor_id2
        url = endpoint + "temperature/sensor/" + str(sensor_id)
        req = requests.delete(url)
        print("*** Answer testDeleteSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = endpoint + "temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testDeleteSensor : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.delete(url, headers=headers)
        print("\n*** Answer testDeleteSensor : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 422, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.login('test', 'test')
        token = req.json()['token']
        
        # Delete first sensor
        url = endpoint + "temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.delete(url, headers=headers)
        print("\n*** Answer testDeleteSensor : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)

        # Delete second sensor
        url = endpoint + "temperature/sensor/" + str(sensor_id2)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.delete(url, headers=headers)
        self.assertEqual(req.status_code, 200, msg=req.status_code)

        # Get all sensors
        url = endpoint + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testGetAllSensor : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)
        self.assertEqual(len(req.json()['sensor']), 0)

    def test_5_EventpoolStart(self):

        # ===== TEST WITH WRONG HEADER =====
        url = endpoint + "temperature/start/2"
        req = requests.get(url)
        print("*** Answer testEventpoolStart : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = endpoint + "temperature/start/2"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testEventpoolStart : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "temperature/start/2"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.get(url, headers=headers)
        print("\n*** Answer testEventpoolStart : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 422, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.login('test', 'test')
        token = req.json()['token']

        url = endpoint + "temperature/start/2"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testEventpoolStart : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)

        # Sleep for 11 s
        print("We will sleep for 11 s. Please check server that test_function has been triggered")
        time.sleep(11)

    
    def test_6_EventpoolStop(self):

        # ===== TEST WITH WRONG HEADER =====
        url = endpoint + "temperature/stop"
        req = requests.get(url)
        print("*** Answer testEventpoolStop : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = endpoint + "temperature/stop"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testEventpoolStop : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "temperature/stop"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.get(url, headers=headers)
        print("\n*** Answer testEventpoolStop : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 422, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.login('test', 'test')
        token = req.json()['token']

        url = endpoint + "temperature/stop"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testEventpoolStartStop : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)

    def test_7_ReadTemp(self):

        # ====== ADDING ONE SENSOR ======
        req = self.login('test', 'test')
        token = req.json()['token']

        url = endpoint + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            'name':'test1',
            'folder':'28-0516b501daff',
            'position':'test_position',
            'unit':'c',
            'comment':'test sensor - first'
        }
        req = requests.post(url, headers=headers, json=payload)
        print("*** Answer testReadTemp - Adding sensor : WITH TOKEN ***")
        print("URL: ", url)
        print("PAYLOAD: ", payload)
        print("HEADERS: ", headers)
        print(req.text)
        global sensor_id 
        sensor_id = req.json()['sensor_id']
        self.assertEqual(req.status_code, 201, msg=req.status_code)

        # ===== TEST WITH WRONG HEADER =====
        url = endpoint + "temperature/read/" + str(sensor_id)
        req = requests.get(url)
        print("*** Answer testReadTemp : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = endpoint + "temperature/read/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testReadTemp : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = endpoint + "temperature/read/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.get(url, headers=headers)
        print("\n*** Answer testReadTemp : WITHOUT TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 422, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        url = endpoint + "temperature/read/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testReadTemp : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)


    #===============================================================
    # INTERNAL METHODS
    #===============================================================

    def login(self, user, pwd) -> requests:
        url = endpoint + "auth/login"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'username':user, 
            'password':pwd
        }
        return requests.post(url, headers=headers, json=payload)
 
    

# Run REST_quality unittest
if __name__ == '__main__':
    unittest.main()


