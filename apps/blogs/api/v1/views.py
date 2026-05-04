from typing import Dict, Any

from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.blogs.models import Post
from core.pagination.cursor import StandardCursorPagination
from .serializers import PostListSerializer, PostDetailSerializer, PostCreateSerializer


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().select_related("author", "category")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardCursorPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateSerializer
        return PostListSerializer

    def create(self, request, *args, **kwargs):
        # override to return the fully serialized created object (with slug/id/author)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = getattr(serializer, "instance", None)
        output = PostDetailSerializer(instance, context={"request": request})
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        qs = super().get_queryset().select_related("author", "category")
        # By default only show published posts to anonymous/read-only users
        user = getattr(self.request, "user", None)
        if not (user and user.is_authenticated and (user.is_staff or user.is_superuser)):
            qs = qs.filter(status=Post.STATUS_PUBLISHED)

        # Category filter: accept slug or numeric id
        cat = self.request.query_params.get("category")
        if cat:
            if str(cat).isdigit():
                qs = qs.filter(category__id=int(cat))
            else:
                qs = qs.filter(category__slug__iexact=cat)

        # Search across title, content, author name/email
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(content__icontains=q)
                | Q(author__email__icontains=q)
                | Q(author__name__icontains=q)
            )

        # Ordering: allow clients to request ordering via `ordering` param
        ordering = self.request.query_params.get("ordering")
        allowed = {"published_at", "created_at", "views", "title"}
        if ordering:
            desc = ordering.startswith("-")
            field = ordering.lstrip("-")
            if field in allowed:
                final = f"-{field}" if desc else field
                # set ordering on the pagination class so cursor pagination uses it
                if getattr(self, "pagination_class", None):
                    try:
                        self.pagination_class.ordering = final
                    except Exception:
                        pass
                qs = qs.order_by(final)

        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "slug"
    queryset = Post.objects.all().select_related("author")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PostCreateSerializer
        return PostDetailSerializer


class PostRetrieveByIDView(generics.RetrieveAPIView):
    queryset = Post.objects.all().select_related("author")
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"
    serializer_class = PostDetailSerializer
