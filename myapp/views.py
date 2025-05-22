from django.http import HttpResponse
from django.http import JsonResponse
from .forms import DefaultSettingForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, EmailAuthenticationForm, SearchNewsForm
from django.contrib.auth.models import User
import xml.etree.ElementTree as ET
from django.utils import timezone
from .models import RssNews, DefaultSetting
import requests
import json
from django.db.models import Count, Q
import datetime

@login_required
def home(request):
    user = request.user
    # 最新の設定を取得
    try:
        setting = DefaultSetting.objects.filter(user=user).latest('id')
        default_filter = setting.default_filter
    except DefaultSetting.DoesNotExist:
        default_filter = 'all'

    # GETパラメータがあればそれを優先、なければdefault_filterを使う
    filter_type = request.GET.get('filter')
    if not filter_type:
        filter_type = default_filter

    news_list = RssNews.objects.filter(user=user).order_by('-pubdate')
    if filter_type == 'unread':
        news_list = news_list.filter(read=False)
    elif filter_type == 'favorite':
        news_list = news_list.filter(favorite=True)
    elif filter_type == 'read':
        news_list = news_list.filter(read=True)
    elif filter_type == 'unread_favorite':
        news_list = news_list.filter(read=False, favorite=True)
    elif filter_type == 'read_favorite':
        news_list = news_list.filter(read=True, favorite=True)
    # 検索フォームの初期化
    search_form = SearchNewsForm()
    return render(request, 'myapp/home.html', {'news_list': news_list, 'form': search_form, 'default_filter': filter_type})

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

def delete_news(request):
    if request.method == "POST":
        data = json.loads(request.body)
        news_id = data.get("id")
        from .models import RssNews
        try:
            news = RssNews.objects.get(id=news_id)
            news.delete()
            return JsonResponse({"success": True})
        except RssNews.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

@login_required
def search_news(request):
    if request.method == 'POST':
        form = SearchNewsForm(request.POST)
        news_list = RssNews.objects.filter(user=request.user)
        if form.is_valid():
            search_type = form.cleaned_data.get('search_type')
            query = form.cleaned_data.get('query')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            if search_type == 'title' and query:
                news_list = news_list.filter(title__icontains=query)
            elif search_type == 'category' and query:
                news_list = news_list.filter(category__icontains=query)
            elif search_type == 'period':
                if date_from:
                    news_list = news_list.filter(pubdate__gte=date_from)
                if date_to:
                    news_list = news_list.filter(pubdate__lte=date_to)
        return render(request, 'myapp/home.html', {'news_list': news_list, 'form': form})
    else:
        return redirect('myapp:home')

@login_required
def default_setting(request):
    if request.method == 'POST':
        form = DefaultSettingForm(request.POST)
        if form.is_valid():
            # 既存の設定を削除してから新しい設定を保存
            DefaultSetting.objects.filter(user=request.user).delete()
            setting = form.save(commit=False)
            setting.user = request.user
            setting.save()
            return redirect('myapp:home')
    else:
        # 既存の設定があれば取得
        try:
            setting = DefaultSetting.objects.filter(user=request.user).latest('id')
            form = DefaultSettingForm(instance=setting)
        except DefaultSetting.DoesNotExist:
            form = DefaultSettingForm()
    return render(request, 'myapp/default_setting.html', {'form': form})



# スコア計算式
# def calc_score(read_count, favorite_count, read_and_favorite_count, pubdate):
#     days = (datetime.datetime.now(datetime.timezone.utc) - pubdate).days + 1
#     # 重み付け係数
#     weight_read = 1.1
#     weight_favorite = 1.34
#     weight_read_and_favorite = 1.7

#     base =  read_count * weight_read + favorite_count * weight_favorite + read_and_favorite_count * weight_read_and_favorite

#     return base / days

# v2
def calc_score(read_count, favorite_count, read_and_favorite_count, pubdate):
    """
    より高度なスコアリング計算式 V2:
    改善された時間減衰と追加エンゲージメント要素を含む (線形加算ベース)

    Args:
        read_count (int): 記事の既読数
        favorite_count (int): 記事がお気に入りされた数
        read_and_favorite_count (int): 記事が既読かつお気に入りされた数
        comment_count (int): 記事へのコメント数 (利用できない場合は 0 を渡す)
        share_count (int): 記事がシェアされた数 (利用できない場合は 0 を渡す)
        pubdate (datetime): 記事の公開日時 (UTC推奨)

    Returns:
        float: 計算されたスコア
    """
    # 記事公開からの経過時間（日数、小数点以下も考慮）
    time_diff = datetime.datetime.now(datetime.timezone.utc) - pubdate
    days = max(0, time_diff.total_seconds() / (24 * 3600)) # 日数を秒単位で計算し、日数に変換。

    # 各エンゲージメントに対する重み付け係数

    weight_read = 0.831  # 既読のみの基本的な価値
    weight_favorite = 2.525 # お気に入りの価値 (既読より高めに設定)
    weight_read_and_favorite = 3.594 # 既読かつお気に入りの特別な価値 (他の行動よりかなり高めに設定)

    # 基本エンゲージメントスコア（各行動の重み付け和）
    # read_and_favorite_count は read_count や favorite_count と重複しますが、
    # ここでは「既読とお気に入りの両方をした」という行動自体に高い価値があるとして、
    # 元の式の構造に合わせて別途加算する形を維持します。
    engagement_score = (read_count * weight_read + favorite_count * weight_favorite + read_and_favorite_count * weight_read_and_favorite)

    # 時間減衰係数（逆数関数にオフセットを追加）
    # days + time_decay_offset とすることで、days=0 のゼロ除算を防ぎ、
    # 初期の減衰を滑らかにします。time_decay_offset を大きくすると減衰が緩やかになります。
    time_decay_offset = 1.197 # 例: 1.0, 2.0, 3.0 など。公開初日を days=0 とした場合、分母は 2.0 になる。
    time_factor = (1.0 / (days + time_decay_offset) )

    # 最終スコア = エンゲージメントスコア * 時間減衰係数　*10
    score = engagement_score * time_factor * 10

    return score

@login_required
def ranking(request):
    from django.db.models import Count, Q
    # タイトル・リンクごとに集計
    qs = (
        RssNews.objects
        .values('title', 'link', 'pubdate', 'description', 'category', 'pubdate')
        .annotate(
            read_count=Count('id', filter=Q(read=True)),
            favorite_count=Count('id', filter=Q(favorite=True)),
            read_and_favorite_count=Count('id', filter=Q(read=True, favorite=True)),
        )
    )
    # スコアを計算してリスト化
    ranking = []
    for news in qs:
        score = calc_score(
            news['read_count'],
            news['favorite_count'],
            news['read_and_favorite_count'],
            news['pubdate']
        )
        news['score'] = score
        ranking.append(news)
    # スコア順にソート
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)[:10]
    return render(request, 'myapp/ranking.html', {'ranking': ranking})

def root_redirect(request):
    return redirect('/myapp/home')