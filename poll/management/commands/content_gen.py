# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from ...models import Content, Comment


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(id=1)
        for i in range(100):
            content_object = Content.objects.create(
                title='Title %s' % i,
                content_type=Content.CONTENT_TYPE[i % 2][0],
                text='Text %s' % i,
                author=user
            )
            for ii in range(3):
                Comment.objects.create(
                    author=user,
                    message='Message %s' % ii,
                    content=content_object
                )
