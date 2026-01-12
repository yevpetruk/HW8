from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаем router для ViewSet
router = DefaultRouter()
# Задание 1: Регистрируем CategoryViewSet
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # ==============================================
    # ЗАДАНИЕ 1: ROUTER ДЛЯ CATEGORYVIEWSET
    # ==============================================
    path('', include(router.urls)),

    # ==============================================
    # СУЩЕСТВУЮЩИЕ GENERIC VIEWS
    # ==============================================

    # Задачи
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:id>/', views.TaskRetrieveUpdateDestroyView.as_view(),
         name='task-detail-update-delete'),

    # Подзадачи
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:id>/', views.SubTaskRetrieveUpdateDestroyView.as_view(),
         name='subtask-detail-update-delete'),

    # ==============================================
    # АГРЕГИРУЮЩИЕ ЭНДПОИНТЫ
    # ==============================================

    # Статистика задач
    path('tasks/stats/', views.TaskStatsAPIView.as_view(), name='task-stats'),

    # ==============================================
    # ВСПОМОГАТЕЛЬНЫЕ ЭНДПОИНТЫ
    # ==============================================

    # Создание тестовых данных
    path('create-test-data/', views.CreateTestDataView.as_view(), name='create-test-data'),
]