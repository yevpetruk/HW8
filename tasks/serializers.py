from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Task, SubTask, Category


# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


# Сериализатор для категорий (чтение) - ДОЛЖЕН БЫТЬ ПЕРВЫМ!
class CategorySerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'tasks_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'tasks_count']

    def get_tasks_count(self, obj):
        return obj.tasks.count()


# Сериализатор для создания категорий
class CategoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания категорий"""

    class Meta:
        model = Category
        fields = ['id', 'name']

    def validate_name(self, value):
        """Валидация уникальности при создании"""
        if Category.objects.filter(name=value, is_deleted=False).exists():
            raise serializers.ValidationError(f'Категория с названием "{value}" уже существует.')
        return value


# Сериализатор для создания задач
class TaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'owner', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом")
        return value


# Сериализатор для отображения задач
class TaskDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    subtasks = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)  # Теперь CategorySerializer определен!

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'owner', 'categories', 'subtasks',
            'deadline', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at']

    def get_subtasks(self, obj):
        subtasks = obj.subtasks.all()
        return SubTaskSerializer(subtasks, many=True).data


# Сериализатор для создания подзадач
class SubTaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'task', 'owner', 'deadline', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']


# Сериализатор для отображения подзадач
class SubTaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'owner', 'deadline', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']