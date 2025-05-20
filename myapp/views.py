from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from django.contrib.auth.models import User
import xml.etree.ElementTree as ET
from django.utils import timezone
from .models import RssNews
import requests
import json

@login_required
def home(request):
    news_list = RssNews.objects.filter(user=request.user).order_by('-pubdate')
    return render(request, 'myapp/home.html', {'news_list': news_list})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('myapp:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                from django.contrib.auth import authenticate, login as auth_login
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('myapp:home')
            except User.DoesNotExist:
                pass  # 認証失敗時は何もしない（エラー表示はテンプレートで）
    else:
        form = EmailAuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

@login_required
def mypage(request):
    news_count = RssNews.objects.filter(user=request.user).count()
    read_count = RssNews.objects.filter(user=request.user, read=True).count()
    favorite_count = RssNews.objects.filter(user=request.user, favorite=True).count()
    return render(request, 'myapp/mypage.html', {'news_count': news_count, 'read_count': read_count, 'favorite_count': favorite_count})

@login_required
def logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    return redirect('myapp:login')

@login_required
def fetch_news(request):
    if request.method == "POST":
        url = "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE5mTTJRU0FtcGhLQUFQAQ?hl=ja&gl=JP&ceid=JP:ja"
        response = requests.get(url)
        root = ET.fromstring(response.content)
        channel = root.find("channel")
        category = channel.find("title").text if channel is not None else ""
        print("item数:", len(channel.findall("item")))
        for item in channel.findall("item"):
            title = item.find("title").text
            print("タイトル:", title)
            link = item.find("link").text
            pubdate = item.find("pubDate").text
            description = item.find("description").text
            # image取得（media:contentまたはchannel/image/url）
            image = ""
            media = item.find("{http://search.yahoo.com/mrss/}content")
            if media is not None and "url" in media.attrib:
                image = media.attrib["url"]
            elif channel.find("image/url") is not None:
                image = channel.find("image/url").text
            # pubdateをdatetimeに変換
            from dateutil import parser
            pubdate_dt = parser.parse(pubdate)
            # 重複チェックして保存
            if not RssNews.objects.filter(user=request.user, title=title).exists():
                RssNews.objects.create(
                    user=request.user,
                    title=title,
                    link=link,
                    pubdate=pubdate_dt,
                    description=description,
                    image=image,
                    category=category
                )
                print("保存完了")
            else:
                print("重複のため保存しませんでした")
        return redirect('myapp:home')
    return render(request, "myapp/fetch_news.html")


def mark_read(request):
    if request.method == "POST":
        data = json.loads(request.body)
        news_id = data.get("id")
        from .models import RssNews
        try:
            news = RssNews.objects.get(id=news_id)
            news.read = True
            news.save()
            return JsonResponse({"success": True})
        except RssNews.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

def delete_read(request):
    if request.method == "POST":
        data = json.loads(request.body)
        news_id = data.get("id")
        from .models import RssNews
        try:
            news = RssNews.objects.get(id=news_id)
            news.read = False
            news.save()
            return JsonResponse({"success": True})
        except RssNews.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

def mark_favorite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        news_id = data.get("id")
        from .models import RssNews
        try:
            news = RssNews.objects.get(id=news_id)
            news.favorite = not news.favorite
            news.save()
            return JsonResponse({"success": True})
        except RssNews.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

def delete_favorite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        news_id = data.get("id")
        from .models import RssNews
        try:
            news = RssNews.objects.get(id=news_id)
            news.favorite = False
            news.save()
            return JsonResponse({"success": True})
        except RssNews.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})
