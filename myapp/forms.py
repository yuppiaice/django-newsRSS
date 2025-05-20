from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DefaultSetting, UserProfile

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

class SearchNewsForm(forms.Form):
    SEARCH_CHOICES = [
        ('title', 'タイトル'),
        ('period', '期間'),
    ]
    search_type = forms.ChoiceField(label='検索対象', choices=SEARCH_CHOICES, required=True, initial='title')
    query = forms.CharField(label='検索', required=False, max_length=100)
    date_from = forms.DateField(label='日付(開始)', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(label='日付(終了)', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class DefaultSettingForm(forms.ModelForm):
    FILTER_CHOICES = [
        ('all', '全て'),
        ('unread', '未読'),
        ('favorite', 'お気に入り'),
        ('read', '既読'),
        ('unread_favorite', '未読お気に入り'),
        ('read_favorite', '既読お気に入り'),
    ]
    default_filter = forms.ChoiceField(
        choices=FILTER_CHOICES,
        label='デフォルト表示',
        required=True
    )
    class Meta:
        model = DefaultSetting
        fields = ['default_filter']

