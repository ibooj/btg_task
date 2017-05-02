# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.urls import reverse


class Content(models.Model):
    CONTENT_TYPE = (
        ('news', 'News'),
        ('article', 'Article')
    )

    content_type = models.CharField(choices=CONTENT_TYPE, max_length=7)
    title = models.CharField(max_length=300)
    text = models.TextField()
    date_create = models.DateTimeField(auto_now=False, auto_now_add=True)
    date_publication = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return self.title

    def get_admin_edit_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])

    class Meta:
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'
        ordering = ('-date_create',)


class Comment(models.Model):
    content = models.ForeignKey(Content, related_name='comment_list')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_create = models.DateTimeField(auto_now=False, auto_now_add=True)
    message = models.TextField()

    def __unicode__(self):
        return self.message

    def get_admin_edit_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('-date_create',)


class LikeManager(models.Manager):
    def likes(self, model, object_id):
        qs = self.filter(content_type__app_label='poll', content_type__model=model, object_id=object_id).aggregate(
            like=models.Count(models.Case(models.When(like=True, then=1))),
            dislike=models.Count(models.Case(models.When(like=False, then=1)))
        )
        print qs
        return qs


class Like(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to=models.Q(app_label='poll', model='content') | models.Q(
                                         app_label='poll', model='comment'))
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_create = models.DateTimeField(auto_now=False, auto_now_add=True)
    like = models.BooleanField(default=True)

    like_counter = LikeManager()

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        unique_together = ('content_type', 'object_id', 'author', 'like')
