# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Content, Comment, Like


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'date_create', 'id')
    raw_id_fields = ('author',)
    list_filter = ('content_type',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'content')
    list_display = ('message', 'content', 'date_create', 'author', 'id')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
