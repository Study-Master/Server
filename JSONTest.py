from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest
from functools import partial

class JSONTest(unittest.TestCase):

    def setUp(self):
        self.url = "ws://cz2006.ciel.im:8087"
        self.exptInput = None
        self.exptOutput = None
        self.connection = None
        self.loginInfo = {"event": "login",
                          "endpoint": "Examinee",
                          "content": {"account": "test",
                                      "password": "c4ca4238a0b923820dcc509a6f75849b"}
                         }
        self.logoutInfo = {"event": "logout",
                           "endpoint": "Examinee",
                           "content": None
                       }
        
    def read_message(self, future):
        self.assertEqual(json.loads(future.result()), self.exptOutput)
        IOLoop.instance().stop()
        
    def write_read_msg(self, future):
        self.connection = future.result()
        self.connection.write_message(json.dumps(self.exptInput))
        self.connection.read_message(callback=self.read_message)

    def write_msg_only(self, future, msg):
        self.connection = future.result()
        self.connection.write_message(json.dumps(msg))
        IOLoop.instance().stop()

    def conduct_test(self):
        websocket_connect(self.url, callback=self.write_read_msg)
        IOLoop.instance().start()

    def login(self):
        websocket_connect(self.url, callback=partial(self.write_msg_only, msg=self.loginInfo))

    def logout(self):
        websocket_connect(self.url, callback=partial(self.write_msg_only, msg=self.logoutInfo))
