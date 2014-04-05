from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

URL = "ws://cz2006.ciel.im:8087"

class LoginTest(unittest.TestCase):
    
    def setUp(self):
        self.url = "ws://cz2006.ciel.im:8087"
        self.exptOutput = {'event': 'login',
                           'endpoint': 'Server',
                           'content': {
                               'status': 'success'}}
        self.exptInput = {"event": "login",
                          "endpoint": "Examinee",
                          "content": {
                              "account": "s",
                              "password": "c4ca4238a0b923820dcc509a6f75849b"
                          }}
        
    def test_login_success(self):
        
        def callback(future):
                connection = future.result()
                connection.write_message(json.dumps(self.exptInput))
                connection.read_message(callback=read_message)

        def read_message(future):
            exptOutput = {'event': 'login',
                          'endpoint': 'Server',
                          'content': {
                              'status': 'success'}}
            self.assertEqual(json.loads(future.result()), self.exptOutput)
            IOLoop.instance().stop()
            
        client = websocket_connect(self.url, callback=callback)
        IOLoop.instance().start()


if __name__ == '__main__':
    unittest.main()
