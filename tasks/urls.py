from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # ViewSet для категорий
    path('', include(router.urls)),

    # Задачи
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:id>/', views.TaskRetrieveUpdateDestroyView.as_view(),
         name='task-detail-update-delete'),

    # Задание 1: Задачи текущего пользователя
    path('tasks/my/', views.MyTasksView.as_view(), name='my-tasks'),

    # Подзадачи
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:id>/', views.SubTaskRetrieveUpdateDestroyView.as_view(),
         name='subtask-detail-update-delete'),

    # Статистика
    path('tasks/stats/', views.TaskStatsAPIView.as_view(), name='task-stats'),

    # Регистрация
    path('register/', views.RegisterView.as_view(), name='register'),
]