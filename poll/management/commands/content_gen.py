# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from ...models import Content, Comment, Like


def delete_all_content():
    for o in Comment.objects.all():
        o.delete()

    for o in Content.objects.all():
        o.delete()

    for o in User.objects.all().exclude(id=1):
        o.delete()


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(id=1)
        delete_all_content()
        user_list = [User.objects.create_user('test_user_%s' % i) for i in range(3)]
        content_type_list = ContentType.objects.filter(app_label='poll').filter(
            Q(model='content') | Q(model='comment')).order_by('-model')
        for i in range(100):
            content_object = Content.objects.create(
                title='Title %s' % i,
                content_type=Content.CONTENT_TYPE[i % 2][0],
                text='Text %s' % i,
                author=user
            )
            Like.objects.create(
                object_id=content_object.id,
                content_type=content_type_list[0],
                author=user_list[random.randint(0, 2)],
                like=bool(i % 2)
            )
            for ii in range(3):
                comment_object = Comment.objects.create(
                    author=user,
                    message='Message %s' % ii,
                    content=content_object
                )
                Like.objects.create(
                    object_id=comment_object.id,
                    content_type=content_type_list[1],
                    author=user_list[random.randint(0, 2)],
                    like=bool(i % 2)
                )
