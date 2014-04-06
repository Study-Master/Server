from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class examineeLoginTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.exptInput = {"event": "login",
                          "endpoint": "Examinee",
                          "content": {"account": "test",
                                      "password": "c4ca4238a0b923820dcc509a6f75849b"}
                         }

    def tearDown(self):
        self.exptInput['content']['account'] = "test"
        self.logout()


    def test_login_success(self):
        self.exptOutput = {'event': 'login',
                           'endpoint': 'Server',
                           'content': {'status': 'success'}
                       }
        self.conduct_test()

    def test_login_failure_alreadyloggedin(self):
        self.exptOutput =  {'event': 'login',
                            'endpoint': 'Server',
                            'content': {
                                'status': 'failed',
                                'code': '0',
                                'reason': "Your account is already logged in!"}}
        self.login()
        self.conduct_test()

    def test_login_failure_wronginfo(self):
        self.exptInput['content']['account'] = "X"
        self.exptOutput =  {'event': 'login',
                            'endpoint': 'Server',
                            'content': {
                                'status': 'failed',
                                'code': '0',
                                'reason': "Account or Password is wrong!"}}
        self.conduct_test()

if __name__ == '__main__':
   unittest.main()