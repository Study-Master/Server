from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class cancelBookTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.login() 
        self.msg={"event": "booking", "endpoint": "Examinee", "content": { "code": "CZ2001", "account": "test"}}
        self.send_msg()
        self.exptInput = {"content": {"status": "successful", "start_time": "2014/04/16 15:49:00", "code": "CZ0001"}, "event": "cancel", "endpoint": "Server"}
        self.exptOutput ={"content": {"status": "successful", "start_time": "2014/04/16 15:49:00", "code": "CZ0001"}, "event": "cancel", "endpoint": "Server"}
    
    def tearDown(self):
        self.logout()

    def test_cancel_book(self):
        self.conduct_test()


if __name__ == '__main__':
    unittest.main()
