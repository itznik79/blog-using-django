from django import forms
from django.contrib import admin
import importlib

# Import CKEditorWidget dynamically to avoid static analysis errors
try:
    _mod = importlib.import_module("ckeditor.widgets")
    CKEditorWidget = getattr(_mod, "CKEditorWidget")
except Exception:
    # Fallback widget for environments without django-ckeditor installed
    from django.forms import Textarea as CKEditorWidget

from .models import Post, Category


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Post
        fields = '__all__'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "author", "status", "published_at", "views")
    list_filter = ("status", "published_at", "category")
    search_fields = ("title", "content", "author__email")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views", "published_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
