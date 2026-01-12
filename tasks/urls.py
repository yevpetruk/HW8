from django.urls import path
from . import views

urlpatterns = [
    # ==============================================
    # ЗАДАНИЕ 1: ЗАДАЧИ ПО ДНЮ НЕДЕЛИ
    # ==============================================
    path('tasks/by-weekday/', views.TaskListByWeekdayView.as_view(),
         name='tasks-by-weekday'),

    # ==============================================
    # ЗАДАНИЕ 2: ПАГИНИРОВАННЫЕ ПОДЗАДАЧИ
    # ==============================================
    path('subtasks/paginated/', views.SubTaskListView.as_view(),
         name='subtasks-paginated'),

    # ==============================================
    # ЗАДАНИЕ 3: ФИЛЬТРАЦИЯ ПОДЗАДАЧ
    # ==============================================
    path('subtasks/filter/', views.SubTaskFilterView.as_view(),
         name='subtasks-filter'),

    # ==============================================
    # ВСПОМОГАТЕЛЬНЫЕ ЭНДПОИНТЫ
    # ==============================================
    path('create-test-data/', views.CreateTestDataView.as_view(),
         name='create-test-data'),
]