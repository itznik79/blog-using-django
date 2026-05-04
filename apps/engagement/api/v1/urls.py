from django.urls import path
from .views import CommentListCreateView, CommentDetailView, toggle_like, toggle_bookmark

app_name = 'engagement'

urlpatterns = [
    path('comments/', CommentListCreateView.as_view(), name='comments_list_create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
    path('likes/toggle/', toggle_like, name='toggle_like'),
    path('bookmarks/toggle/', toggle_bookmark, name='toggle_bookmark'),
]
