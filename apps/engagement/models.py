from typing import Optional

from django.db import models
from django.conf import settings

# use lazy model reference to avoid import-time coupling
Post = 'blogs.Post'


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Comment by {self.author} on {self.post_id}'

    @property
    def author_id(self) -> Optional[int]:
        # prefer stored fk value if present on instance dict to avoid extra db access
        val = self.__dict__.get('author_id')
        if val is not None:
            return val
        return getattr(self.author, 'pk', None)

    @property
    def post_id(self) -> Optional[int]:
        val = self.__dict__.get('post_id')
        if val is not None:
            return val
        return getattr(self.post, 'pk', None)


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name='likes')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like', condition=models.Q(post__isnull=False)),
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_user_comment_like', condition=models.Q(comment__isnull=False)),
        ]

    def __str__(self):
        target = self.post_id or self.comment_id
        return f'Like by {self.user_id} -> {target}'

    @property
    def user_id(self) -> Optional[int]:
        val = self.__dict__.get('user_id')
        if val is not None:
            return val
        return getattr(self.user, 'pk', None)

    @property
    def post_id(self) -> Optional[int]:
        val = self.__dict__.get('post_id')
        if val is not None:
            return val
        return getattr(self.post, 'pk', None)

    @property
    def comment_id(self) -> Optional[int]:
        val = self.__dict__.get('comment_id')
        if val is not None:
            return val
        return getattr(self.comment, 'pk', None)


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'Bookmark {self.user_id}->{self.post_id}'

    @property
    def user_id(self) -> Optional[int]:
        val = self.__dict__.get('user_id')
        if val is not None:
            return val
        return getattr(self.user, 'pk', None)

    @property
    def post_id(self) -> Optional[int]:
        val = self.__dict__.get('post_id')
        if val is not None:
            return val
        return getattr(self.post, 'pk', None)
