from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class QuestionAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    question = models.CharField(max_length=1000)
    answer = models.TextField()
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.question


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    research_area = models.CharField(
        max_length=100, blank=True, null=True, default="請輸入您的研究領域"
    )
    education = models.CharField(
        max_length=100, blank=True, null=True, default="請輸入您的最高學歷"
    )
    key_skills = models.CharField(
        max_length=100, blank=True, null=True, default="請輸入您的專業技能"
    )
    work_experiences = models.CharField(
        max_length=100, blank=True, null=True, default="請輸入您的工作經驗"
    )
    relevant_coursework = models.CharField(
        max_length=100, blank=True, null=True, default="請輸入您的相關課程"
    )
    extracurricular = models.CharField(
        max_length=100, blank=True, null=True, default="請輸入您的課外活動"
    )
    language_skills = models.CharField(
        max_length=100, blank=True, null=True, default="請輸入您的外語能力"
    )

    # Add more fields as needed

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
