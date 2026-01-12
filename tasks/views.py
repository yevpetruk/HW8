from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.utils import timezone
from .models import Task, SubTask, Category
from .serializers import (
    # Для задания 1
    SubTaskCreateSerializer,
    # Для задания 2
    CategoryCreateSerializer,
    # Для задания 3
    TaskDetailSerializer,
    # Для задания 4
    TaskCreateSerializer,
    # Дополнительные
    SubTaskUpdateSerializer,
    TaskListSerializer,
    CategorySerializer
)


# ==============================================
# ЗАДАНИЕ 5: SubTaskListCreateView
# ==============================================

class SubTaskListCreateView(APIView):
    """
    Класс представления для создания и получения списка подзадач
    Задание 5: Создание и получение списка подзадач
    """

    def get(self, request):
        """
        Получение списка всех подзадач
        GET /api/subtasks/
        """
        try:
            # Получаем все подзадачи
            subtasks = SubTask.objects.all().order_by('-created_at')

            # Используем сериализатор из задания 1
            serializer = SubTaskCreateSerializer(subtasks, many=True)

            return Response({
                'count': len(subtasks),
                'results': serializer.data
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Создание новой подзадачи
        POST /api/subtasks/
        """
        try:
            # Используем сериализатор из задания 1
            serializer = SubTaskCreateSerializer(data=request.data)

            # Проверяем валидность данных
            if serializer.is_valid():
                # Сохраняем подзадачу
                subtask = serializer.save()

                return Response(
                    {
                        'message': 'Подзадача успешно создана',
                        'data': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                # Возвращаем ошибки валидации
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==============================================
# ЗАДАНИЕ 5: SubTaskDetailUpdateDeleteView
# ==============================================

class SubTaskDetailUpdateDeleteView(APIView):
    """
    Класс представления для получения, обновления и удаления подзадач
    Задание 5: Детали, обновление и удаление подзадачи
    """

    def get_object(self, pk):
        """
        Вспомогательный метод для получения подзадачи по ID
        """
        try:
            return SubTask.objects.get(pk=pk)
        except SubTask.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Получение деталей подзадачи по ID
        GET /api/subtasks/<pk>/
        """
        try:
            subtask = self.get_object(pk)
            serializer = SubTaskCreateSerializer(subtask)
            return Response(serializer.data)

        except Http404:
            return Response(
                {'error': 'Подзадача не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Полное обновление подзадачи
        PUT /api/subtasks/<pk>/
        """
        try:
            subtask = self.get_object(pk)

            # Используем сериализатор для обновления
            serializer = SubTaskUpdateSerializer(subtask, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'message': 'Подзадача успешно обновлена',
                        'data': serializer.data
                    }
                )
            else:
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Http404:
            return Response(
                {'error': 'Подзадача не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, pk):
        """
        Частичное обновление подзадачи
        PATCH /api/subtasks/<pk>/
        """
        try:
            subtask = self.get_object(pk)

            # Используем сериализатор для частичного обновления
            serializer = SubTaskUpdateSerializer(subtask, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'message': 'Подзадача успешно обновлена (частично)',
                        'data': serializer.data
                    }
                )
            else:
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Http404:
            return Response(
                {'error': 'Подзадача не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk):
        """
        Удаление подзадачи
        DELETE /api/subtasks/<pk>/
        """
        try:
            subtask = self.get_object(pk)
            subtask.delete()

            return Response(
                {'message': 'Подзадача успешно удалена'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Http404:
            return Response(
                {'error': 'Подзадача не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==============================================
# ДОПОЛНИТЕЛЬНЫЕ ПРЕДСТАВЛЕНИЯ (для тестирования всех заданий)
# ==============================================

class TaskListView(APIView):
    """
    Получение списка задач с TaskDetailSerializer (задание 3)
    """

    def get(self, request):
        tasks = Task.objects.all().order_by('-created_at')
        serializer = TaskDetailSerializer(tasks, many=True)
        return Response({
            'count': len(tasks),
            'results': serializer.data
        })


class TaskCreateView(APIView):
    """
    Создание задачи с TaskCreateSerializer (задание 4)
    """

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)

        if serializer.is_valid():
            task = serializer.save()
            return Response(
                {
                    'message': 'Задача успешно создана',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )


class TaskDetailView(APIView):
    """
    Получение деталей задачи с TaskDetailSerializer (задание 3)
    """

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            serializer = TaskDetailSerializer(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Задача не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )


class CategoryCreateView(APIView):
    """
    Создание категории с CategoryCreateSerializer (задание 2)
    """

    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)

        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {
                    'message': 'Категория успешно создана',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryListView(APIView):
    """
    Получение списка категорий
    """

    def get(self, request):
        categories = Category.objects.all().order_by('name')
        serializer = CategorySerializer(categories, many=True)
        return Response({
            'count': len(categories),
            'results': serializer.data
        })


class TestAPIView(APIView):
    """
    Тестовый эндпоинт для проверки работы API
    """

    def get(self, request):
        return Response({
            'message': 'API менеджера задач работает!',
            'endpoints': {
                'subtasks': {
                    'list_create': '/api/subtasks/',
                    'detail_update_delete': '/api/subtasks/<id>/'
                },
                'tasks': {
                    'list': '/api/tasks/',
                    'create': '/api/tasks/create/',
                    'detail': '/api/tasks/<id>/'
                },
                'categories': {
                    'list': '/api/categories/',
                    'create': '/api/categories/create/'
                }
            }
        })