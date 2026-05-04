from typing import Any, Dict

from django.conf import settings
import bleach
from rest_framework import serializers
from apps.blogs.models import Post, Category


class PostListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "title", "slug", "excerpt", "status", "published_at", "author", "views", "category")
        read_only_fields = fields

    def get_author(self, obj):
        if obj.author:
            return {"id": obj.author.id, "name": obj.author.name or obj.author.email, "email": obj.author.email}
        return None


class PostDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "title", "slug", "content", "excerpt", "status", "published_at", "author", "views", "category")
        read_only_fields = ("id", "slug", "author", "views", "published_at")

    def get_category(self, obj):
        if obj.category:
            return {"id": obj.category.id, "name": obj.category.name, "slug": obj.category.slug}
        return None

    def get_author(self, obj):
        if obj.author:
            return {"id": obj.author.id, "name": obj.author.name or obj.author.email, "email": obj.author.email}
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    # accept category by id on create/update
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ("id", "title", "content", "excerpt", "status", "category", "slug")
        read_only_fields = ("id", "slug")

    def create(self, validated_data: Dict[str, Any]) -> Post:
        # `author` may be passed via serializer.save(author=...) from the view
        author = validated_data.pop("author", None)
        if author is None:
            request = self.context.get("request")
            author = getattr(request, "user", None)
        # sanitize HTML content server-side
        content = validated_data.get("content")
        if content:
            cleaned = bleach.clean(
                content,
                tags=getattr(settings, "BLEACH_ALLOWED_TAGS", []),
                attributes=getattr(settings, "BLEACH_ALLOWED_ATTRIBUTES", {}),
                strip=getattr(settings, "BLEACH_STRIP", True),
            )
            validated_data["content"] = cleaned
        return Post.objects.create(author=author, **validated_data)

    def update(self, instance: Post, validated_data: Dict[str, Any]) -> Post:
        # sanitize on update as well
        content = validated_data.get("content")
        if content:
            cleaned = bleach.clean(
                content,
                tags=getattr(settings, "BLEACH_ALLOWED_TAGS", []),
                attributes=getattr(settings, "BLEACH_ALLOWED_ATTRIBUTES", {}),
                strip=getattr(settings, "BLEACH_STRIP", True),
            )
            validated_data["content"] = cleaned
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

