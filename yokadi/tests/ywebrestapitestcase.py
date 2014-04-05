# -*- coding: UTF-8 -*-
"""
Yokadi parser test cases
@author: Benjamin Port <contact@benjaminport.fr>
@license: GPL v3 or later
"""

import unittest
import json

import testutils

from yokadi.yw import yweb


class YWebRestAPITestCase(unittest.TestCase):

    def setUp(self):
        testutils.clearDatabase()
        yweb.app.testing = True
        self.client = yweb.app.test_client()

    def testTasks(self):
        # No task
        response = self.client.get('/api/tasks')
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

        # test add method



