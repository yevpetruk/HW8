from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Task, SubTask, Category
from .serializers import (
    TaskDetailSerializer,
    TaskCreateSerializer,
    SubTaskCreateSerializer,
    SubTaskSerializer,
    CategorySerializer
)


# ==============================================
# КАСТОМНЫЙ ПАГИНАТОР
# ==============================================

class StandardPagination(PageNumberPagination):
    """Стандартная пагинация для всех представлений"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ==============================================
# ЗАДАНИЕ 1: GENERIC VIEWS ДЛЯ ЗАДАЧ (TASKS)
# ==============================================

class TaskListCreateView(generics.ListCreateAPIView):
    """
    Generic View для создания и получения списка задач
    Задание 1: ListCreateAPIView для задач
    """
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    pagination_class = StandardPagination

    # Задание 1: Фильтрация, поиск и сортировка
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Фильтрация по полям
    filterset_fields = ['status', 'deadline']

    # Поиск по полям
    search_fields = ['title', 'description']

    # Сортировка по полю created_at
    ordering_fields = ['created_at', 'deadline', 'title']
    ordering = ['-created_at']  # По умолчанию сортировка по убыванию даты создания

    def get_queryset(self):
        """Дополнительная фильтрация"""
        queryset = super().get_queryset()

        # Фильтрация по категории
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        # Фильтрация по просроченным задачам
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(deadline__lt=timezone.now())
        elif overdue == 'false':
            queryset = queryset.filter(Q(deadline__gte=timezone.now()) | Q(deadline__isnull=True))

        return queryset.distinct()


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic View для получения, обновления и удаления задачи
    Задание 1: RetrieveUpdateDestroyAPIView для задач
    """
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'


# ==============================================
# ЗАДАНИЕ 2: GENERIC VIEWS ДЛЯ ПОДЗАДАЧ (SUBTASKS)
# ==============================================

class SubTaskListCreateView(generics.ListCreateAPIView):
    """
    Generic View для создания и получения списка подзадач
    Задание 2: ListCreateAPIView для подзадач
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskCreateSerializer
    pagination_class = StandardPagination

    # Задание 2: Фильтрация, поиск и сортировка
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Фильтрация по полям
    filterset_fields = ['status', 'deadline', 'task']

    # Поиск по полям
    search_fields = ['title', 'description']

    # Сортировка по полю created_at
    ordering_fields = ['created_at', 'deadline', 'title']
    ordering = ['-created_at']  # По умолчанию сортировка по убыванию даты создания

    def get_queryset(self):
        """Дополнительная фильтрация"""
        queryset = super().get_queryset()

        # Фильтрация по просроченным подзадачам
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(deadline__lt=timezone.now())
        elif overdue == 'false':
            queryset = queryset.filter(Q(deadline__gte=timezone.now()) | Q(deadline__isnull=True))

        return queryset


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic View для получения, обновления и удаления подзадачи
    Задание 2: RetrieveUpdateDestroyAPIView для подзадач
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskCreateSerializer
    lookup_field = 'id'


# ==============================================
# GENERIC VIEWS ДЛЯ КАТЕГОРИЙ
# ==============================================

class CategoryListCreateView(generics.ListCreateAPIView):
    """Generic View для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Generic View для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


# ==============================================
# АГРЕГИРУЮЩИЙ ЭНДПОИНТ (ОСТАВЛЯЕМ КАК ЕСТЬ)
# ==============================================

class TaskStatsAPIView(APIView):
    """
    Агрегирующий эндпоинт для статистики задач
    Оставляем как есть по заданию
    """

    def get(self, request):
        """Получение статистики по задачам"""
        # Общее количество задач
        total_tasks = Task.objects.count()

        # Количество просроченных задач
        total_overdue = Task.objects.filter(
            deadline__lt=timezone.now()
        ).count()

        # Статистика по статусам
        status_new = Task.objects.filter(status='new').count()
        status_in_progress = Task.objects.filter(status='in_progress').count()
        status_pending = Task.objects.filter(status='pending').count()
        status_blocked = Task.objects.filter(status='blocked').count()
        status_done = Task.objects.filter(status='done').count()

        # Процент выполнения
        completion_rate = 0
        if total_tasks > 0:
            completion_rate = round((status_done / total_tasks) * 100, 2)

        return Response({
            'total_tasks': total_tasks,
            'total_overdue': total_overdue,
            'by_status': {
                'new': status_new,
                'in_progress': status_in_progress,
                'pending': status_pending,
                'blocked': status_blocked,
                'done': status_done
            },
            'completion_rate': completion_rate
        })


# ==============================================
# ВСПОМОГАТЕЛЬНЫЕ ЭНДПОИНТЫ
# ==============================================

class CreateTestDataView(APIView):
    """Создание тестовых данных для проверки"""

    def post(self, request):
        """Создание тестовых данных"""
        from datetime import timedelta

        # Создаем категории
        categories = ['Работа', 'Личное', 'Учеба', 'Проект']
        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)

        # Создаем задачи
        tasks_data = [
            ("Завершить проект API", "Доделать API для менеджера задач", 'in_progress', 3),
            ("Подготовить отчет", "Написать отчет по проекту", 'new', 5),
            ("Тестирование системы", "Протестировать все функции", 'pending', 7),
            ("Встреча с командой", "Обсудить прогресс по проекту", 'done', 1),
            ("Изучение документации", "Изучить Django REST Framework", 'blocked', 10),
        ]

        created_tasks = []
        work_category = Category.objects.get(name='Работа')

        for title, description, status, days_ahead in tasks_data:
            task = Task.objects.create(
                title=title,
                description=description,
                status=status,
                deadline=timezone.now() + timedelta(days=days_ahead)
            )
            task.categories.add(work_category)

            # Создаем подзадачи
            for i in range(3):
                SubTask.objects.create(
                    title=f"Подзадача {i + 1} для {title[:20]}",
                    description=f"Описание подзадачи {i + 1}",
                    task=task,
                    status=['new', 'in_progress', 'done'][i % 3],
                    deadline=timezone.now() + timedelta(days=i + 1)
                )

            created_tasks.append({
                'id': task.id,
                'title': task.title,
                'status': task.status
            })

        return Response({
            'message': 'Тестовые данные созданы',
            'created_tasks': created_tasks,
            'total_tasks': Task.objects.count(),
            'total_subtasks': SubTask.objects.count()
        })