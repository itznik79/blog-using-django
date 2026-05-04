from rest_framework.pagination import CursorPagination


class StandardCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-published_at"
    cursor_query_param = "cursor"
    page_size_query_param = "page_size"
