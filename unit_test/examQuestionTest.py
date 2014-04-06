from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

from JSONTest import JSONTest


class examQuestionTest(JSONTest):

    def setUp(self):
        super().setUp()
        self.login()
        self.exptOutput = {"question_content":{"description":"What is the name of this course?","choices":{"d":"Engineering mathematics","b":"Engineering and society","c":"Data structure","a":"Software engineering"},"answer":""},"num":1,"type":"multi","pk":9} 
        self.exptInput = {"event": "exam_question","endpoint": "Examinee","content":{"code": "CZ0001","account": "s"}}
    
    def tearDown(self):
        self.exptInput['content']['account'] = "test"
        self.logout()
    
    def test_exam_load_success(self):
        self.conduct_test()

if __name__ == '__main__':
    unittest.main()

