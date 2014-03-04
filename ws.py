import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado.options import define, options

import json

from sm.models import *

clients = []

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print('---New Connection---')
        print(self.request.connection.stream.socket.getsockname())
        clients.append(self)
        print(str(self))

    def on_message(self, message):     
        print(message)
        msg = json.loads(message)
        event = msg['event']

        if(event == 'login'): login(self, msg['content']);
      
        # for client in clients:
        #     client.write_message(message)
      
    def on_close(self):
        print('---Connection Closed---')
        clients.remove(self)
        self.close()
        
def login(self, msg):
    if(Account.objects.get(username=msg['account'], password=msg['password'])):
        print('---Login Success---')
        reContent = {'event': 'login',
                     'endpoint': 'Server',
                     'content':{
                         'status': 'success'}}
    else:
        print('---Login Failed---')
        reContent = {'event': 'login',
                     'endpoint': 'Servebr',
                     'content':{
                         'status': 'failed',
                         'code': '0',
                         'reason': 'Account or Password is wrong.'}}
        
    self.write_message(json.dumps(reContent))
            

app = tornado.web.Application([
    (r'/', WebSocketChatHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8087)
    tornado.ioloop.IOLoop.instance().start()
