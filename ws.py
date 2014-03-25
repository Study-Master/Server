from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado import web
from tornado import websocket
from tornado import gen
from sm.models import *
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
import time
import json

##################################################
#  WEBSOCKET APPS
##################################################

clients = []
fclients = []

class JSONHandler(websocket.WebSocketHandler):
    def open(self, *args):
        clients.append(self)
        self.account = ""
        self.endpoint = ""
        self.target = ""
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] NEW CONNECTION')
        showClientInfo(self)
        print('[INFO] -----------------------------------------------------------------------')
    
    def on_message(self, message):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] MESSAGE RECEIVED')
        print('[INFO]')
        print('[JSON] ' + message)
        msg = json.loads(message)            
        if(self.endpoint == ""): self.endpoint = msg['endpoint']
        if(self.endpoint == "Invigilator"): self.examinee = []
        showClientInfo(self)
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] ENTER ' + msg['event'] + ' VIEW')
        print('[INFO]')
        if(msg['endpoint'] == 'Invigilator'): invigilator = self
        globals()[msg['event']](self, msg['content'])

    def on_close(self):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] CONNECTION CLOSED')
        showClientInfo(self)
        print('[INFO] -----------------------------------------------------------------------')
        clients.remove(self)
        self.close()

class ForwardHandler(websocket.WebSocketHandler):
    def open(self, *args):
        fclients.append(self)
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] FORWORD SOCKET CONNECTED')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] -----------------------------------------------------------------------')
    
    def on_message(self, message):
        print('[INFO] -----------------------------------------------------------------------')
        jsonSocket = next(c for c in clients if c.request.remote_ip == self.remote_ip)
        if([fc for fc in fclients if fc.request.remote_ip == json.target] != []):
            target = [fc for fc in fclients if fc.request.remote_ip == jsonSocket.target][0]
            target.write_message(message)
            print('[EVNT] DATA SEND')
        else:
            print('[ERRO] Invigilator not found')
        print('[INFO] -----------------------------------------------------------------------')
            
    def on_close(self):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] CONNECTION CLOSED')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] -----------------------------------------------------------------------')
        fclients.remove(self)
        self.close()
        

##################################################
#  VIEWS
##################################################

fmt = '%Y/%m/%d %H:%M:%S'

def showClientInfo(self):
    print('[INFO]')
    print('[INFO] CLIENT INFO')
    print('[INFO] IP: ' + self.request.remote_ip)
    print('[INFO] Account: ' + self.account)
    print('[INFO] Endpoint: ' + self.endpoint)

def sendMsg(self, reContent):
    print('[INFO] -----------------------------------------------------------------------')
    print('[EVNT] MESSAGE SEND')
    msg = json.dumps(reContent)
    print('[JSON] ' + msg)
    self.write_message(msg)
    print('[INFO] -----------------------------------------------------------------------')

def pong(self, content):
    reContent = {"event": "pong",
                 "endpoint": "Server",
                 "content": {
                     "time": datetime.strftime(datetime.now(), fmt)}}
    sendMsg(self, reContent)
    
def login(self, content):
    try:
        # next(client for client in clients
        #      if client.account == content['account'])
        if([client for client in clients
            if client.account == content['account']] != []):
            raise NameError('error')
        account = Account.objects.get(username=content['account'],
                                      password=content['password'])
        print('[INFO] LOGIN SUCCESS')
        reContent = {'event': 'login',
                     'endpoint': 'Server',
                     'content': {
                         'status': 'success'}}
        self.account = account.username
    except (ObjectDoesNotExist, NameError) as e:
        reason = ""
        print('[INFO] LOGIN FAILED')
        if(type(e) == NameError):
            reason = "Your account is already logged in!"
        if(type(e) == ObjectDoesNotExist):
            reason = "Account or Password is wrong!"
        reContent = {'event': 'login',
                     'endpoint': 'Servebr',
                     'content': {
                         'status': 'failed',
                         'code': '0',
                         'reason': reason}}
    sendMsg(self, reContent)

