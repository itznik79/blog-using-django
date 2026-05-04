from django.urls import path
from .views import PostListCreateView, PostDetailView, PostRetrieveByIDView
from .category_views import CategoryListCreateView, CategoryDetailView

app_name = "posts"

urlpatterns = [
    path("", PostListCreateView.as_view(), name="list_create"),
    # Category endpoints (must come before slug-based post detail)
    path("categories/", CategoryListCreateView.as_view(), name="category_list_create"),
    path("categories/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),

    path("<slug:slug>/", PostDetailView.as_view(), name="detail"),
    path("id/<int:pk>/", PostRetrieveByIDView.as_view(), name="detail_by_id"),
]
