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

def pong(self, content):
    reContent = {"event": "pong",
                 "endpoint": "Server",
                 "content": {
                     "time": datetime.strftime(datetime.now(), fmt)}}

    self.write_message(json.dumps(reContent))

def login(self, content):
    if(Account.objects.get(username=content['account'], password=content['password'])):
        print('---Login Success---')
        reContent = {'event': 'login',
                     'endpoint': 'Server',
                     'content': {
                         'status': 'success'}}
    else:
        print('---Login Failed---')
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
            exam = Exam.objects.get(enroll__course__code=c["code"])
        except ObjectDoesNotExist:
            exam = None
        if(exam): # if booked
            c["start_time"] = exam.timeslot.start_time
            if(datetime.strptime(c["start_time"], fmt) - datetime.now()
               > timedelta(minutes=15)):
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
        account=Account.objects.get(username=content["account"]))),
        timeslot=ExamTimeslot.objects.get(start_time=content["start_time"]),
        invigilator=Invigilator.objects.all()[0])
    print("---exam booked---")
    exam.save()
    
    

def exam_question(self, content):
    qList = [json.loads(item.content)
             for item in ExamQuestion.objects.filter(course__code=content["code"])]

    exam = Exam.objects.get(
        enroll=Enroll.objects.get(student=Student.objects.get(account=content["account"])),
        timeslot=ExamTimeslot.objects.get(start_time=content["start_time"]))

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
    


    
##################################################
#  CONFIG
##################################################

app = tornado.web.Application([(r'/', WebSocketChatHandler),])

if __name__ == '__main__':    
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8087)
    tornado.ioloop.IOLoop.instance().start()
