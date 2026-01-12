from rest_framework import viewsets, status, generics, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Task, SubTask, Category
from .serializers import (
    TaskDetailSerializer,
    TaskCreateSerializer,
    SubTaskCreateSerializer,
    SubTaskSerializer,
    CategorySerializer,
    CategoryCreateSerializer,
    UserSerializer
)
from .permissions import IsOwnerOrReadOnly, IsTaskOwner, IsSubTaskOwner


# Класс пагинации
class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


# ==============================================
# ЗАДАНИЕ 1: ПРЕДСТАВЛЕНИЯ С ИЗВЛЕЧЕНИЕМ ПОЛЬЗОВАТЕЛЯ
# ==============================================

class TaskListCreateView(generics.ListCreateAPIView):
    """
    Создание и получение списка задач
    Задание 1: Автоматическое добавление владельца
    """
    serializer_class = TaskCreateSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'title']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Задание 1: Фильтрация по владельцу при необходимости"""
        queryset = Task.objects.all()

        # Если пользователь аутентифицирован и запрашивает свои задачи
        my_tasks = self.request.query_params.get('my_tasks', '')
        if self.request.user.is_authenticated and my_tasks.lower() == 'true':
            queryset = queryset.filter(owner=self.request.user)

        return queryset

    def perform_create(self, serializer):
        """Задание 1: Автоматическое добавление владельца при создании"""
        serializer.save(owner=self.request.user)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление и удаление задачи
    Задание 2: Применение кастомных пермишенов
    """
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsTaskOwner()]


class SubTaskListCreateView(generics.ListCreateAPIView):
    """
    Создание и получение списка подзадач
    Задание 1: Автоматическое добавление владельца
    """
    serializer_class = SubTaskCreateSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline', 'task']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'title']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Задание 1: Автоматическое добавление владельца при создании"""
        serializer.save(owner=self.request.user)


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление и удаление подзадачи
    Задание 2: Применение кастомных пермишенов
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskCreateSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsSubTaskOwner()]


# ==============================================
# ЗАДАНИЕ 1: ПРЕДСТАВЛЕНИЕ ДЛЯ ПОЛУЧЕНИЯ ЗАДАЧ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
# ==============================================

class MyTasksView(generics.ListAPIView):
    """
    Представление для получения задач текущего пользователя
    Задание 1: Фильтрация задач по текущему пользователю
    """
    serializer_class = TaskDetailSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращаем только задачи текущего пользователя"""
        return Task.objects.filter(owner=self.request.user).order_by('-created_at')


# ==============================================
# ПРЕДСТАВЛЕНИЯ ДЛЯ КАТЕГОРИЙ
# ==============================================

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'count_tasks']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return CategoryCreateSerializer
        return CategorySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(
            {
                'message': f'Категория "{instance.name}" успешно удалена',
                'deleted_at': instance.deleted_at,
                'category_id': instance.id
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        tasks_count = category.tasks.count()

        return Response({
            'category_id': category.id,
            'category_name': category.name,
            'total_tasks': tasks_count
        })


# ==============================================
# ДРУГИЕ ПРЕДСТАВЛЕНИЯ
# ==============================================

class TaskStatsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

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


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]