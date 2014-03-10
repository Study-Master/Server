from django.contrib import admin
from sm.models import *

class AccountAdmin(admin.ModelAdmin):
    pass
    
class UserAdmin(admin.ModelAdmin):
    pass
    
class StudentAdmin(admin.ModelAdmin):
    pass
    
class InvigilatorAdmin(admin.ModelAdmin):
    pass
    
class CourseAdmin(admin.ModelAdmin):
    pass
    
class ExamTimeslotAdmin(admin.ModelAdmin):
    pass

class ExamQuestionAdmin(admin.ModelAdmin):
    pass

class EnrollAdmin(admin.ModelAdmin):
    pass
    
class ExamAdmin(admin.ModelAdmin):
    pass



admin.site.register(Account, AccountAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Invigilator, InvigilatorAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(ExamTimeslot, ExamTimeslotAdmin)
admin.site.register(ExamQuestion, ExamQuestionAdmin)
admin.site.register(Enroll, EnrollAdmin)
admin.site.register(Exam, ExamAdmin)
