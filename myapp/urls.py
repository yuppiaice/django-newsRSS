from django.contrib import admin
from django.urls import path, include
from . import views
from myapp.views import root_redirect

app_name = 'myapp'
urlpatterns = [
    path('', root_redirect),
    # ユーザー関連
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('mypage/', views.mypage, name='mypage'),

    # 動作関連
    path('fetch_news/', views.fetch_news, name='fetch_news'),
    path('mark_read/', views.mark_read, name='mark_read'),
    path('delete_read/', views.delete_read, name='delete_read'),
    path('mark_favorite/', views.mark_favorite, name='mark_favorite'),
    path('delete_favorite/', views.delete_favorite, name='delete_favorite'),
    path('search_news/', views.search_news, name='search_news'),
    path('default_setting/', views.default_setting, name='default_setting'),
    path('delete_news/', views.delete_news, name='delete_news'),
    path('ranking/', views.ranking, name='ranking'),
    path('news/<int:news_id>/', views.news_info, name='news_info'),
    path('share/', views.share_news, name='share_news'),
]
