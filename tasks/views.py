from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import Task, SubTask, Category
from .serializers import (
    TaskDetailSerializer,
    TaskCreateSerializer,
    SubTaskCreateSerializer,
    SubTaskSerializer,
    CategorySerializer,
    CategoryCreateSerializer
)


# ==============================================
# ЗАДАНИЕ 1: CATEGORYVIEWSET (MODELVIEWSET)
# ==============================================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для CRUD операций с категориями
    Задание 1: Полный CRUD через ModelViewSet
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # Для создания используем отдельный сериализатор
    def get_serializer_class(self):
        if self.action == 'create':
            return CategoryCreateSerializer
        return CategorySerializer

    # Задание 2: Переопределяем метод destroy для мягкого удаления
    def destroy(self, request, *args, **kwargs):
        """
        Мягкое удаление категории
        Задание 2: вместо физического удаления устанавливаем is_deleted=True
        """
        instance = self.get_object()

        # Выполняем мягкое удаление
        instance.soft_delete()

        return Response(
            {
                'message': f'Категория "{instance.name}" успешно удалена (мягкое удаление)',
                'deleted_at': instance.deleted_at,
                'category_id': instance.id
            },
            status=status.HTTP_200_OK
        )

    # Задание 1: Кастомный метод для подсчета задач
    @action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        """
        Кастомный метод для подсчета задач в категории
        Задание 1: метод count_tasks с декоратором @action
        """
        category = self.get_object()

        # Получаем количество задач в категории
        tasks_count = category.tasks.count()

        # Получаем список задач
        tasks = category.tasks.all()[:10]  # Ограничиваем 10 задачами для примера

        # Сериализуем задачи
        from .serializers import TaskDetailSerializer
        tasks_serializer = TaskDetailSerializer(tasks, many=True)

        return Response({
            'category_id': category.id,
            'category_name': category.name,
            'total_tasks': tasks_count,
            'tasks': tasks_serializer.data
        })

    # Дополнительный метод для получения удаленных категорий
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """
        Получение списка удаленных категорий
        """
        deleted_categories = Category.all_objects.filter(is_deleted=True)
        serializer = self.get_serializer(deleted_categories, many=True)

        return Response({
            'count': deleted_categories.count(),
            'results': serializer.data
        })

    # Метод для восстановления удаленной категории
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Восстановление удаленной категории
        """
        # Используем all_objects для поиска даже удаленных
        try:
            category = Category.all_objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Категория не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not category.is_deleted:
            return Response(
                {'message': 'Категория не была удалена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Восстанавливаем категорию
        category.restore()

        return Response({
            'message': f'Категория "{category.name}" успешно восстановлена',
            'category_id': category.id
        })


# ==============================================
# СУЩЕСТВУЮЩИЕ GENERIC VIEWS (ОСТАВЛЯЕМ)
# ==============================================

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'title']
    ordering = ['-created_at']


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'


class SubTaskListCreateView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskCreateSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline', 'task']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'title']
    ordering = ['-created_at']


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskCreateSerializer
    lookup_field = 'id'


# ==============================================
# АГРЕГИРУЮЩИЕ ЭНДПОИНТЫ
# ==============================================

class TaskStatsAPIView(APIView):
    def get(self, request):
        total_tasks = Task.objects.count()
        total_overdue = Task.objects.filter(deadline__lt=timezone.now()).count()

        status_new = Task.objects.filter(status='new').count()
        status_in_progress = Task.objects.filter(status='in_progress').count()
        status_pending = Task.objects.filter(status='pending').count()
        status_blocked = Task.objects.filter(status='blocked').count()
        status_done = Task.objects.filter(status='done').count()

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


class CreateTestDataView(APIView):
    def post(self, request):
        from datetime import timedelta

        # Создаем тестовые категории
        categories = ['Работа', 'Личное', 'Учеба', 'Проект']
        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)

        # Создаем задачи
        tasks_data = [
            ("Завершить проект", "Доделать проект по Django", 'in_progress', 3),
            ("Подготовить отчет", "Написать отчет", 'new', 5),
            ("Тестирование", "Протестировать систему", 'pending', 7),
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

            for i in range(2):
                SubTask.objects.create(
                    title=f"Подзадача {i + 1} для {title[:20]}",
                    description=f"Описание подзадачи {i + 1}",
                    task=task,
                    status=['new', 'done'][i % 2],
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