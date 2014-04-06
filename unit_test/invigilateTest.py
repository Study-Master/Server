from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class invigilateTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.examinee_login()
        self.exptInput= {"content":{"examTime": [{"start_time": "2014/04/16 15:49:00"}], "code": "CZ0001", "name": "Engineering and Society"}, "event": "booking", "endpoint": "Server"}
        self.invigilator_login()
        self.exptInput={"content":{"start_time":"2014/04/06 19:34:00","code":"CZ0001"},"event":"invigilate","endpoint":"Invigilator"}
        self.exptOutput=
    def tearDown(self):
        self.examinee_logout()
        self.invigilator_logout()

    def test_login_success(self):
        self.conduct_test()

if __name__ == '__main__':
   unittest.main()

