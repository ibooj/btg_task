# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Content, Comment, Like
from .serializers import ContentSerializer


class ContentViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test')
        self.client.force_login(self.user)
        self.content_item_list = []
        self.content_type_list = ContentType.objects.filter(app_label='poll').filter(
            Q(model='content') | Q(model='comment')).order_by('-model')
        for i in range(100):
            content_object = Content.objects.create(
                title='Title %s' % i,
                content_type=Content.CONTENT_TYPE[i % 2][0],
                text='Text %s' % i,
                author=self.user
            )
            for ii in range(3):
                Comment.objects.create(
                    author=self.user,
                    message='Message %s' % ii,
                    content=content_object
                )
            self.content_item_list.append(content_object)

    def tearDown(self):
        for o in Like.objects.all():
            o.delete()

        for o in Comment.objects.all():
            o.delete()

        for o in Content.objects.all():
            o.delete()

        for o in User.objects.all():
            o.delete()

    def test_article_list(self):
        response = self.client.get(reverse('poll:article-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())

    def test_article_detail(self):
        response = self.client.get(reverse('poll:article-detail', args=[self.content_item_list[1].id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(response.json()['content_type'], self.content_item_list[1].content_type)

    def test_news_list(self):
        response = self.client.get(reverse('poll:news-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())

    def test_news_detail(self):
        response = self.client.get(reverse('poll:news-detail', args=[self.content_item_list[0].id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(response.json()['content_type'], self.content_item_list[0].content_type)

    def test_comment_list(self):
        rc = random.randint(0, 99)
        response = self.client.get(reverse('poll:comment-list', args=[self.content_item_list[rc].id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())

    def test_comment_create(self):
        rc = random.randint(0, 99)
        data = {
            'message': 'Test message add'
        }
        response = self.client.post(reverse('poll:comment-list', args=[self.content_item_list[rc].id]), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())

    def test_make_like(self):
        rc = random.randint(0, 99)
        data = {
            'content_type': self.content_type_list[0].id,
            'object_id': self.content_item_list[rc].id,
            'like': True
        }
        response = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())

    def test_make_dislike(self):
        rc = random.randint(0, 99)
        data = {
            'content_type': self.content_type_list[0].id,
            'object_id': self.content_item_list[rc].id,
            'like': False
        }
        response = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())

    def test_remove_like(self):
        rc = random.randint(0, 99)
        data = {
            'content_type': self.content_type_list[0].id,
            'object_id': self.content_item_list[rc].id,
            'like': True
        }
        response_make_like = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response_make_like.status_code, status.HTTP_201_CREATED, msg=response_make_like.json())
        response_remove_like = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response_remove_like.status_code, status.HTTP_204_NO_CONTENT, msg=response_make_like.json())
        self.assertFalse(Like.objects.filter(author=self.user, **data).exists())

    def test_remove_dislike(self):
        rc = random.randint(0, 99)
        data = {
            'content_type': self.content_type_list[0].id,
            'object_id': self.content_item_list[rc].id,
            'like': False
        }
        response_make_like = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response_make_like.status_code, status.HTTP_201_CREATED, msg=response_make_like.json())
        response_remove_like = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response_remove_like.status_code, status.HTTP_204_NO_CONTENT, msg=response_make_like.json())
        self.assertFalse(Like.objects.filter(author=self.user, **data).exists())

    def test_make_like_when_already_set_dislike(self):
        rc = random.randint(0, 99)
        data = {
            'content_type': self.content_type_list[0].id,
            'object_id': self.content_item_list[rc].id,
            'like': False
        }
        response = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())

        old_like = ContentSerializer(self.content_item_list[rc]).data['likes_count']

        data.update({'like': True})
        response = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())
        self.assertNotEqual(old_like, ContentSerializer(self.content_item_list[rc]).data['likes_count'])

    def test_make_dislike_when_already_set_like(self):
        rc = random.randint(0, 99)
        data = {
            'content_type': self.content_type_list[0].id,
            'object_id': self.content_item_list[rc].id,
            'like': True
        }
        response = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())

        old_like = ContentSerializer(self.content_item_list[rc]).data['likes_count']

        data.update({'like': False})
        response = self.client.post(reverse('poll:like-action'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.json())
        self.assertNotEqual(old_like, ContentSerializer(self.content_item_list[rc]).data['likes_count'])