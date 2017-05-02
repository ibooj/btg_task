# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics, viewsets, permissions, response, status

from .models import Content, Comment, Like
from .serializers import ContentSerializer, CommentSerializer, LikeSerializer


class ArticleView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentSerializer

    def get_queryset(self):
        return Content.objects.filter(content_type='article').select_related('author')


class NewsView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentSerializer

    def get_queryset(self):
        return Content.objects.filter(content_type='news').select_related('author')


class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(**self.kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, **self.kwargs)


class MakeLikeView(generics.CreateAPIView):
    serializer_class = LikeSerializer

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        like_conditions = dict(serializer.validated_data)
        like = like_conditions.pop('like')
        like_object = Like.objects.filter(author=request.user, **like_conditions).first()
        if like_object:
            like_object.delete()
            if like == like_object.like:
                return response.Response(status=status.HTTP_204_NO_CONTENT)
        serializer.save(author=request.user)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
