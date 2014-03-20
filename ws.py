import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado.options import define, options
import json
from sm.models import *
from datetime import datetime, timedelta
from hashlib import md5
from django.core.exceptions import ObjectDoesNotExist


##################################################
#  WEBSOCKET
##################################################

clients = []

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        clients.append(self)
        self.account = ""
        self.endpoint = ""
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] NEW CONNECTION')
        print('[INFO]')
        print('[INFO] Client IP: ' + self.request.remote_ip)
        print('[INFO] -----------------------------------------------------------------------')
    
    def on_message(self, message):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] MESSAGE RECEIVED')
        print('[INFO]')
        print('[JSON] ' + message)
        msg = json.loads(message)
        if(self.endpoint == ""):
            self.endpoint = msg['endpoint']
        print('[INFO]')
        print('[INFO] SENDER INFO')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] Account: ' + self.account)
        print('[INFO] Endpoint: ' + self.endpoint)
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] ENTER ' + msg['event'] + ' VIEW')
        print('[INFO]')
        globals()[msg['event']](self, msg['content'])
        
    def on_close(self):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] CONNECTION CLOSED')
        print('[INFO]')
        print('[INFO] CLIENT INFO')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] Account: ' + self.account)
        print('[INFO] Endpoint: ' + self.endpoint)
        print('[INFO] -----------------------------------------------------------------------')
        clients.remove(self)
        self.close()


##################################################
#  FUNCTIONS
##################################################

fmt = '%Y/%m/%d %H:%M:%S'

def pong(self, content):
    reContent = {"event": "pong",
                 "endpoint": "Server",
                 "content": {
                     "time": datetime.strftime(datetime.now(), fmt)}}
    self.write_message(json.dumps(reContent))

def login(self, content):
    try:
        account = Account.objects.get(username=content['account'],
                                      password=content['password'])
        print('[INFO] LOGIN SUCCESS')
        reContent = {'event': 'login',
                     'endpoint': 'Server',
                     'content': {
                         'status': 'success'}}
        self.account = account.username
    except ObjectDoesNotExist:
        print('[INFO] LOGIN FAILED')
        reContent = {'event': 'login',
                     'endpoint': 'Servebr',
                     'content': {
                         'status': 'failed',
                         'code': '0',
                         'reason': 'Account or Password is wrong.'}}
    self.write_message(json.dumps(reContent))
    

def profile(self, content):
    s = Student.objects.get(account=Account.objects.get(username=content['account']))
    courseList = [{"code": e.course.code,
                   "name": e.course.name,
                   "status": "unbooked",
                   "start_time": ""} for e in Enroll.objects.filter(student=s)]
    for c in courseList:
        try:
            exam = Exam.objects.get(enroll__course__code=c["code"],
                                    enroll__student=s)
        except ObjectDoesNotExist:
            exam = None
        if(exam): # if booked
            c["start_time"] = exam.timeslot.start_time
            age = datetime.strptime(c["start_time"], fmt) - datetime.now()
            if(age > timedelta(minutes=15)):
                c["status"] = "booked"
            elif(age < timedelta(0)):
                c["status"] = "finished"
        else:
            tsList = [datetime.strptime(item.start_time, fmt)
                      for item in ExamTimeslot.objects.filter(course__code=c["code"])]
            if(tsList == [] or datetime.now() > max(tsList)):
                c["status"] = "closed"
            else:
                c["start_time"] = datetime.strftime(max(tsList), fmt)
    reContent = {"event": "profile",
                 "endpoint": "Server",
                 "content": {
                     "account": content['account'],
                     "profile":  {
                         "courses": courseList
                     }
                 }
             }
    self.write_message(json.dumps(reContent))

def booking(self, content):    
    tsList = [{"start_time": item.start_time}
              for item in ExamTimeslot.objects.filter(course__code=content["code"])]
    reContent = {"event": "booking",
                 "endpoint": "Server",
                 "content": {
                     "account": content["account"],
                     "code": content["code"],
                     "examTime": tsList
                 }
             }    
    self.write_message(json.dumps(reContent))

def booked(self, content):
    exam = Exam(enroll=Enroll.objects.get(
        student=Student.objects.get(
            account=Account.objects.get(username=content["account"])),
        course=Course.objects.get(code=content["code"])),
        timeslot=ExamTimeslot.objects.get(start_time=content["examTime"]),
        invigilator=Invigilator.objects.all()[0])
    
    print('[INFO] EXAM BOOKED')
    exam.save()
    
def exam_question(self, content):
    qList = [json.loads(item.content)
             for item in ExamQuestion.objects.filter(course__code=content["code"])]
    exam = Exam.objects.get(enroll=Enroll.objects.get(
        student=Student.objects.get(account=Account.objects.get(username=content["account"])),
        course=Course.objects.get(code=content["code"])))
    reContent = {"event": "exam_question",
                 "endpoint": "Server",
                 "content": {
                     "course_code": content["code"],
                     "exam_pk": exam.pk,
                     "question_set": qList
                 }
             }
    self.write_message(json.dumps(reContent))
    
def exam_question_answer(self, content):
    for item in content["question_set"]:
        answer = Answer(exam=Exam.objects.get(pk=content["exam_pk"]),
                        question=ExamQuestion.objects.get(pk=item["pk"]),
                        answer=item["question_content"]["answer"])
        answer.save()
    reContent = {"event": "submission_message",
                 "endpoint": "Server",
                 "content": {
                     "code": "CZ0001",
                     "submission_status": "successful"
                 }
             }
    self.write_message(json.dumps(reContent))
        
def cancel(self, content):
    exam = Exam.objects.get(enroll=Enroll.objects.get(
        student=Student.objects.get(account=Account.objects.get(username=content["account"])),
        course=Course.objects.get(code=content["code"])))
    start_time = exam.timeslot.start_time
    exam.delete()
    reContent = {"event": "cancel",
                 "endpoint": "Server",
                 "content": {
                     "code": content["code"],
                     "account": content["account"],
                     "status": "successful",
                     "start_time": start_time
                 }
             }
    self.write_message(json.dumps(reContent))

def exam_chat(self, content):
    ex = Exam.objects.get(pk=content["exam_pk"])
    target = next((client for clinet in clients
                   if client.account == ex.invigilator.account.username), None)
    chat = TextChat(exam=ex, content=content["msg"], time=content["system_time"])
    chat.save()
    reContent = {}
    target.write_message(json.dumps(reContent))


##################################################
#  CONFIG
##################################################

app = tornado.web.Application([(r'/', WSHandler),])

if __name__ == '__main__':    
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8087)
    tornado.ioloop.IOLoop.instance().start()
