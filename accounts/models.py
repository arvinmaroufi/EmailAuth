from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='کاربر')
    first_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='نام خانوادگی')
    image = models.ImageField(upload_to='profile/', null=True, blank=True, verbose_name='تصویر پروفایل')
    phone_number = models.CharField(max_length=11, null=True, blank=True, validators=[RegexValidator(regex='^09\d{9}$',
                                    message='شماره تلفن باید با 09 شروع شده و 11 رقم باشد')], verbose_name='شماره تلفن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'

    def __str__(self):
        return f"پروفایل {self.user.username}"


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)