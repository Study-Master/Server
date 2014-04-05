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
videoclients = []
screenclients = []

class JSONHandler(websocket.WebSocketHandler):
    def open(self, *args):
        clients.append(self)
        self.account = ""
        self.endpoint = ""
        self.target = None
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
        if(msg['event'] == 'profile' or 'profile_invigilator'):
            self.inProfileView = True
        else:
            self.inProfileView = False
        if(self.endpoint == ""): self.endpoint = msg['endpoint']
        if(self.endpoint == "Invigilator"):
            self.inExamView = False
        self.show_client_info()
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] ENTER ' + msg['event'] + ' VIEW')
        print('[INFO] -----------------------------------------------------------------------')
        globals()[msg['event']](self, msg['content'])

    def on_close(self):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] CONNECTION CLOSED')
        self.show_client_info()
        print('[INFO] -----------------------------------------------------------------------')
        list_remove(clients, self.request.remote_ip)
        self.close()

    def show_client_info(self):
        print('[INFO]')
        print('[INFO] CLIENT INFO')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] Account: ' + self.account)
        print('[INFO] Endpoint: ' + self.endpoint)

class P2PHandler(websocket.WebSocketHandler):
    def open(self, *args):
        self.set_nodelay(True)
        p2pclients.append(self)
        self.endpoint = ""
        self.target = None
        self.json_target = None
        self.content_type = ""
        if(self.is_examinee()):
            self.endpoint = "Examinee"
            self.json_target = self.get_invigilator_json()
            self.target = self.get_invigilator_p2p()
            reContent = {"event": "examinee_come_in",
                         "endpoint": "Server",
                         "content": {
                             "name": self.get_examinee_json().account,
                             "type": self.content_type
                         }
                     }
            self.json_target.write_message(json.dumps(reContent))
            print('[EVNT] examinee_come_in JSON SEND')
        else:
            self.endpoint = "Invigilator"
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] P2P SOCKET CONNECTED')
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] endpoint: ' + self.endpoint)
        if(self.target):
            print('[INFO] p2p target ip: ' + self.target.request.remote_ip)
        print('[INFO] -----------------------------------------------------------------------')
        print('[DBUG] client list: ' + str([c.endpoint for c in clients]))
    
    def on_message(self, message):
        if(self.endpoint == "Examinee"):
            self.target.write_message(message, binary=True)

    def on_close(self):
        print('[INFO] -----------------------------------------------------------------------')
        print('[EVNT] CONNECTION CLOSED')
        print('[INFO] endpoint: ' + self.endpoint)
        print('[INFO] IP: ' + self.request.remote_ip)
        print('[INFO] -----------------------------------------------------------------------')
        list_remove(p2pclients, self.request.remote_ip)
        self.close()

    def is_examinee(self):
        return self.request.remote_ip in [c.request.remote_ip for c in clients
                                      if c.endpoint == "Examinee"]

    def get_examinee_json(self):
        return [c for c in clients
                if c.request.remote_ip == self.request.remote_ip
                and c.endpoint == "Examinee"][0]
    
    def get_invigilator_p2p(self):
        examineeJson = self.get_examinee_json()
        print('[DBUG] examineeJson: ' + examineeJson.target.request.remote_ip)
        print('[DBUG] p2pclients: ' + str([pc.request.remote_ip for pc in p2pclients]))
        targetList = [pc for pc in p2pclients
                      if pc.request.remote_ip == examineeJson.target.request.remote_ip]
        print('[DBUG] targetList: ' + targetList[0].request.remote_ip)
        return targetList[0]

    def get_invigilator_json(self):
        examineeJson = self.get_examinee_json()
        print('[DBUG] ENTER get_invigilator_json')
        print(clients)
        invJson = [c for c in clients
                   if c.request.remote_ip == examineeJson.target.request.remote_ip][0]
        print(invJson)
        print('[DBUG] invJson: ' + invJson.request.remote_ip)
        return invJson

# class VideoHandler(P2PHandler):

    
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
        reason = "Account or Password is wrong!"
        print('[EVET] LOGIN FAILED')
        if(type(e) == NameError):
            reason = "Your account is already logged in!"
        reContent = {'event': 'login',
                     'endpoint': 'Server',
                     'content': {
                         'status': 'failed',
                         'code': '0',
                         'reason': reason}}
    send_msg(self, reContent)

@gen.coroutine
def check_exam(self, courseList):
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
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + 3)
    print('[EVET] check_exam FINISHED')
    print('[INFO] -----------------------------------------------------------------------')

    
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

