from django.contrib import admin
from .models import QuestionAnswer, UserProfile
# Register your models here.

admin.site.register(QuestionAnswer)
admin.site.register(UserProfile)