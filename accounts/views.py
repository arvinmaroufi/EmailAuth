from django.shortcuts import render, redirect
import random
from .models import VerificationCode
from .forms import RegisterForm
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings


def generate_verification_code():
    return ''.join(random.choices('0123456789', k=5))


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()
            code = generate_verification_code()
            VerificationCode.objects.create(
                user=user,
                code=code,
                code_expiry=timezone.now() + timedelta(minutes=2)
            )
            send_mail(
                'کد تایید ثبت ‌نام',
                f'خوش آمدید! ثبت‌ نام شما با موفقیت انجام شد.\n\nکد تایید شما: {code}\nلطفاً این کد را در صفحه تایید وارد کنید.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            request.session['verification_type'] = 'register'
            messages.success(request, 'ثبت ‌نام انجام شد. کد تایید به ایمیل شما ارسال شد.')
            return redirect('accounts:verify_code')
    else:
        form = RegisterForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)
