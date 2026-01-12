from rest_framework import serializers
from django.utils import timezone
from .models import Task, SubTask, Category


# ==============================================
# СЕРИАЛИЗАТОРЫ ДЛЯ CATEGORY
# ==============================================

class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категорий
    """
    # Поле для подсчета задач (только чтение)
    tasks_count = serializers.SerializerMethodField()

    # Статус удаления
    is_deleted = serializers.BooleanField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'tasks_count', 'is_deleted', 'deleted_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'tasks_count', 'is_deleted', 'deleted_at']

    def get_tasks_count(self, obj):
        """Получаем количество задач в категории"""
        return obj.tasks.count()

    def validate_name(self, value):
        """
        Валидация уникальности названия категории
        Проверяем только среди неудаленных категорий
        """
        # Проверяем, существует ли категория с таким именем (не удаленная)
        if Category.objects.filter(name=value, is_deleted=False).exists():
            # Если это обновление существующей категории
            if self.instance and self.instance.name == value:
                return value
            raise serializers.ValidationError(f'Категория с названием "{value}" уже существует.')
        return value


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания категорий
    """

    class Meta:
        model = Category
        fields = ['id', 'name']

    def validate_name(self, value):
        """Валидация уникальности при создании"""
        if Category.objects.filter(name=value, is_deleted=False).exists():
            raise serializers.ValidationError(f'Категория с названием "{value}" уже существует.')
        return value


# ==============================================
# СЕРИАЛИЗАТОРЫ ДЛЯ TASK И SUBTASK
# ==============================================

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом")
        return value


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'categories', 'subtasks', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_subtasks(self, obj):
        subtasks = obj.subtasks.all()
        return SubTaskSerializer(subtasks, many=True).data


class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'task', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']