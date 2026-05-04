from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.engagement.models import Comment, Like, Bookmark
from apps.blogs.models import Post
from .serializers import CommentSerializer
from core.pagination.cursor import StandardCursorPagination


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all().select_related("author", "post")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardCursorPagination

    def get_queryset(self):
        qs = super().get_queryset()
        post = self.request.query_params.get("post")
        if post:
            if str(post).isdigit():
                qs = qs.filter(post__id=int(post))
            else:
                qs = qs.filter(post__slug__iexact=post)
        # only active comments by default
        qs = qs.filter(is_active=True)
        # annotate replies count
        qs = qs.annotate(replies_count=Count("replies"))
        # ensure paginator orders by created_at when using cursor pagination
        if getattr(self, "pagination_class", None):
            try:
                self.pagination_class.ordering = "-created_at"
            except Exception:
                pass
        return qs

    def perform_create(self, serializer):
        serializer.save()


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all().select_related("author", "post")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        obj = self.get_object()
        user = getattr(self.request, "user", None)
        if not (user and (user.is_staff or obj.author_id == user.id)):
            raise PermissionError("Not allowed")
        serializer.save()

    def perform_destroy(self, instance: Comment):
        user = getattr(self.request, "user", None)
        if not (user and (user.is_staff or instance.author_id == user.id)):
            raise PermissionError("Not allowed")
        instance.delete()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_like(request):
    post_id = request.data.get("post")
    comment_id = request.data.get("comment")
    user = request.user
    if post_id:
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()
            return Response({"liked": False})
        return Response({"liked": True})
    if comment_id:
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        like, created = Like.objects.get_or_create(user=user, comment=comment)
        if not created:
            like.delete()
            return Response({"liked": False})
        return Response({"liked": True})
    return Response({"detail": "post or comment required"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_bookmark(request):
    post_id = request.data.get("post")
    user = request.user
    if not post_id:
        return Response({"detail": "post required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    bm, created = Bookmark.objects.get_or_create(user=user, post=post)
    if not created:
        bm.delete()
        return Response({"bookmarked": False})
    return Response({"bookmarked": True})
