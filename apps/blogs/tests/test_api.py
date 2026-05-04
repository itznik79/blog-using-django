from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from django.test import TestCase

from apps.blogs.models import Category, Post


class BlogAPITest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email="tester@example.com", password="pass1234")
        self.client = APIClient()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.user)

    def test_category_crud_and_post_filters(self):
        # Create categories
        resp = self.auth_client.post("/api/v1/posts/categories/", {"name": "Tech", "description": "Tech posts"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        tech_slug = resp.data["slug"]
        tech_id = resp.data["id"]

        resp = self.auth_client.post("/api/v1/posts/categories/", {"name": "Sports"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        sports_slug = resp.data["slug"]

        # Retrieve category
        resp = self.client.get(f"/api/v1/posts/categories/{tech_slug}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Tech")

        # Update category
        resp = self.auth_client.put(f"/api/v1/posts/categories/{tech_slug}/", {"name": "Techy", "description": "Updated"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Techy")

        # Create posts
        p1 = self.auth_client.post(
            "/api/v1/posts/",
            {"title": "Post 1", "content": "hello world", "status": Post.STATUS_PUBLISHED, "category": tech_id},
            format="json",
        )
        self.assertEqual(p1.status_code, status.HTTP_201_CREATED)

        p2 = self.auth_client.post(
            "/api/v1/posts/",
            {"title": "Sports day", "content": "game time", "status": Post.STATUS_PUBLISHED, "category": resp.data.get("id")},
            format="json",
        )
        self.assertEqual(p2.status_code, status.HTTP_201_CREATED)

        # Draft post should not be visible to anonymous
        self.auth_client.post(
            "/api/v1/posts/",
            {"title": "Draft", "content": "not live", "status": Post.STATUS_DRAFT, "category": tech_id},
            format="json",
        )

        # List published posts (anonymous)
        list_resp = self.client.get("/api/v1/posts/?page_size=2")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", list_resp.data)
        self.assertTrue(all(item["status"] == Post.STATUS_PUBLISHED for item in list_resp.data["results"]))

        # Filter by category slug
        resp_cat = self.client.get(f"/api/v1/posts/?category={tech_slug}")
        self.assertEqual(resp_cat.status_code, status.HTTP_200_OK)
        for item in resp_cat.data["results"]:
            # category returned as slug in list serializer
            self.assertEqual(item.get("category"), tech_slug)

        # Filter by category id
        resp_cat2 = self.client.get(f"/api/v1/posts/?category={tech_id}")
        self.assertEqual(resp_cat2.status_code, status.HTTP_200_OK)

        # Search
        resp_search = self.client.get("/api/v1/posts/?q=Sports")
        self.assertEqual(resp_search.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Sports" in (r.get("title") or "") for r in resp_search.data["results"]))

        # Ordering by title
        resp_order = self.client.get("/api/v1/posts/?ordering=title")
        self.assertEqual(resp_order.status_code, status.HTTP_200_OK)

        # Retrieve by slug
        slug = p1.data["slug"]
        resp_detail = self.client.get(f"/api/v1/posts/{slug}/")
        self.assertEqual(resp_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_detail.data["title"], "Post 1")

        # Retrieve by id
        pid = p1.data.get("id")
        resp_by_id = self.client.get(f"/api/v1/posts/id/{pid}/")
        self.assertEqual(resp_by_id.status_code, status.HTTP_200_OK)
