from django.db import models
import datetime

class Account(models.Model):
    username = models.CharField(max_length=15)
    password = models.CharField(max_length=15)

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

class ExamTimeslot(models.Model):
    course = models.ForeignKey(Course)
    start_time = models.DateTimeField()

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

class TextChat(models.Model):
    exam = models.ForeignKey(Exam)
    content = models.TextField()
    time = models.DateTimeField(default=datetime.datetime.now().time())
    
class FileStorage(models.Model):
    exam = models.ForeignKey(Exam)
    content = models.FileField(upload_to='webcam/%Y/%m/%d')

class WebcamRecording(FileStorage): pass
class ScreenRecording(FileStorage): pass
class AudioChat(FileStorage): pass
