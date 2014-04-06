from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class courselistTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.login()
        self.exptInput = {'event': 'profile',
                           'endpoint': 'Examinee',
                           'content': {
                            'account': 'test'}}
        self.exptOutput = {"endpoint": "Server", "content": {"profile": {"courses": [{"name": "Software Engineering", "start_time": "2014/04/05 20:58:00", "code": "CZ2006", "status": "finished"}, {"name": "Operating System", "start_time": "2014/03/24 15:00:00", "code": "CZ2005", "status": "finished"}, {"name": "Human Computer Interaction", "start_time": "2014/04/03 14:00:00", "code": "CZ2004", "status": "finished"}, {"name": "Data Structure", "start_time": "2014/03/30 14:45:00", "code": "CZ2007", "status": "finished"}, {"name": "Human Relationship", "start_time": "2014/04/30 15:00:00", "code": "HS8009", "status": "unbooked"}, {"name": "Algorithm", "start_time": "2014/04/30 15:00:00", "code": "CZ2001", "status": "booked"}, {"name": "Graphics", "start_time": "2014/04/30 15:00:00", "code": "CZ2003", "status": "booked"}, {"name": "Great Ideas in Computing", "start_time": "2014/04/30 09:00:00", "code": "CZ1004", "status": "booked"}, {"name": "Engineering Math", "start_time": "2014/05/02 09:00:00", "code": "CZ1008", "status": "booked"}, {"name": "Discrete Math", "start_time": "2014/03/29 12:39:00", "code": "CZ1001", "status": "finished"}]}}, "event": "profile"}
    
    def tearDown(self):
        self.logout()

    def test_courselist_success(self):
        self.conduct_test()

if __name__ =='__main__':
    unittest.main()
