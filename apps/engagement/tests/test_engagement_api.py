from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from django.test import TestCase

from apps.blogs.models import Post, Category


class EngagementApiTest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='eng@example.com', password='pass1234')
        self.client = APIClient()
        self.auth = APIClient()
        self.auth.force_authenticate(user=self.user)

        # create category and post
        cat = Category.objects.create(name='Test', slug='test')
        self.post = Post.objects.create(author=self.user, title='P1', slug='p1', content='c', status=Post.STATUS_PUBLISHED, category=cat)

    def test_comment_like_bookmark_flow(self):
        # create comment
        resp = self.auth.post('/api/v1/engagement/comments/', {'post': self.post.id, 'content': 'Nice post'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cid = resp.data['id']

        # list comments
        list_resp = self.client.get(f'/api/v1/engagement/comments/?post={self.post.id}')
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        # like post
        like_resp = self.auth.post('/api/v1/engagement/likes/toggle/', {'post': self.post.id}, format='json')
        self.assertEqual(like_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(like_resp.data.get('liked'))

        # unlike post
        unlike = self.auth.post('/api/v1/engagement/likes/toggle/', {'post': self.post.id}, format='json')
        self.assertEqual(unlike.status_code, status.HTTP_200_OK)
        self.assertFalse(unlike.data.get('liked'))

        # bookmark
        bm = self.auth.post('/api/v1/engagement/bookmarks/toggle/', {'post': self.post.id}, format='json')
        self.assertEqual(bm.status_code, status.HTTP_200_OK)
        self.assertTrue(bm.data.get('bookmarked'))

        # remove bookmark
        bm2 = self.auth.post('/api/v1/engagement/bookmarks/toggle/', {'post': self.post.id}, format='json')
        self.assertEqual(bm2.status_code, status.HTTP_200_OK)
        self.assertFalse(bm2.data.get('bookmarked'))
