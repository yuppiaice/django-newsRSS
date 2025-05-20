from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='メールアドレス')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'password1': 'パスワード',
            'password2': 'パスワード（確認用）',
        }
        help_texts = {
            'username': '必須。150文字以内。英字、数字、@/./+/-/_ のみ使用可能。',
            'password1': '8文字以上で入力してください。よく使われるパスワードや個人情報に似たもの、数字のみは使用できません。',
            'password2': '確認のため、同じパスワードをもう一度入力してください。',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(widget=forms.PasswordInput, label='パスワード')