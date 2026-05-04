from typing import Any, Dict

from rest_framework import serializers
from apps.blogs.models import Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")
        read_only_fields = ("id", "slug")

    def create(self, validated_data: Dict[str, Any]) -> Category:
        return Category.objects.create(**validated_data)
