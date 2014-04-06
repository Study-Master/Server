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
        self.loginInfo = None
        self.logoutInfo = None
        self.msg = None
        self.connection = None
  
    def connect(self, callback):
        websocket_connect(self.url, callback=callback)
        
    def read_and_validate_msg(self, future):
        self.assertEqual(json.loads(future.result()), self.exptOutput)
        IOLoop.instance().stop()
        
    def write_read_msg(self, future):
        self.connection = future.result()
        self.connection.write_message(json.dumps(self.exptInput))
        self.connection.read_message(callback=self.read_and_validate_msg)

    def write_msg_only(self, future, msg):
        self.connection = future.result()
        self.connection.write_message(json.dumps(msg))
        IOLoop.instance().stop()

    def conduct_test(self):
        self.connect(callback=self.write_read_msg)
        IOLoop.instance().start()

    def send_msg(self):
        self.connect(callback=partial(self.write_msg_only, msg=self.msg))

    def login(self):
        self.connect(callback=partial(self.write_msg_only, msg=self.loginInfo))
        
    def logout(self):
        self.connect(callback=partial(self.write_msg_only, msg=self.logoutInfo))

    def examinee_login(self):
        self.loginInfo = {"event": "login",
                          "endpoint": "Examinee",
                          "content": {"account": "test",
                                      "password": "c4ca4238a0b923820dcc509a6f75849b"}
                      }
        self.login()
        self.loginInfo = None

    def examinee_logout(self):
        self.logoutInfo = {"event": "logout",
                           "endpoint": "Examinee",
                           "content": None
                       }
        self.logout()
        self.logoutInfo = None

    def invigilator_login(self):
        self.loginInfo = {"event": "login",
                          "endpoint": "Invigilator",
                          "content": {"account": "invtest",
                                      "password": "c4ca4238a0b923820dcc509a6f75849b"}
                         }
        self.login()
        self.loginInfo = None
        
    def invigilator_logout(self):
        self.logoutInfo = {"event": "logout",
                           "endpoint": "Invigilator",
                           "content": None
                       }
        self.logout()
        self.logoutInfo = None
