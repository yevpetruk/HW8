from rest_framework.pagination import PageNumberPagination, CursorPagination


class SafePageNumberPagination(PageNumberPagination):
    """
    Безопасная пагинация с фиксированными параметрами
    Задание 1: 6 объектов на страницу
    """
    page_size = 6  # Задание 1: не более 6 объектов
    page_size_query_param = None  # Отключаем возможность менять размер страницы через параметры
    max_page_size = 6  # Максимальный размер страницы тоже 6

    # Не показываем общее количество страниц и элементов в заголовках
    def get_paginated_response(self, data):
        from rest_framework.response import Response
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class CursorPaginationSafe(CursorPagination):
    """
    Курсорная пагинация (самая безопасная)
    """
    page_size = 6  # Задание 1: не более 6 объектов
    ordering = '-created_at'  # Сортировка по умолчанию

    # Отключаем параметры в URL
    page_size_query_param = None
    max_page_size = 6