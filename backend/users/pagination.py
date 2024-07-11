from rest_framework.pagination import PageNumberPagination

from recipes.constants import PAGE_SIZE


class UserRecipePagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = "limit"
