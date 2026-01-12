from django.urls import path
from . import views

urlpatterns = [
    # Задание 1: Создание задачи
    path('tasks/create/', views.create_task, name='task-create'),

    # Задание 2: Получение списка задач и конкретной задачи
    path('tasks/', views.task_list, name='task-list'),
    path('tasks/<int:id>/', views.task_detail, name='task-detail'),

    # Задание 3: Статистика
    path('tasks/stats/', views.task_stats, name='task-stats'),
]