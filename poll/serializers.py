# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .models import Content, Comment, Like


class CustomViewRelatedField(serializers.ModelField):
    default_error_messages = {
        'invalid': _('Value must be valid JSON.')
    }

    def __init__(self, model_field, view_fields=None, **kwargs):
        self.view_fields = view_fields
        super(CustomViewRelatedField, self).__init__(model_field, allow_null=True, **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            value = data.get('id')
        else:
            try:
                json_data = json.loads(data)
                value = json_data.get('id')
            except (TypeError, ValueError):
                self.fail('invalid')
        try:
            return self.model_field.related_model.objects.get(pk=value)
        except (TypeError, ValueError, ObjectDoesNotExist):
            pass

    def to_representation(self, obj):
        o = getattr(obj, self.model_field.name)
        if o:
            d = {'id': o.id}
            for f in self.view_fields:
                attr = getattr(o, f)
                if callable(attr):
                    attr = attr()
                    f = str(f).replace('get_', '')
                d.update({f: attr})
            return d


class ContentSerializer(serializers.ModelSerializer):
    author = CustomViewRelatedField(model_field=Content()._meta.get_field('author'),
                                    view_fields=['id', 'get_full_name'], read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comment_list.count()

    def get_likes_count(self, obj):
        return Like.like_counter.likes('content', obj.id)


class CommentSerializer(serializers.ModelSerializer):
    author = CustomViewRelatedField(model_field=Content()._meta.get_field('author'),
                                    view_fields=['id', 'get_full_name'], read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        exclude = ('content',)

    def get_likes_count(self, obj):
        return Like.like_counter.likes('content', obj.id)


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ('content_type', 'object_id', 'like')
