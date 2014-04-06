from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class submitSolution(JSONTest):

    def setUp(self):
        super().setUp()
        self.login()
        self.exptOutput = {"event": "submission_successful","endpoint": "Server","content":{}}
        self.exptInput = {"content": {"profile": {"courses": [{"status": "finished", "start_time": "2014/04/06 15:25:00", "code": "CZ0001", "name": "Engineering and Society"}]}}, "event": "profile", "endpoint": "Server"}
    
    def tearDown(self):
        self.exptInput['content']['account'] = "test"
        self.logout()
    
    def test_submit_solution(self):
        self.conduct_test()

if __name__ == '__main__':
    unittest.main()

