# tasks/models.py
from django.db import models
from django.utils import timezone


# ==============================================
# КАСТОМНЫЙ МЕНЕДЖЕР ДЛЯ МЯГКОГО УДАЛЕНИЯ
# ==============================================

class SoftDeleteManager(models.Manager):
    """Менеджер для мягкого удаления"""

    def get_queryset(self):
        """
        Переопределяем метод get_queryset()
        По умолчанию показываем только неудаленные записи
        Задание 2: фильтрация is_deleted=False
        """
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        """Получить все записи, включая удаленные"""
        return super().get_queryset()

    def only_deleted(self):
        """Получить только удаленные записи"""
        return super().get_queryset().filter(is_deleted=True)


# ==============================================
# ОБНОВЛЕННАЯ МОДЕЛЬ CATEGORY С МЯГКИМ УДАЛЕНИЕМ
# ==============================================

class Category(models.Model):
    """
    Модель категории с мягким удалением
    Задание 2: добавление полей is_deleted и deleted_at
    """
    # Основное поле
    name = models.CharField(max_length=100, unique=True)

    # Задание 2: Поля для мягкого удаления
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Дата создания
    created_at = models.DateTimeField(auto_now_add=True)

    # Задание 2: Используем кастомный менеджер
    objects = SoftDeleteManager()  # Менеджер по умолчанию (только неудаленные)
    all_objects = models.Manager()  # Стандартный менеджер (все записи)

    def __str__(self):
        return self.name

    # Задание 2: Метод мягкого удаления
    def soft_delete(self):
        """
        Мягкое удаление категории
        Устанавливает is_deleted=True и deleted_at=текущее время
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    # Задание 2: Метод восстановления
    def restore(self):
        """
        Восстановление удаленной категории
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    class Meta:
        db_table = 'task_manager_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


# ==============================================
# СУЩЕСТВУЮЩИЕ МОДЕЛИ (ОСТАВЛЯЕМ БЕЗ ИЗМЕНЕНИЙ)
# ==============================================

class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'task_manager_task'
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class SubTask(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (задача: {self.task.title})"

    class Meta:
        db_table = 'task_manager_subtask'
        ordering = ['-created_at']
        verbose_name = 'SubTask'
        verbose_name_plural = 'SubTasks'