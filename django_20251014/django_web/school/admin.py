from django.contrib import admin
from .models import Exam,Student,Score

# Register your models here.
admin.site.register(Exam)
admin.site.register(Student)
admin.site.register(Score)