from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from .models import Task, SubTask, Category


# ==============================================
# ЗАДАНИЕ 1: СЕРИАЛИЗАТОР ДЛЯ РЕГИСТРАЦИИ
# ==============================================

class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя
    Задание 1: Валидация полей, сложность пароля, хэширование
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator()]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'username': {
                'validators': [
                    RegexValidator(
                        regex='^[a-zA-Z0-9_]+$',
                        message='Имя пользователя может содержать только буквы, цифры и подчеркивания'
                    )
                ]
            },
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, attrs):
        """Задание 1: Валидация данных"""
        # Проверка совпадения паролей
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})

        # Проверка уникальности email
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже существует"})

        # Проверка уникальности username
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Пользователь с таким именем уже существует"})

        # Минимальная длина username
        if len(attrs['username']) < 3:
            raise serializers.ValidationError({"username": "Имя пользователя должно быть не менее 3 символов"})

        return attrs

    def create(self, validated_data):
        """Задание 1: Хэширование и сохранение пароля"""
        # Удаляем password2, так как он не нужен в модели
        validated_data.pop('password2')

        # Создаем пользователя с хэшированным паролем
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        return user


# ==============================================
# ЗАДАНИЕ 2: СЕРИАЛИЗАТОР ДЛЯ ЛОГИНА
# ==============================================

class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа в систему
    Задание 2: Проверка корректности данных
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Задание 2: Проверка существования пользователя и валидация пароля"""
        username = attrs.get('username')
        password = attrs.get('password')

        # Проверяем, что оба поля заполнены
        if not username or not password:
            raise serializers.ValidationError("Необходимо указать имя пользователя и пароль")

        # Проверяем существование пользователя
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким именем не найден")

        # Проверяем пароль
        if not user.check_password(password):
            raise serializers.ValidationError("Неверный пароль")

        # Проверяем активность пользователя
        if not user.is_active:
            raise serializers.ValidationError("Учетная запись неактивна")

        attrs['user'] = user
        return attrs


# ==============================================
# СЕРИАЛИЗАТОР ДЛЯ СМЕНЫ ПАРОЛЯ
# ==============================================

class ChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Новые пароли не совпадают"})
        return attrs


# ==============================================
# СЕРИАЛИЗАТОР ДЛЯ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ
# ==============================================

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')


# ==============================================
# СУЩЕСТВУЮЩИЕ СЕРИАЛИЗАТОРЫ
# ==============================================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'owner']
        read_only_fields = ['id', 'owner']


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'owner', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'owner', 'deadline', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']