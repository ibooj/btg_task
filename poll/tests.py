# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from .models import Content, Comment


class ContentViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test')
        self.content_item_list = []
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
