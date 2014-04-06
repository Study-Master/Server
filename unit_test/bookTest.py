
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class BookTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.login()
        self.exptOutput={"content": {"examTime": [{"start_time": "2014/04/16 15:49:00"}], "code": "CZ0001", "name": "Engineering and Society"}, "event": "booking", "endpoint": "Server"}
        self.exptInput= {"content":{"examTime": [{"start_time": "2014/04/16 15:49:00"}], "code": "CZ0001", "name": "Engineering and Society"}, "event": "booking", "endpoint": "Server"}

    def tearDown(self):
        self.msg = {"content": {"status": "successful", "start_time": "2014/04/16 15:49:00", "code": "CZ0001"}, "event": "cancel", "endpoint": "Server"}
        self.send_msg()
        self.logout()

    def test_book(self):
        self.conduct_test()

if __name__ == '__main__':
    unittest.main()
