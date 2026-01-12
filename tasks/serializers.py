from rest_framework import serializers
from django.utils import timezone
from .models import Task, SubTask, Category


# ==============================================
# ЗАДАНИЕ 1: SubTaskCreateSerializer
# ==============================================

class SubTaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания подзадач
    Поле created_at доступно только для чтения
    """

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'task', 'deadline', 'created_at']
        read_only_fields = ['created_at']  # Задание 1: created_at только для чтения
        extra_kwargs = {
            'title': {'required': True},
            'task': {'required': True},
            'status': {'default': 'new'},
        }


# ==============================================
# ЗАДАНИЕ 2: CategoryCreateSerializer
# ==============================================

class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления категорий
    С проверкой уникальности названия
    """

    class Meta:
        model = Category
        fields = ['id', 'name']

    # Задание 2: Переопределение метода create
    def create(self, validated_data):
        """
        Создание категории с проверкой уникальности названия
        """
        name = validated_data.get('name')

        # Проверяем, существует ли категория с таким названием
        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                {'name': f'Категория с названием "{name}" уже существует.'}
            )

        # Создаем категорию
        return Category.objects.create(**validated_data)

    # Задание 2: Переопределение метода update
    def update(self, instance, validated_data):
        """
        Обновление категории с проверкой уникальности названия
        """
        new_name = validated_data.get('name', instance.name)

        # Проверяем, существует ли другая категория с таким названием
        if Category.objects.filter(name=new_name).exclude(id=instance.id).exists():
            raise serializers.ValidationError(
                {'name': f'Категория с названием "{new_name}" уже существует.'}
            )

        # Обновляем данные
        instance.name = new_name
        instance.save()

        return instance


# ==============================================
# ДЛЯ ЗАДАНИЯ 3: Вспомогательный SubTaskSerializer
# ==============================================

class SubTaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения подзадач
    Используется во вложенных сериализаторах
    """
    # Отображаем статус в читаемом виде
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Проверяем просроченность
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'status_display',
                  'deadline', 'created_at', 'is_overdue']
        read_only_fields = ['id', 'created_at']

    def get_is_overdue(self, obj):
        """Проверяем, просрочена ли подзадача"""
        if obj.deadline:
            return obj.deadline < timezone.now()
        return False


# ==============================================
# ЗАДАНИЕ 3: TaskDetailSerializer с вложенными подзадачами
# ==============================================

class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального отображения задачи
    Включает вложенные подзадачи
    """
    # Задание 3: Вложенный сериализатор для подзадач
    subtasks = SubTaskSerializer(many=True, read_only=True)

    # Отображаем статус в читаемом виде
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Категории как список имен
    categories = serializers.StringRelatedField(many=True, read_only=True)

    # Проверяем просроченность
    is_overdue = serializers.SerializerMethodField()

    # Количество подзадач
    subtasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'categories', 'subtasks', 'subtasks_count',
            'deadline', 'created_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at']

    def get_is_overdue(self, obj):
        """Проверяем, просрочена ли задача"""
        if obj.deadline:
            return obj.deadline < timezone.now()
        return False

    def get_subtasks_count(self, obj):
        """Получаем количество подзадач"""
        return obj.subtasks.count()


# ==============================================
# ЗАДАНИЕ 4: TaskCreateSerializer с валидацией deadline
# ==============================================

class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания задач
    С валидацией поля deadline
    """

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'title': {'required': True},
            'status': {'default': 'new'},
        }

    # Задание 4: Валидация поля deadline
    def validate_deadline(self, value):
        """
        Проверяем, что дедлайн не в прошлом
        """
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Дедлайн не может быть в прошлом. Пожалуйста, укажите будущую дату."
            )
        return value

    def validate(self, data):
        """
        Дополнительная валидация всех данных
        """
        # Можно добавить дополнительные проверки
        if data.get('title', '').strip() == '':
            raise serializers.ValidationError({
                'title': 'Название задачи не может быть пустым.'
            })

        return data


# ==============================================
# ДОПОЛНИТЕЛЬНЫЕ СЕРИАЛИЗАТОРЫ (для полноты)
# ==============================================

class CategorySerializer(serializers.ModelSerializer):
    """
    Простой сериализатор для категорий (только чтение)
    """

    class Meta:
        model = Category
        fields = ['id', 'name']


class TaskListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка задач (без деталей)
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    subtasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'status_display',
                  'categories', 'subtasks_count', 'deadline', 'created_at']

    def get_subtasks_count(self, obj):
        return obj.subtasks.count()


class SubTaskUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления подзадач
    """

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'deadline']
        read_only_fields = ['id']