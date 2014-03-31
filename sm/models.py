from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta

fmt = '%Y/%m/%d %H:%M:%S'

class Account(models.Model):
    username = models.CharField(max_length=15)
    password = models.CharField(max_length=32)

class User(models.Model):
    account = models.ForeignKey(Account)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    
class Student(User):
    matric_num = models.CharField(max_length=9)
    profile_pic = models.ImageField(upload_to = 'pic_folder', default = 'pic_folder/None/no-img.jpg')

class Invigilator(User): pass

class Course(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=30)

    def get_exam(self, account):
        try:
            exam = Exam.objects.get(enroll__student__account__username=account,
                                    enroll__course__code=self.code)
        except ObjectDoesNotExist:
            exam = None

    def get_examinee_status(self, account):
        exam = self.get_exam(account)
        if(exam):
            result = "booked"
            if(exam.get_examinee_status()):
                result = exam.get_examinee_status()
        else:
            tsList = [datetime.strptime(item.start_time, fmt)
                      for item in ExamTimeslot.objects.filter(course__code=self.code)]
            if(tsList == [] or max(tsList) - datetime.now() < timedelta(days=3)):
                result = "closed"
            else:
                result = "unbooked"

    def get_start_time(self, account):
        if(self.get_examinee_status(account) != "closed" or "unbooked" or "finished"):
            exam = self.get_exam(account)
            return exam.timeslot.start_time
        else:
            return ""
                
class ExamTimeslot(models.Model):
    course = models.ForeignKey(Course)
    start_time = models.CharField(max_length=20)

class ExamQuestion(models.Model):
    course = models.ForeignKey(Course)
    content = models.TextField()
    correct_answer = models.TextField()

class Enroll(models.Model):
    student = models.ForeignKey(Student)
    course = models.ForeignKey(Course)

class Exam(models.Model):
    enroll = models.ForeignKey(Enroll)
    timeslot = models.ForeignKey(ExamTimeslot)
    invigilator = models.ForeignKey(Invigilator)

    def get_examinee_status(self):
        result = None
        timeToExam = datetime.strptime(self.timeslot.start_time, fmt) - datetime.now()
        if(timeToExam < timedelta(days=3)):
            result = "confirmed"
        if(timeToExam < timedelta(minutes=15)):
            result = "exam"
        if(timeToExam < timedelta(minutes=-15)):
            result = "finished"
        return result

    def get_event(self, status):
        timeToExam = datetime.strptime(self.timeslot.start_time, fmt) - datetime.now()
        event = None
        if(timeToExam < timedelta(days=3) and status == "booked"):
            event = "cancel_disabled"
        if(timeToExam < timedelta(minutes=15) and status == "confirmed"):
            event = "exam_enabled"
        if(timeToExam < timedelta(minutes=-15) and status == "exam"):
            event = "exam_disabled"
        return event
    
class Answer(models.Model):
    exam = models.ForeignKey(Exam)
    question = models.ForeignKey(ExamQuestion)
    answer = models.TextField()

class TextChat(models.Model):
    exam = models.ForeignKey(Exam)
    content = models.TextField()
    time = models.CharField(max_length=20)
    
class FileStorage(models.Model):
    exam = models.ForeignKey(Exam)
    content = models.FileField(upload_to='webcam/%Y/%m/%d')

class WebcamRecording(FileStorage): pass
class ScreenRecording(FileStorage): pass
class AudioChat(FileStorage): pass
