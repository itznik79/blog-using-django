from typing import Any, Dict

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.engagement.models import Comment, Like, Bookmark
from apps.blogs.models import Post


class UserSmallSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("id", "name", "email")


class CommentSerializer(serializers.ModelSerializer):
    author = UserSmallSerializer(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "post", "parent", "content", "is_active", "created_at", "updated_at", "replies_count")
        read_only_fields = ("id", "author", "created_at", "updated_at", "replies_count")

    def create(self, validated_data: Dict[str, Any]) -> Comment:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        validated_data["author"] = user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ("id", "user", "post", "comment", "created_at")
        read_only_fields = ("id", "created_at")


class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = ("id", "user", "post", "created_at")
        read_only_fields = ("id", "created_at")
