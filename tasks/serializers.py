from rest_framework import serializers
from django.utils import timezone
from .models import Task, SubTask, Category


# Сериализатор для создания и обновления задач
class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        """Валидация дедлайна"""
        if value and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом")
        return value


# Сериализатор для детального отображения задач
class TaskDetailSerializer(serializers.ModelSerializer):
    # Включаем подзадачи
    subtasks = serializers.SerializerMethodField()

    # Включаем категории
    categories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'categories', 'subtasks', 'deadline', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_subtasks(self, obj):
        """Получаем подзадачи"""
        subtasks = obj.subtasks.all()
        return SubTaskSerializer(subtasks, many=True).data


# Сериализатор для создания и обновления подзадач
class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'task', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']


# Сериализатор для отображения подзадач
class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']


# Сериализатор для категорий
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']