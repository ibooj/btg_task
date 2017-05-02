# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics, viewsets

from .models import Content, Comment
from .serializers import ContentSerializer, CommentSerializer


class ArticleView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentSerializer

    def get_queryset(self):
        return Content.objects.filter(content_type='article').select_related('author')


class NewsView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentSerializer

    def get_queryset(self):
        return Content.objects.filter(content_type='news').select_related('author')


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(**self.kwargs)
