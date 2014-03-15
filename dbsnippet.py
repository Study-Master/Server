from sm.models import *
from datetime import datetime
from hashlib import md5

a = Account(username='s', password=md5(b'1').hexdigest())
a.save()

s = Student(account=a, first_name='study', last_name='master', email='x@x.com', matric_num='U1220000X')
s.save()

c = Course(code='CZ2006', name='Software Engineering')
c.save()

et = ExamTimeslot(course=c, start_time='2014/04/04 12:30:00')
et.save()

