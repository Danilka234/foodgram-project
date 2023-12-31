from django.conf import settings

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация для ответов, где ее необходимо использовать.
    """
    page_size_query_param = "limit"
    page_size = getattr(settings, "PAGE_SIZE")
