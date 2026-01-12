from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q
from .models import Task, SubTask, Category
from .serializers import TaskDetailSerializer, SubTaskCreateSerializer


# ==============================================
# КАСТОМНЫЙ ПАГИНАТОР ДЛЯ ЗАДАНИЯ 2
# ==============================================

class SubTaskPagination(PageNumberPagination):
    """
    Пагинация для подзадач
    Задание 2: 5 объектов на страницу
    """
    page_size = 5  # 5 объектов на страницу
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Кастомный ответ с пагинацией"""
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


# ==============================================
# ЗАДАНИЕ 1: СПИСОК ЗАДАЧ ПО ДНЮ НЕДЕЛИ
# ==============================================

class TaskListByWeekdayView(APIView):
    """
    Эндпоинт для получения списка задач по дню недели
    Задание 1: Фильтрация по дню недели
    """

    def get(self, request):
        """
        GET /api/tasks/by-weekday/
        Параметры:
        - weekday: номер дня недели (1-7, где 1=понедельник)
        - weekday_name: название дня недели (понедельник, вторник и т.д.)
        """
        # Получаем параметр дня недели
        weekday = request.query_params.get('weekday')
        weekday_name = request.query_params.get('weekday_name')

        # Начинаем с всех задач
        tasks = Task.objects.all()

        # Если передан номер дня недели
        if weekday:
            try:
                weekday_int = int(weekday)
                if 1 <= weekday_int <= 7:
                    # Фильтруем задачи, у которых дедлайн в указанный день недели
                    tasks = tasks.filter(
                        deadline__week_day=weekday_int
                    )
                else:
                    return Response(
                        {'error': 'Номер дня недели должен быть от 1 до 7'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Номер дня недели должен быть числом'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Если передано название дня недели
        elif weekday_name:
            # Русские названия дней недели
            weekdays_ru = {
                'понедельник': 2,  # В Django неделя начинается с воскресенья (1)
                'вторник': 3,
                'среда': 4,
                'четверг': 5,
                'пятница': 6,
                'суббота': 7,
                'воскресенье': 1,
                'пн': 2,
                'вт': 3,
                'ср': 4,
                'чт': 5,
                'пт': 6,
                'сб': 7,
                'вс': 1,
            }

            weekday_lower = weekday_name.lower()
            if weekday_lower in weekdays_ru:
                tasks = tasks.filter(
                    deadline__week_day=weekdays_ru[weekday_lower]
                )
            else:
                return Response(
                    {'error': 'Неверное название дня недели'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Сортируем по дате создания (от новых к старым)
        tasks = tasks.order_by('-created_at')

        # Сериализуем данные
        serializer = TaskDetailSerializer(tasks, many=True)

        return Response({
            'count': tasks.count(),
            'weekday_filter': weekday or weekday_name or 'не применен',
            'results': serializer.data
        })


# ==============================================
# ЗАДАНИЕ 2: ПАГИНИРОВАННЫЙ СПИСОК ПОДЗАДАЧ
# ==============================================

class SubTaskListView(APIView):
    """
    Эндпоинт для получения пагинированного списка подзадач
    Задание 2: Пагинация (5 объектов на страницу)
    """

    def get(self, request):
        """
        GET /api/subtasks/paginated/
        """
        # Получаем все подзадачи
        subtasks = SubTask.objects.all()

        # Задание 2: Сортировка по убыванию даты создания
        subtasks = subtasks.order_by('-created_at')

        # Применяем пагинацию
        paginator = SubTaskPagination()
        page = paginator.paginate_queryset(subtasks, request)

        if page is not None:
            serializer = SubTaskCreateSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Если пагинация не применена (мало данных)
        serializer = SubTaskCreateSerializer(subtasks, many=True)
        return Response({
            'count': subtasks.count(),
            'results': serializer.data
        })


# ==============================================
# ЗАДАНИЕ 3: ФИЛЬТРАЦИЯ ПОДЗАДАЧ ПО ЗАДАЧЕ И СТАТУСУ
# ==============================================

class SubTaskFilterView(APIView):
    """
    Эндпоинт для фильтрации подзадач по названию задачи и статусу
    Задание 3: Фильтрация с пагинацией
    """

    def get(self, request):
        """
        GET /api/subtasks/filter/
        Параметры:
        - task_title: название главной задачи
        - status: статус подзадачи
        - page: номер страницы (для пагинации)
        """
        # Получаем параметры фильтрации
        task_title = request.query_params.get('task_title', '').strip()
        status_filter = request.query_params.get('status', '').strip()

        # Начинаем со всех подзадач
        subtasks = SubTask.objects.all()

        # Применяем фильтры

        # Фильтр по названию задачи
        if task_title:
            subtasks = subtasks.filter(
                task__title__icontains=task_title
            )

        # Фильтр по статусу
        if status_filter:
            # Проверяем, что статус валидный
            valid_statuses = ['new', 'in_progress', 'pending', 'blocked', 'done']
            if status_filter in valid_statuses:
                subtasks = subtasks.filter(status=status_filter)
            else:
                return Response(
                    {'error': f'Неверный статус. Допустимые значения: {", ".join(valid_statuses)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Задание 2: Сортировка по убыванию даты создания
        subtasks = subtasks.order_by('-created_at')

        # Применяем пагинацию (5 объектов на страницу)
        paginator = SubTaskPagination()
        page = paginator.paginate_queryset(subtasks, request)

        if page is not None:
            serializer = SubTaskCreateSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Если пагинация не применена
        serializer = SubTaskCreateSerializer(subtasks, many=True)

        return Response({
            'count': subtasks.count(),
            'filters_applied': {
                'task_title': task_title if task_title else 'не применен',
                'status': status_filter if status_filter else 'не применен'
            },
            'results': serializer.data
        })


# ==============================================
# ДОПОЛНИТЕЛЬНЫЕ ПРЕДСТАВЛЕНИЯ
# ==============================================

class CreateTestDataView(APIView):
    """Создание тестовых данных для проверки"""

    def post(self, request):
        """Создание тестовых задач с разными датами"""
        from datetime import timedelta

        # Создаем тестовые задачи на разные дни недели
        days_of_week = [
            ("Понедельник задача", "Задача на понедельник", 1),
            ("Вторник задача", "Задача на вторник", 2),
            ("Среда задача", "Задача на среду", 3),
            ("Четверг задача", "Задача на четверг", 4),
            ("Пятница задача", "Задача на пятницу", 5),
            ("Суббота задача", "Задача на субботу", 6),
            ("Воскресенье задача", "Задача на воскресенье", 7),
        ]

        created_tasks = []

        for title, description, days_ahead in days_of_week:
            # Создаем задачу
            task = Task.objects.create(
                title=title,
                description=description,
                status='new',
                deadline=timezone.now() + timedelta(days=days_ahead)
            )

            # Создаем несколько подзадач с разными статусами
            for i in range(3):
                SubTask.objects.create(
                    title=f"Подзадача {i + 1} для {title}",
                    description=f"Тестовая подзадача {i + 1}",
                    task=task,
                    status=['new', 'in_progress', 'done'][i % 3],
                    deadline=timezone.now() + timedelta(days=i + 1)
                )

            created_tasks.append({
                'id': task.id,
                'title': task.title,
                'deadline': task.deadline
            })

        return Response({
            'message': 'Тестовые данные созданы',
            'created_tasks': created_tasks,
            'total_tasks': Task.objects.count(),
            'total_subtasks': SubTask.objects.count()
        })