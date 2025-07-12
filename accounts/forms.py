from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator


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


class UsernameLoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("نام کاربری یا رمز عبور نادرست است.", code='invalid_info')


class EmailLoginForm(forms.Form):
    email = forms.EmailField()


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField()


class VerifyCodeForm(forms.Form):
    code = forms.CharField(max_length=5)


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=20)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise ValidationError("رمز های عبور جدید مطابقت ندارند.")
        return cleaned_data


class EditProfileForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=11, required=False, validators=[RegexValidator(regex='^09\d{9}$',
                                                message='شماره تلفن باید با 09 شروع شده و 11 رقم باشد')])
    first_name = forms.CharField(max_length=100, required=False, label='نام')
    last_name = forms.CharField(max_length=100, required=False, label='نام خانوادگی')
    image = forms.ImageField(required=False, label='تصویر پروفایل')

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['phone_number'].initial = profile.phone_number
            self.fields['first_name'].initial = profile.first_name
            self.fields['last_name'].initial = profile.last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.phone_number = self.cleaned_data['phone_number']
                profile.first_name = self.cleaned_data['first_name']
                profile.last_name = self.cleaned_data['last_name']
                if self.cleaned_data['image']:
                    profile.image = self.cleaned_data['image']
                profile.save()
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 50:
            raise ValidationError("نام کاربری نمی‌ تواند بیشتر از 50 کاراکتر باشد.")
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("نام کاربری وارد شده از قبل وجود دارد.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if len(email) > 50:
            raise ValidationError("ایمیل نمی ‌تواند بیشتر از 50 کاراکتر باشد.")
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("این ایمیل قبلاً توسط کاربر دیگری ثبت شده است.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise ValidationError("شماره تلفن باید فقط شامل اعداد باشد.")
        if phone_number and len(phone_number) != 11:
            raise ValidationError("شماره تلفن باید 11 رقم باشد.")
        return phone_number

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and len(first_name) > 50:
            raise ValidationError("نام نمی‌ تواند بیشتر از 50 کاراکتر باشد.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and len(last_name) > 50:
            raise ValidationError("نام خانوادگی نمی ‌تواند بیشتر از 50 کاراکتر باشد.")
        return last_name


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=20)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise ValidationError("رمز های عبور جدید مطابقت ندارند.")
        return cleaned_data
