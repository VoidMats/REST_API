
#! /bin/python3
# -*- coding: utf-8 -*-

# Adding temporarily path to enviroment
import sys
sys.path.append("../")
# Third part imports
import unittest
import requests
# Our written python scripts
from config import TestingConfig

"""
Important note Gunicorn and Flask developement server uses different errror codes
during an error. For example wrong header will create a 404 code in Flask while in 
gunicorn it will be a 401 code.
"""

sensor_id = None

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

    def testAddSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor"
        req = requests.post(url)
        print("*** Answer testAddSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = TestingConfig.ENDPOINT_API + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        payload = {
            'name':'test1',
            'folder':'28-00006637696',
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
        url = TestingConfig.ENDPOINT_API + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        payload = {
            'name':'test1',
            'folder':'28-00006637696',
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

        url = TestingConfig.ENDPOINT_API + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            'name':'test1',
            'folder':'28-00006637696',
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

    def testGetSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor/" + str(sensor_id)
        req = requests.get(url)
        print("*** Answer testGetSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = TestingConfig.ENDPOINT_API + "temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testGetSensor : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = TestingConfig.ENDPOINT_API + "temperature/sensor/" + str(sensor_id)
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

        url = TestingConfig.ENDPOINT_API + "/temperature/sensor/" + str(sensor_id)
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testGetSensor : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)


    def testGetAllSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor"
        req = requests.get(url)
        print("*** Answer testGetAllSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = TestingConfig.ENDPOINT_API + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testGetAllSensor : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = TestingConfig.ENDPOINT_API + "temperature/sensor"
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
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            'name':'test2',
            'folder':'28-00006637697',
            'position':'test_position',
            'unit':'c',
            'comment':'test sensor - second'
        }
        requests.post(url, headers=headers, json=payload)
        
        # Get all sensors
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testGetAllSensor : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)

    def testDeleteSensor(self):

        # ===== TEST WITH WRONG HEADER =====
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor/" + str(sensor_id)
        req = requests.delete(url)
        print("*** Answer testGetAllSensor : WRONG HEADER ***")
        print("URL: ", url)
        print("ANSWER: ", req.text)
        self.assertEqual(req.status_code, 401, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = TestingConfig.ENDPOINT_API + "temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format('')}
        req = requests.put(url, headers=headers)
        print("*** Answer testGetAllSensor : WRONG METHOD ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code,405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        url = TestingConfig.ENDPOINT_API + "temperature/sensor"
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
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            'name':'test2',
            'folder':'28-00006637697',
            'position':'test_position',
            'unit':'c',
            'comment':'test sensor - second'
        }
        requests.post(url, headers=headers, json=payload)
        
        # Get all sensors
        url = TestingConfig.ENDPOINT_API + "/temperature/sensor"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        req = requests.get(url, headers=headers)
        print("*** Answer testGetAllSensor : WITH TOKEN ***")
        print("URL: ", url)
        print("HEADERS: ", headers)
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)

    #===============================================================
    # INTERNAL METHODS
    #===============================================================

    def quality_data(self, token, recipe_id, start, end) -> requests:
        url = c.ENDPOINT_QUALITY["HOST"] + ':' + str(c.ENDPOINT_QUALITY["PORT"]) + "/quality/data"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            'recipe_id' : recipe_id,
            'start_date' : start,
            'end_date' : end
        }
        return requests.get(url, headers=headers, json=payload)

    def login(self, user, pwd) -> requests:
        url = TestingConfig.ENDPOINT_API + "/auth/login"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'username':user, 
            'password':pwd
        }
        return requests.post(url, headers=headers, json=payload)
 
    

# Run REST_quality unittest
if __name__ == '__main__':
    unittest.main()


