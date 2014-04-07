from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class taskListTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.invigilator_login()
        self.exptInput = {"event": "profile_invigilator","endpoint": "Invigilator","content":{"account": "invigilator1"}}
        self.exptOutput = {"content": {"profile": {"exams": [{"start_time": "2014/04/06 20:40:00", "code": "CZ0001", "status": "finished", "name": "Engineering and Society"}]}}, "event": "profile_invigilator", "endpoint": "Server"} 


    def tearDown(self):
        self.invigilator_logout()

    def test_task_list_test(self):
        self.conduct_test()

if __name__ == '__main__':
   unittest.main()
