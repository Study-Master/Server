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
p2pclients = []

class JSONHandler(websocket.WebSocketHandler):
    def open(self, *args):
        clients.append(self)
        self.account = ""
        self.endpoint = ""
        self.target = ""
        self.startedExam = []
        self.inProfileView = False
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] NEW CONNECTION')
        self.show_client_info()
        print('[INFO] -----------------------------------------------------------------------')
    
    def on_message(self, message):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] MESSAGE RECEIVED')
        print('[JSON] ' + message)
        msg = json.loads(message)            
        if(self.endpoint == ""): self.endpoint = msg['endpoint']
        if(self.endpoint == "Invigilator"): self.examinee = []
        self.show_client_info()
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] ENTER ' + msg['event'] + ' VIEW')
        print('[INFO] -----------------------------------------------------------------------')
        if(msg['event'] == 'profile'): self.inProfileView = True
        else: self.inProfileView = False
        globals()[msg['event']](self, msg['content'])

    def on_close(self):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] CONNECTION CLOSED')
        self.show_client_info()
        print('[INFO] -----------------------------------------------------------------------')
        clients.remove(self)
        self.close()

    def show_client_info(self):
        print('[INFO]')
        print('[INFO] CLIENT INFO')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] Account: ' + self.account)
        print('[INFO] Endpoint: ' + self.endpoint)

class P2PHandler(websocket.WebSocketHandler):
    def open(self, *args):
        p2pclients.append(self)
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] P2P SOCKET CONNECTED')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] -----------------------------------------------------------------------')
    
    def on_message(self, message):
        print('[INFO] -----------------------------------------------------------------------')
        jsonSocket = next(c for c in clients if c.request.remote_ip == self.remote_ip)
        targetList = [pc for pc in p2pclients if pc.request.remote_ip == json.target]
        if(targetList != []):
            targetList[0].write_message(message)
            print('[EVNT] DATA SEND')
        else:
            print('[ERRO] Invigilator not found')
        print('[INFO] -----------------------------------------------------------------------')
            
    def on_close(self):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] CONNECTION CLOSED')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] -----------------------------------------------------------------------')
        p2pclients.remove(self)
        self.close()
        

##################################################
#  VIEWS
##################################################

fmt = '%Y/%m/%d %H:%M:%S'

def send_msg(self, reContent):
    print('[INFO] -----------------------------------------------------------------------')
    print('[EVNT] MESSAGE SEND')
    msg = json.dumps(reContent)
    print('[JSON] ' + msg)
    self.write_message(msg)
    print('[INFO] -----------------------------------------------------------------------')

def login(self, content):
    try:
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
                     'endpoint': 'Server',
                     'content': {
                         'status': 'failed',
                         'code': '0',
                         'reason': reason}}
    send_msg(self, reContent)

@gen.coroutine
def check_exam(self, arg):
    print('[INFO] -----------------------------------------------------------------------')
    print('[EVET] check_exam EVOKED')
    while(self.inProfileView == True):
        for course in courseList:
            try:
                exam = Exam.objects.get(enroll__student__account__username=self.account,
                                        enroll__course__code=course["code"])
            except ObjectDoesNotExist:
                exam = None
            if(exam):
                timeToExam = datetime.strptime(exam.timeslot.start_time, fmt) - datetime.now()
                event = None
                if(timeToExam < timedelta(days=3) and course["status"] == "booked"):
                    event = "cancel_disabled"
                    course["status"] = "confirmed"
                if(timeToExam < timedelta(minutes=15) and course["status"] == "confirmed"):
                    event = "exam_enabled"
                    course["status"] = "exam"
                if(timeToExam < timedelta(minutes=-15) and course["status"] == "exam"):
                    event = "exam_disabled"
                    course["status"] = "finished"
                if(event):
                    reContent = {'event': event,
                                 'endpoint': 'Server',
                                 'content': {
                                     'code': course["code"],
                                     'start_time': exam.timeslot.start_time
                                 }
                             }
                    send_msg(self, reContent)
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + 5)
    
def profile(self, content):
    courseList = [{"code": e.course.code,
                   "name": e.course.name,
                   "status": "unbooked",
                   "start_time": ""}
                  for e in Enroll.objects.filter(student__account__username=self.account)]
    for course in courseList:
        try:
            exam = Exam.objects.get(enroll__student__account__username=self.account,
                                    enroll__course__code=course["code"])
        except ObjectDoesNotExist:
            exam = None
        if(exam):
            course["status"] = "booked"
            course["start_time"] = exam.timeslot.start_time
            timeToExam = datetime.strptime(course["start_time"], fmt) - datetime.now()
            if(timeToExam < timedelta(days=3)):
                course["status"] = "confirmed"
            if(timeToExam < timedelta(minutes=15)):
                course["status"] = "exam"
            if(timeToExam < timedelta(minutes=-15)):
                course["status"] = "finished"
        else:
            tsList = [datetime.strptime(item.start_time, fmt)
                      for item in ExamTimeslot.objects.filter(course__code=course["code"])]
            if(tsList == [] or max(tsList) - datetime.now() < timedelta(days=3)):
                course["status"] = "closed"
            else:
                course["start_time"] = datetime.strftime(max(tsList), fmt)
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
    send_msg(self, reContent)
    check_exam(self, courseList)

def booking(self, content):
    tsList = [{"start_time": item.start_time}
              for item in ExamTimeslot.objects.filter(course__code=content["code"])]
    timeList = [datetime.strptime(exam.timeslot.start_time, fmt) for exam in
                Exam.objects.filter(enroll__student__account__username=self.account)]
    for ts in tsList:
        tsd = datetime.strptime(ts["start_time"], fmt)
        timeToExam = tsd - datetime.now()
        if(timeToExam < timedelta(days=3)):
            tsList.remove(ts)
        for time in timeList:
            delta = tsd - time
            if(timedelta(hours=-1) < delta < timedelta(hours=1)):
                tsList.remove(ts)
    name = Course.objects.get(code=content["code"]).name
    reContent = {"event": "booking",
                 "endpoint": "Server",
                 "content": {
                     "code": content["code"],
                     "name": name,
                     "examTime": tsList
                 }
             }
    send_msg(self, reContent)

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
    send_msg(self, reContent)
    
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
    # inv = [c for c in clients if c.account == exam.invigilator.account.username][0]
    # self.target = inv.request.remote_ip
    send_msg(self, reContent)
    
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
    send_msg(self, reContent)
        
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
    send_msg(self, reContent)

def exam_chat(self, content):
    ex = Exam.objects.get(pk=content["exam_pk"])
    chat = TextChat(exam=ex, content=content["msg"], time=content["system_time"])
    chat.save()
    # reContent = {}
    # send_msg(self, reContent)


##################################################
#  MAIN
##################################################

JSONApp = web.Application([(r'/', JSONHandler),])
VideoApp = web.Application([(r'/', P2PHandler),])
AudioApp = web.Application([(r'/', P2PHandler),])
ScreenApp = web.Application([(r'/', P2PHandler),])

if __name__ == '__main__':    
    HTTPServer(JSONApp).listen(8087)
    HTTPServer(VideoApp).listen(8080)
    HTTPServer(AudioApp).listen(8081)
    HTTPServer(ScreenApp).listen(8082)
    IOLoop.instance().add_callback(check_exam)
    IOLoop.instance().start()
