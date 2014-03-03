import tornado.ioloop
import tornado.web
import tornado.websocket

import json

clients = []

# class IndexHandler(tornado.web.RequestHandler):
#     @tornado.web.asynchronous
#     def get(request):
#         request.render("index.html")

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print("open", "WebSocketChatHandler")
        print(self.request.connection.stream.socket.getsockname())
        clients.append(self)

    def on_message(self, message):     
        print(message)
        msg = json.loads(message)
        event = msg['event']

        if(event == 'login'): login(self, msg['content']);
      
        # for client in clients:
        #     client.write_message(message)
      
    def on_close(self):
        print("webSocket closed")
        clients.remove(self)
        
def login(self, msg):
    if(msg['account'] == 'studymaster' and
       msg['password'] == 'e807f1fcf82d132f9bb018ca6738a19f'):
        print('---Login Success---')
        reContent = {'event': 'login',
                     'endpoint': 'Server',
                     'content':{
                         'status': 'success'}}
    else:
        print('---Login Failed---')
        reContent = {'event': 'login',
                     'endpoint': 'Server',
                     'content':{
                         'status': 'failed',
                         'code': '0',
                         'reason': 'Account or Password is wrong.'}}
        
    self.write_message(json.dumps(reContent))
            

app = tornado.web.Application([(r'/', WebSocketChatHandler)])


app.listen(8080)
tornado.ioloop.IOLoop.instance().start()
