from django.shortcuts import render, redirect
import random
from .models import VerificationCode
from .forms import RegisterForm, UsernameLoginForm, EmailLoginForm, ForgetPasswordForm, VerifyCodeForm
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


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


def username_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UsernameLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accounts:dashboard')
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    else:
        form = UsernameLoginForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/username_login.html', context)


def email_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                code = generate_verification_code()
                VerificationCode.objects.create(
                    user=user,
                    code=code,
                    code_expiry=timezone.now() + timedelta(minutes=2)
                )
                send_mail(
                    'کد تایید ورود',
                    f'خوش آمدید! برای ورود به حساب کاربری خود از کد زیر استفاده کنید.\n\nکد تایید شما: {code}\nلطفاً این کد را در صفحه تایید وارد کنید.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                request.session['verification_type'] = 'login'
                request.session['verified_user_id'] = user.id
                messages.success(request, 'کد تایید به ایمیل شما ارسال شد.')
                return redirect('accounts:verify_code')
            except User.DoesNotExist:
                messages.error(request, 'ایمیل وارد شده وجود ندارد.')
    else:
        form = EmailLoginForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/email_login.html', context)


def forget_password(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                code = generate_verification_code()
                VerificationCode.objects.create(
                    user=user,
                    code=code,
                    code_expiry=timezone.now() + timedelta(minutes=2)
                )
                send_mail(
                    'کد تایید بازیابی رمز عبور',
                    f'خوش آمدید! برای بازیابی رمز عبور خود از کد زیر استفاده کنید.\n\nکد تایید شما: {code}\nلطفاً این کد را در صفحه تایید وارد کنید.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                request.session['verification_type'] = 'reset_password'
                messages.success(request, 'کد تایید به ایمیل شما ارسال شد.')
                return redirect('accounts:verify_code')
            except User.DoesNotExist:
                messages.error(request, 'ایمیل وارد شده وجود ندارد.')
    else:
        form = ForgetPasswordForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/forget_password.html', context)


def verify_code(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    VerificationCode.clean_expired_codes()

    if request.method == 'POST':
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                verification = VerificationCode.objects.get(code=code, is_used=False)
                if verification.is_valid(code):
                    verification.is_used = True
                    verification.save()
                    verification.delete()

                    verification_type = request.session.get('verification_type')
                    user = verification.user

                    if verification_type == 'register':
                        user.is_active = True
                        user.save()
                        login(request, user)
                        messages.success(request, 'تایید موفقیت‌ آمیز بود. وارد شدید.')
                        return redirect('accounts:dashboard')
                    elif verification_type == 'login':
                        user.is_active = True
                        user.save()
                        login(request, user)
                        messages.success(request, 'تایید موفقیت ‌آمیز بود. وارد شدید.')
                        return redirect('accounts:dashboard')
                    elif verification_type == 'reset_password':
                        request.session['verified_user_id'] = user.id
                        return redirect('accounts:reset_password')
                else:
                    messages.error(request, 'کد تایید نامعتبر یا منقضی شده است.')
            except VerificationCode.DoesNotExist:
                messages.error(request, 'کد تایید نامعتبر است.')
    else:
        form = VerifyCodeForm()

    try:
        latest_code = VerificationCode.objects.filter(is_used=False).latest('code_expiry')
        remaining_seconds = int((latest_code.code_expiry - timezone.now()).total_seconds())
    except VerificationCode.DoesNotExist:
        remaining_seconds = 120

    context = {
        'form': form,
        'remaining_seconds': remaining_seconds
    }
    return render(request, 'accounts/verify_code.html', context)
