import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado.options import define, options

import json

from sm.models import *

from datetime import datetime, timedelta
from hashlib import md5

clients = []

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print('---New Connection---')
        print(self.request.connection.stream.socket.getsockname())
        clients.append(self)
        print(str(self))
        print(clients)

    def on_message(self, message):     
        print(message)
        msg = json.loads(message)
        globals()[msg['event']](self, msg['content'])
      
    def on_close(self):
        print('---Connection Closed---')
        clients.remove(self)
        self.close()



##################################################
#  FUNCTIONS
##################################################

fmt = '%Y/%m/%d %H:%M:%S'

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

def profile(self, msg):
    now = datetime.now()
    s = Student.objects.get(account=Account.objects.get(username=msg['account']))

    courseList = [{"code": e.course.code,
                   "name": e.course.name,
                   "status": "unbooked",
                   "start_time": None} for e in Enroll.objects.filter(student=s)]

    for c in courseList:
        exam = Exam.objects.get(enroll__course__pk=c.pk)
        if(exam):
            c["start_time"] = exam.timeslot.start_time
            age = datetime.now() - datetime.strptime(c["start_time"], fmt)
            if(timedelta(minutes=15) < age < timedelta(days=3)):
                c["status"] = "booked"
            elif(age < 0):
                c["status"] = "finished"
        elif(now > max(ExamTimeslot.objects.filter(course=c))):
            c["status"] = "closed"

    
    reContent = {"event": "profile",
                 "endpoint": "Server",
                 "content": {
                     "account": msg['account'],
                     "profile":  {
                         "courses": courseList
                     }
                 }
             }
    
    self.write_message(json.dumps(reContent))

    
##################################################
#  CONFIG
##################################################


app = tornado.web.Application([
    (r'/', WebSocketChatHandler),
])

if __name__ == '__main__':
    
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8087)
    tornado.ioloop.IOLoop.instance().start()
