from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import timedelta


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


class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes', verbose_name='کاربر')
    code = models.CharField(max_length=5, verbose_name='کد تایید')
    code_expiry = models.DateTimeField(verbose_name='تاریخ انقضای کد')
    is_used = models.BooleanField(default=False, verbose_name='استفاده شده؟')

    class Meta:
        verbose_name = 'کد تایید'
        verbose_name_plural = 'کد های تایید'

    def __str__(self):
        return self.code

    def is_valid(self, code):
        if self.code == code and not self.is_used and self.code_expiry:
            if timezone.now() <= self.code_expiry:
                return True
            else:
                self.delete()
                return False
        return False

    def set_code(self, code):
        self.code = code
        self.code_expiry = timezone.now() + timedelta(minutes=2)
        self.save()

    @classmethod
    def clean_expired_codes(cls):
        cls.objects.filter(models.Q(is_used=True) | models.Q(code_expiry__lt=timezone.now())).delete()


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)