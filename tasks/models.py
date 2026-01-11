from django.db import models


# 1. Модель Category (Категория)
class Category(models.Model):
    # Поля модели
    name = models.CharField(max_length=100, unique=True)

    # Метод __str__ для отображения в админке и консоли
    def __str__(self):
        return self.name

    # Класс Meta для настроек модели
    class Meta:
        db_table = 'task_manager_category'  # Имя таблицы в базе данных
        verbose_name = 'Category'  # Человекочитаемое имя в единственном числе
        verbose_name_plural = 'Categories'  # Человекочитаемое имя во множественном числе


# 2. Модель Task (Задача)
class Task(models.Model):
    # Выбор статуса (choices)
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    # Поля модели
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Метод __str__ для отображения в админке и консоли
    def __str__(self):
        return self.title

    # Класс Meta для настроек модели
    class Meta:
        db_table = 'task_manager_task'  # Имя таблицы в базе данных
        ordering = ['-created_at']  # Сортировка по убыванию даты создания
        verbose_name = 'Task'  # Человекочитаемое имя в единственном числе
        verbose_name_plural = 'Tasks'  # Человекочитаемое имя во множественном числе


# 3. Модель SubTask (Подзадача)
class SubTask(models.Model):
    # Выбор статуса (choices)
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    # Поля модели
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Метод __str__ для отображения в админке и консоли
    def __str__(self):
        return f"{self.title} (задача: {self.task.title})"

    # Класс Meta для настроек модели
    class Meta:
        db_table = 'task_manager_subtask'
        ordering = ['-created_at']  # Сортировка по убыванию даты создания
        verbose_name = 'SubTask'
        verbose_name_plural = 'SubTasks'
