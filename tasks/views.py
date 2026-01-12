from rest_framework import viewsets, status, generics, filters, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta

from . import serializers
from .models import Task, SubTask, Category
from .serializers import (
    TaskDetailSerializer,
    TaskCreateSerializer,
    SubTaskSerializer,
    CategorySerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer
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
# ЗАДАНИЕ 1: РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
# ==============================================

class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя
    Задание 1: Валидация, сложность пароля, хэширование
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Создаем пользователя
        user = serializer.save()

        # Создаем JWT токены для нового пользователя
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


# ==============================================
# ЗАДАНИЕ 2: ВХОД В АККАУНТ (КАСТОМНЫЙ)
# ==============================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Кастомный view для входа с расширенной валидацией
    Задание 2: Проверка данных, возврат JWT токенов
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем пользователя из валидированных данных
        user = serializer.validated_data.get('user')

        # Создаем токены
        refresh = RefreshToken.for_user(user)

        # Обновляем last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        response_data = {
            'message': 'Вход выполнен успешно',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }

        # Задание 2: Безопасное хранение в httpOnly cookies (опционально)
        response = Response(response_data, status=status.HTTP_200_OK)

        # Устанавливаем cookies (для браузерных клиентов)
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,  # True в production с HTTPS
            samesite='Lax',
            max_age=7 * 24 * 60 * 60  # 7 дней
        )

        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 60  # 1 час
        )

        return response


# ==============================================
# ЗАДАНИЕ 3: ВЫХОД ИЗ АККАУНТА
# ==============================================

class LogoutView(APIView):
    """
    Выход из системы
    Задание 3: Помещение токенов в blacklist
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Получаем refresh токен из запроса
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                # Пробуем получить из cookies
                refresh_token = request.COOKIES.get('refresh_token')

            if refresh_token:
                # Помещаем токен в blacklist
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Очищаем cookies
            response = Response(
                {"message": "Выход выполнен успешно"},
                status=status.HTTP_200_OK
            )

            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            # Выход из сессии Django (если используется)
            logout(request)

            return response

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==============================================
# ОБНОВЛЕНИЕ ACCESS ТОКЕНА
# ==============================================

class TokenRefreshView(APIView):
    """
    Обновление access токена через refresh токен
    Задание 2: Механизм обновления
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            # Пробуем получить из cookies
            refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"error": "Refresh токен не предоставлен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Пробуем обновить токен
            refresh = RefreshToken(refresh_token)

            # Помещаем старый токен в blacklist (если включено)
            try:
                refresh.blacklist()
            except Exception:
                pass  # Игнорируем, если blacklist не настроен

            # Создаем новые токены
            new_refresh = RefreshToken.for_user(refresh.access_token.payload['user_id'])

            return Response({
                'access': str(new_refresh.access_token),
                'refresh': str(new_refresh),
            })

        except TokenError as e:
            return Response(
                {"error": "Неверный или просроченный refresh токен"},
                status=status.HTTP_401_UNAUTHORIZED
            )


# ==============================================
# ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
# ==============================================

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Профиль текущего пользователя
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    Смена пароля
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Проверяем старый пароль
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": "Неверный пароль"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Устанавливаем новый пароль
            user.set_password(serializer.data.get("new_password"))
            user.save()

            return Response(
                {"message": "Пароль успешно изменен"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================
# СУЩЕСТВУЮЩИЕ ПРЕДСТАВЛЕНИЯ (ОБНОВЛЯЕМ)
# ==============================================

class TaskListCreateView(generics.ListCreateAPIView):
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
        queryset = Task.objects.all()
        if self.request.user.is_authenticated:
            my_tasks = self.request.query_params.get('my_tasks', '')
            if my_tasks.lower() == 'true':
                queryset = queryset.filter(owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsTaskOwner()]


class SubTaskListCreateView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
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
        serializer.save(owner=self.request.user)


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsSubTaskOwner()]


class MyTasksView(generics.ListAPIView):
    serializer_class = TaskDetailSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user).order_by('-created_at')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'count_tasks']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

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