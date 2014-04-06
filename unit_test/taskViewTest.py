from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class taskListTest(JSONTest):

    def setUp(self):
        super().setUp()

        self.loginInfo = {"event": "login",
                          "endpoint": "Invigilator",
                          "content": {"account": "invtest",
                                      "password": "c4ca4238a0b923820dcc509a6f75849b"}
                         }
        self.logoutInfo = {"event": "logout",
                           "endpoint": "Invigilator",
                           "content": None
                       }
        self.exptInput = {"event": "profile_invigilator","endpoint": "Invigilator","content":{"account": "invigilator1"}}
        self.exptOutput = 


    def tearDown(self):
        self.exptInput['content']['account'] = "invtest"
        self.logout()



    def test_task_list_test(self):
        self.conduct_test()

if __name__ == '__main__':
   unittest.main()
