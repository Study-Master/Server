from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
import json
import unittest

class JSONTest(unittest.TestCase):

    def setUp(self):
        self.url = "ws://cz2006.ciel.im:8087"
        self.exptInput = None
        self.exptOutput = None
        self.connection = None

    def read_message(self, future):
        self.assertEqual(json.loads(future.result()), self.exptOutput)
        IOLoop.instance().stop()
        
    def write_read_msg(self, future):
        self.connection = future.result()
        self.connection.write_message(json.dumps(self.exptInput))
        self.connection.read_message(callback=self.read_message)

    def write_msg_only(self, future):
        self.connection = future.result()
        self.connection.write_message(json.dumps(self.exptInput))
        IOLoop.instance().stop()

    def conduct_test(self):
        websocket_connect(self.url, callback=self.write_read_msg)
        IOLoop.instance().start()
