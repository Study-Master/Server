import unittest
import json
import websocket
import ws
import tornado.websocket
from tornado import testing
from tornado import web
from tornado.ioloop import IOLoop
from functools import partial


class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        self.write_message(message)

class WebSocketTest(testing.AsyncHTTPTestCase):
    def get_app(self):
        return web.Application([(r'/', EchoWebSocketHandler),])

    def get_protocol(self):
        return 'ws'

    def test_login_success(self):
        _self = self

        # tornado.websocket.websocket_connect(
        #     self.get_url('/'),
        #     io_loop=self.io_loop,
        #     callback=self.stop)
        # self.wait()
        # self.assertEquals(message)
        
        class WSClient(websocket.WebSocket):
            def on_open(self):
                msg = {"event": "login",
                           "endpoint": "Java Client",
                           "content": {
                               "account": "s",
                               "password": "c4ca4238a0b923820dcc509a6f75849b"
                           }}
                ws.login(self, msg['content'])
                
            def on_message(self, message):
                reContent = {'event': 'login',
                             'endpoint': 'Server',
                             'content': {
                                 'status': 'success'}}
                _self.assertEquals(message, json.loads(reContent))
                _self.io_loop.add_callback(_self.stop)

        self.io_loop.add_callback(partial(WSClient, self.get_url('/'), self.io_loop))
        self.wait()

# class AsyncTest(unittest.TestCase):
#     pass

if __name__ == '__main__':
    unittest.main()