# BUG
def booking(self, content):
    tsList = [{"start_time": item.start_time}
              for item in ExamTimeslot.objects.filter(course__code=content["code"])]
    timeList = [datetime.strptime(exam.timeslot.start_time, fmt) for exam in
                Exam.objects.filter(enroll__student__account__username=self.account)]
    for ts in tsList:
        tsd = datetime.strptime(ts["start_time"], fmt)
        timeToExam = tsd - datetime.now()
        remove = False
        if(timeToExam < timedelta(days=3)):
            remove = True
        for time in timeList:
            delta = tsd - time
            if(timedelta(hours=-1) < delta < timedelta(hours=1)):
                remove = True
        if(remove): tsList.remove(ts)
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
    inv = [c for c in clients if c.account == exam.invigilator.account.username][0]
    print('[DBUG] inv ip: ' + inv.request.remote_ip)
    self.target = inv
    print('[DBUG] target ip: ' + self.target.request.remote_ip)
    send_msg(self, reContent)
    
def exam_question_answer(self, content):
    for item in content["question_set"]:
        answer = Answer(exam=Exam.objects.get(pk=content["exam_pk"]),
                        question=ExamQuestion.objects.get(pk=item["pk"]),
                        answer=item["question_content"]["answer"])
        answer.save()
    reContent = {"event": "submission_successful",
                 "endpoint": "Server",
                 "content": None
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
    reContent = {"event": "exam_chat",
                 "endpoint": self.endpoint,
                 "content": content}
    target = None
    if(self.endpoint == "Examinee"):
        target = self.target            
    else:
        target = [c for c in clients
                  if c.account == ex.enroll.student.account.username
                  and c.endpoint == "Examinee"][0]
    send_msg(target, reContent)

def profile_invigilator(self, content):
    examListRaw = [{"code": e.enroll.course.code,
                 "name": e.enroll.course.name,
                 "status": "waiting",
                 "start_time": e.timeslot.start_time}
                for e in Exam.objects.filter(invigilator__account__username=self.account)]
    examList = []
    for item in examListRaw:
        if item not in examList:
            examList.append(item)
    for exam in examList:
        timeToExam = datetime.strptime(exam["start_time"], fmt) - datetime.now()
        if(timeToExam < timedelta(minutes=15)):
            exam["status"] = "invigilate"
        if(timeToExam < timedelta(minutes=-15)):
            exam["status"] = "finished"
    reContent = {"event": "profile_invigilator",
                 "endpoint": "Server",
                 "content": {   
                     "profile": {"exams": examList}}}
    send_msg(self, reContent)
    check_invigilate(self, examList)

@gen.coroutine
def check_invigilate(self, examList):
    print('[INFO] -----------------------------------------------------------------------')
    print('[EVET] check_invigilate EVOKED')
    while(self.inProfileView):
        for exam in examList:
            timeToExam = datetime.strptime(exam["start_time"], fmt) - datetime.now()
            if(timeToExam < timedelta(minutes=15) and exam["status"] == "waiting"):
                exam["status"] = "invigilate"
                reContent = {"event": "enable_invigilation",
                             "endpoint": "Server",
                             "content": {
                                 "code": exam["code"],
                                 "start_time": exam["start_time"]
                             }
                         }
                send_msg(self, reContent)
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + 3)
    print('[EVET] check_invigilate FINISHED')
    print('[INFO] -----------------------------------------------------------------------')

def invigilate(self, content):
    self.inExamView = True
    studentList = [e.enroll.student.account.username
                   for e in Exam.objects.filter(invigilator__account__username=self.account,
                                                enroll__course__code=content["code"],
                                                timeslot__start_time=content["start_time"])]
    self.examinees = studentList

def logout(self, content):
    reContent = {"event": "logout",
                "endpoint": "Server",
                 "content": {
                     "status": "success",
                 }
             }
    send_msg(self, reContent)
    list_remove(clients, self.request.remote_ip)
    list_remove(p2pclients, self.request.remote_ip)

def list_remove(clients, ip):
    for c in clients:
        if(c.request.remote_ip == ip):
            clients.remove(c)

##################################################
#  MAIN
##################################################

JSONApp = web.Application([(r'/', JSONHandler),])
VideoApp = web.Application([(r'/', P2PHandler),])
ScreenApp = web.Application([(r'/', P2PHandler),])

if __name__ == '__main__':    
    HTTPServer(JSONApp).listen(8087)
    HTTPServer(VideoApp).listen(8080)
    HTTPServer(ScreenApp).listen(8081)
    IOLoop.instance().add_callback(check_exam)
    IOLoop.instance().add_callback(check_invigilate)
    IOLoop.instance().start()
