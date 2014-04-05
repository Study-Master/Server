from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class LoginTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.exptOutput = {'event': 'login',
                           'endpoint': 'Server',
                           'content': {
                               'status': 'success'}}
        self.exptInput = {"event": "login",
                          "endpoint": "Examinee",
                          "content": {
                              "account": "d",
                              "password": "c4ca4238a0b923820dcc509a6f75849b"
                          }}

    def test_login_success(self):
        self.conduct_test()

    def test_login_failure_alreadyloggedin(self):
        self.exptOutput =  {'event': 'login',
                            'endpoint': 'Server',
                            'content': {
                                'status': 'failed',
                                'code': '0',
                                'reason': "Your account is already logged in!"}}
        websocket_connect(self.url, callback=self.write_msg_only)
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
