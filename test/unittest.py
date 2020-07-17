
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
        payload = {
            'recipe_id' : 1,
            'start_date' : '2019-01-01 00:00:00',
            'end_date' : '2019-01-25 23:00:00'
        }
        req = requests.get(url, json=payload)
        print("*** Answer from test_0_quality_data : quality data WRONG HEADER ***")
        print(req.text)
        self.assertEqual(req.status_code, 400, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = c.ENDPOINT_QUALITY["HOST"] + ':' + str(c.ENDPOINT_QUALITY["PORT"]) + "/quality/data"
        payload = {
            'recipe_id' : 1,
            'start_date' : '2019-01-01 00:00:00',
            'end_date' : '2019-01-25 23:00:00'
        }
        req = requests.put(url, json=payload)
        print("*** Answer from test_0_quality_data : quality data WRONG METHOD ***")
        print(req.text)
        self.assertEqual(req.status_code, 405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        req = self.quality_data("", 9, '2019-01-01 00:00:00', '2019-01-25 23:00:00')
        print("*** Answer from test_0_quality_data : quality data WITHOUT TOKEN ***")
        print(req.text)
        self.assertEqual(req.status_code, 404, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.quality_data(c.ENDPOINT_API['TOKEN'], 9, '2019-01-01 00:00:00', '2019-01-25 23:00:00')
        print("*** Answer from test_0_quality_data : quality data WITH TOKEN ***")
        print(req.text)
        self.assertEqual(req.status_code, 200, msg=req.status_code)

    def test_4_sample(self):

        num = 4

        # all test  methods are for insert of sample
        # ===== TEST WITH WRONG HEADER =====
        url = c.ENDPOINT_QUALITY["HOST"] + ':' + str(c.ENDPOINT_QUALITY["PORT"]) + "/quality/sample/" + str(1)
        print(url)
        payload = {
            'xbar_x1_ucl':6.5, 'xbar_x1_lcl':3.5,
            'xbar_x2_ucl':7.5, 'xbar_x2_lcl':2.5,
            'xbar_x3_ucl':8.5, 'xbar_x3_lcl':1.5,
            'xbar_r1_ucl':6.6, 'xbar_r1_lcl':4.4,
            'xbar_r2_ucl':7.7, 'xbar_r2_lcl':3.3,
            'xbar_r3_ucl':8.8, 'xbar_r3_lcl':2.2,
            's_x1_ucl':3.0, 's_x1_lcl':2.0,
            's_x2_ucl':4.0, 's_x2_lcl':1.5,
            's_x3_ucl':6.0, 's_x3_lcl':1.0,
            'R_r1_ucl':9.5, 'R_r1_lcl':5.0,
            'R_r2_ucl':10.5, 'R_r2_lcl':3.0,
            'R_r3_ucl':11.5, 'R_r3_lcl':1.0,
            'xbar_center':6.3,
            's_center':2.5,
            'R_center':7.0
        }
        req = requests.post(url)
        print("*** Answer from test_{}_sample : insert sample WRONG HEADER ***".format(num))
        print(req.text)
        self.assertEqual(req.status_code, 400, msg=req.status_code)

        # ===== TEST WRONG METHOD =====
        url = c.ENDPOINT_QUALITY["HOST"] + ':' + str(c.ENDPOINT_QUALITY["PORT"]) + "/quality/sample/" + str(1)
        req = requests.put(url)
        print("*** Answer from test_{}_sample : insert sample WRONG METHOD ***".format(num))
        print(req.text)
        self.assertEqual(req.status_code, 405, msg=req.status_code)

        # ===== TEST WITHOUT TOKEN =====
        req = self.add_sample("", 1)
        print("*** Answer from test_{}_sample : insert sample WITHOUT TOKEN ***".format(num))
        print(req.text)
        self.assertEqual(req.status_code, 404, msg=req.status_code)

        # ===== TEST WITH TOKEN =====
        req = self.add_sample(c.ENDPOINT_API['TOKEN'], 9)
        print("*** Answer from test_{}_sample : insert sample WITH TOKEN ***".format(num))
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

    # ========== RECIPE HELP FUNCTIONS ===========

    def add_recipe(self, token) -> requests:
        url = c.ENDPOINT_QUALITY["HOST"] + ':' + str(c.ENDPOINT_QUALITY["PORT"]) + "/quality/recipe"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {0}'.format(token)}
        payload = {
            "parameter":1,
            "interval":1,
            "samples":7,
            "no_samples":5
        }
        return requests.post(url, json=payload, headers=headers)

 
    

# Run REST_quality unittest
if __name__ == '__main__':
    unittest.main()


