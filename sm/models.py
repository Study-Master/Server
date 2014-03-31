from django.db import models
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

    def get_examinee_status(self, account):
        try:
            exam = Exam.objects.get(enroll__student__account__username=account,
                                    enroll__course__code=self.code)
        except ObjectDoesNotExist:
            exam = None
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
