from rest_framework import serializers
from .models import Task, SubTask, Category
from django.utils import timezone


# Сериализатор для категорий
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# Сериализатор для создания и обновления задач
class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    # Кастомная валидация для поля deadline
    def validate_deadline(self, value):
        """
        Проверяем, что дедлайн не в прошлом
        """
        if value and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом!")
        return value

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']  # Эти поля только для чтения
        extra_kwargs = {
            'title': {'required': True},
            'status': {'required': True, 'default': 'new'},
        }


# Сериализатор для отображения задач (с деталями)
class TaskDetailSerializer(serializers.ModelSerializer):
    # Включаем категории
    categories = CategorySerializer(many=True, read_only=True)

    # Включаем подзадачи
    subtasks = serializers.SerializerMethodField()

    # Статус в человекочитаемом виде
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Проверка просроченности
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'categories', 'subtasks', 'deadline', 'created_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at']

    def get_subtasks(self, obj):
        """Получаем список подзадач"""
        from .serializers import SubTaskSerializer
        subtasks = obj.subtasks.all()
        return SubTaskSerializer(subtasks, many=True).data

    def get_is_overdue(self, obj):
        """Проверяем, просрочена ли задача"""
        if obj.deadline:
            return obj.deadline < timezone.now()
        return False


# Сериализатор для подзадач
class SubTaskSerializer(serializers.ModelSerializer):
    # ID задачи для удобства
    task_id = serializers.PrimaryKeyRelatedField(source='task', queryset=Task.objects.all())

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'task_id', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']


# Сериализатор для статистики
class TaskStatsSerializer(serializers.Serializer):
    # Общая статистика
    total_tasks = serializers.IntegerField()
    total_overdue = serializers.IntegerField()

    # Статистика по статусам
    status_new = serializers.IntegerField()
    status_in_progress = serializers.IntegerField()
    status_pending = serializers.IntegerField()
    status_blocked = serializers.IntegerField()
    status_done = serializers.IntegerField()

    # Процент выполнения
    completion_rate = serializers.FloatField()

    class Meta:
        fields = [
            'total_tasks', 'total_overdue',
            'status_new', 'status_in_progress', 'status_pending',
            'status_blocked', 'status_done', 'completion_rate'
        ]