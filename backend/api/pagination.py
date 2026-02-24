"""
Классы пагинации для API.

Содержит конфигурацию постраничного деления результатов API запросов.
"""

from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """
    Пагинация на основе номера страницы с параметром limit.

    Использует параметр 'limit' вместо стандартного 'page_size' для указания
    количества элементов на странице.
    """

    page_size_query_param = 'limit'
