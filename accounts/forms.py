from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=20)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 50:
            raise ValidationError("نام کاربری نمی ‌تواند بیشتر از 50 کاراکتر باشد.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("نام کاربری وارد شده از قبل وجود دارد.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if len(email) > 50:
            raise ValidationError("ایمیل نمی ‌تواند بیشتر از 50 کاراکتر باشد.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("ایمیل وارد شده از قبل وجود دارد.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("رمز های عبور مطابقت ندارند.")
        return password
