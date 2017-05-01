# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from poll import views

router = SimpleRouter()
router.register(r'article', views.ArticleView, base_name='article')
router.register(r'news', views.NewsView, base_name='news')

urlpatterns = [
    # url(r'^articles/', views.ArticleView.as_view(), name='article-list'),
]

urlpatterns += router.urls
