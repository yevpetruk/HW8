from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # ViewSet для категорий
    path('', include(router.urls)),

    # ==============================================
    # ЗАДАНИЕ 1, 2, 3: АУТЕНТИФИКАЦИЯ
    # ==============================================

    # Регистрация
    path('register/', views.RegisterView.as_view(), name='register'),

    # Вход (кастомный)
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),

    # Выход
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Обновление токена
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),

    # Профиль пользователя
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # ==============================================
    # API ДЛЯ ЗАДАЧ
    # ==============================================

    # Задачи
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:id>/', views.TaskRetrieveUpdateDestroyView.as_view(),
         name='task-detail-update-delete'),
    path('tasks/my/', views.MyTasksView.as_view(), name='my-tasks'),

    # Подзадачи
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:id>/', views.SubTaskRetrieveUpdateDestroyView.as_view(),
         name='subtask-detail-update-delete'),

    # Статистика
    path('tasks/stats/', views.TaskStatsAPIView.as_view(), name='task-stats'),
]