@gen.coroutine
def checkExam(self, bList):
    cancelList = []
    confirmList = []
    blockList = []
    while(True):
        examList = Exam.objects.filter(enroll__student__account__username=self.account)
        for exam in examList:
            timeToExam = datetime.strptime(exam.timeslot.start_time, fmt) - datetime.now()
            if(exam.enroll.course.code not in bList):
                event = None
                if(timeToExam < timedelta(minutes=-15) and exam.pk not in blockList):
                    event = "exam_disabled"
                    blockList.append(exam.pk)
                if(timeToExam < timedelta(minutes=15) and exam.pk not in confirmList):
                    event = "exam_enabled"
                    confirmList.append(exam.pk)
                if(timeToExam < timedelta(days=3) and exam.pk not in cancelList):
                    event = "cancel_disabled"
                    cancelList.append(exam.pk)
                if(event):
                    reContent = {'event': event,
                                 'endpoint': 'Server',
                                 'content': {
                                     'code': exam.enroll.course.code,
                                     'start_time': exam.timeslot.start_time
                                 }
                             }
                    sendMsg(self, reContent)
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + 5)
    
def profile(self, content):
    s = Student.objects.get(account=Account.objects.get(username=self.account))
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
        if(exam):
            c["status"] = "booked"
            c["start_time"] = exam.timeslot.start_time
            if(datetime.strptime(c["start_time"], fmt) - datetime.now() < timedelta(0)):
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
                     "profile": {
                         "courses": courseList
                     }
                 }
             }
    bList = [course["code"] for course in courseList 
             if course["status"] == "closed" or course["status"] == "finished"]
    sendMsg(self, reContent)
    checkExam(self, bList)

def booking(self, content):    
    tsList = [{"start_time": item.start_time}
              for item in ExamTimeslot.objects.filter(course__code=content["code"])]
    reContent = {"event": "booking",
                 "endpoint": "Server",
                 "content": {
                     "code": content["code"],
                     "examTime": tsList
                 }
             }
    sendMsg(self, reContent)

def booked(self, content):
    exam = Exam(enroll=Enroll.objects.get(
        student=Student.objects.get(
            account=Account.objects.get(username=self.account)),
        course=Course.objects.get(code=content["code"])),
        timeslot=ExamTimeslot.objects.get(start_time=content["start_time"],
                                          course__code=content["code"]),
        invigilator=Invigilator.objects.all()[0])
    print('[INFO] EXAM BOOKED')
    exam.save()
    reContent = {"event": "booked",
                 "endpoint": "Server",
                 "content": {
                     "status": "success"
                 }
             }
    sendMsg(self, reContent)
    
def exam_question(self, content):
    qList = [json.loads(item.content)
             for item in ExamQuestion.objects.filter(course__code=content["code"])]
    exam = Exam.objects.get(enroll=Enroll.objects.get(
        student=Student.objects.get(account=Account.objects.get(username=self.account)),
        course=Course.objects.get(code=content["code"])))
    reContent = {"event": "exam_question",
                 "endpoint": "Server",
                 "content": {
                     "course_code": content["code"],
                     "exam_pk": exam.pk,
                     "question_set": qList
                 }
             }
    inv = [c for c in client if c.account == exam.invigilator.account.username][0]
    self.target = inv.request.remote_ip
    sendMsg(self, reContent)
    
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
    sendMsg(self, reContent)
        
def cancel(self, content):
    exam = Exam.objects.get(enroll=Enroll.objects.get(
        student=Student.objects.get(account=Account.objects.get(username=self.account)),
        course=Course.objects.get(code=content["code"])))
    start_time = exam.timeslot.start_time
    exam.delete()
    reContent = {"event": "cancel",
                 "endpoint": "Server",
                 "content": {
                     "code": content["code"],
                     "status": "successful",
                     "start_time": start_time
                 }
             }
    sendMsg(self, reContent)

def exam_chat(self, content):
    ex = Exam.objects.get(pk=content["exam_pk"])
    chat = TextChat(exam=ex, content=content["msg"], time=content["system_time"])
    chat.save()
    # reContent = {}
    # sendMsg(self, reContent)


##################################################
#  MAIN
##################################################

JSONApp = web.Application([(r'/', JSONHandler),])
VideoApp = web.Application([(r'/', ForwardHandler),])
AudioApp = web.Application([(r'/', ForwardHandler),])
ScreenApp = web.Application([(r'/', ForwardHandler),])

if __name__ == '__main__':    
    HTTPServer(JSONApp).listen(8087)
    HTTPServer(VideoApp).listen(8080)
    HTTPServer(AudioApp).listen(8081)
    HTTPServer(ScreenApp).listen(8082)
    IOLoop.instance().add_callback(checkExam)
    IOLoop.instance().start()
