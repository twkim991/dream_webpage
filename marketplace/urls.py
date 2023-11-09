from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),  # 데이터를 처리할 url 등록!
    path('search/ordered', views.reorder, name='reorder')
]