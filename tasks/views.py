# tasks/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Task
import json


# ============ ЗАДАНИЕ 1: СОЗДАНИЕ ЗАДАЧИ ============
@api_view(['POST'])
def create_task(request):
    """
    Эндпоинт для создания новой задачи
    POST /api/tasks/create/
    """
    try:
        # Получаем данные из запроса
        data = request.data

        # Создаем задачу
        task = Task.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            status=data.get('status', 'new'),
            deadline=data.get('deadline')
        )

        # Возвращаем успешный ответ
        return Response({
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'message': 'Задача успешно создана'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Ошибка при создании задачи'
        }, status=status.HTTP_400_BAD_REQUEST)


# ============ ЗАДАНИЕ 2: ПОЛУЧЕНИЕ ЗАДАЧ ============
@api_view(['GET'])
def task_list(request):
    """
    Эндпоинт для получения списка всех задач
    GET /api/tasks/
    """
    try:
        tasks = Task.objects.all().order_by('-created_at')

        # Преобразуем в список словарей
        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'deadline': task.deadline,
                'created_at': task.created_at,
                'is_overdue': task.deadline < timezone.now() if task.deadline else False
            })

        return Response({
            'count': len(tasks_data),
            'tasks': tasks_data
        })

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_detail(request, id):
    """
    Эндпоинт для получения конкретной задачи по ID
    GET /api/tasks/<id>/
    """
    try:
        task = Task.objects.get(id=id)

        return Response({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'deadline': task.deadline,
            'created_at': task.created_at,
            'categories': [cat.name for cat in task.categories.all()],
            'subtasks_count': task.subtasks.count(),
            'is_overdue': task.deadline < timezone.now() if task.deadline else False
        })

    except Task.DoesNotExist:
        return Response({
            'error': 'Задача не найдена'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# ============ ЗАДАНИЕ 3: СТАТИСТИКА ============
@api_view(['GET'])
def task_stats(request):
    """
    Эндпоинт для получения статистики задач
    GET /api/tasks/stats/
    """
    try:
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

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)