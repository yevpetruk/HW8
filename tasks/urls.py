from django.urls import path
from . import views

urlpatterns = [
    # ==============================================
    # ТЕСТОВЫЙ ЭНДПОИНТ
    # ==============================================
    path('', views.TestAPIView.as_view(), name='api-root'),

    # ==============================================
    # ЗАДАНИЕ 5: ЭНДПОИНТЫ ДЛЯ ПОДЗАДАЧ
    # ==============================================

    # SubTaskListCreateView (Задание 5)
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),

    # SubTaskDetailUpdateDeleteView (Задание 5)
    path('subtasks/<int:pk>/', views.SubTaskDetailUpdateDeleteView.as_view(),
         name='subtask-detail-update-delete'),

    # ==============================================
    # ДОПОЛНИТЕЛЬНЫЕ ЭНДПОИНТЫ ДЛЯ ТЕСТИРОВАНИЯ
    # ==============================================

    # TaskListView с TaskDetailSerializer (Задание 3)
    path('tasks/', views.TaskListView.as_view(), name='task-list'),

    # TaskCreateView с TaskCreateSerializer (Задание 4)
    path('tasks/create/', views.TaskCreateView.as_view(), name='task-create'),

    # TaskDetailView с TaskDetailSerializer (Задание 3)
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),

    # CategoryCreateView с CategoryCreateSerializer (Задание 2)
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),

    # CategoryListView
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
]