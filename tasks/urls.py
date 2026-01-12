from django.urls import path
from . import views

urlpatterns = [
    # ==============================================
    # ЗАДАНИЕ 1: GENERIC VIEWS ДЛЯ ЗАДАЧ
    # ==============================================

    # ListCreateAPIView для задач
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),

    # RetrieveUpdateDestroyAPIView для задач
    path('tasks/<int:id>/', views.TaskRetrieveUpdateDestroyView.as_view(),
         name='task-detail-update-delete'),

    # ==============================================
    # ЗАДАНИЕ 2: GENERIC VIEWS ДЛЯ ПОДЗАДАЧ
    # ==============================================

    # ListCreateAPIView для подзадач
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),

    # RetrieveUpdateDestroyAPIView для подзадач
    path('subtasks/<int:id>/', views.SubTaskRetrieveUpdateDestroyView.as_view(),
         name='subtask-detail-update-delete'),

    # ==============================================
    # GENERIC VIEWS ДЛЯ КАТЕГОРИЙ
    # ==============================================

    # ListCreateAPIView для категорий
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),

    # RetrieveUpdateDestroyAPIView для категорий
    path('categories/<int:id>/', views.CategoryRetrieveUpdateDestroyView.as_view(),
         name='category-detail-update-delete'),

    # ==============================================
    # АГРЕГИРУЮЩИЙ ЭНДПОИНТ (ОСТАВЛЯЕМ)
    # ==============================================

    # Статистика задач
    path('tasks/stats/', views.TaskStatsAPIView.as_view(), name='task-stats'),

    # ==============================================
    # ВСПОМОГАТЕЛЬНЫЕ ЭНДПОИНТЫ
    # ==============================================

    # Создание тестовых данных
    path('create-test-data/', views.CreateTestDataView.as_view(), name='create-test-data'),
]