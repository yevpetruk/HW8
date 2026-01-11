from django.contrib import admin
from .models import Task, SubTask, Category


# 1. Настройка админки для Category
class CategoryAdmin(admin.ModelAdmin):
    # Что отображать в списке
    list_display = ('id', 'name')

    # По каким полям можно кликать для редактирования
    list_display_links = ('id', 'name')

    # По каким полям можно искать
    search_fields = ('name',)

    # Сортировка по умолчанию
    ordering = ('name',)


# 2. Настройка админки для Task
class TaskAdmin(admin.ModelAdmin):
    # Что отображать в списке
    list_display = ('id', 'title', 'status', 'deadline', 'created_at')

    # По каким полям можно кликать для редактирования
    list_display_links = ('id', 'title')

    # Фильтры справа
    list_filter = ('status', 'categories', 'deadline')

    # По каким полям можно искать
    search_fields = ('title', 'description')

    # Удобный виджет для ManyToMany поля
    filter_horizontal = ('categories',)

    # Сортировка по умолчанию
    ordering = ('-created_at',)

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'categories')
        }),
        ('Статус и время', {
            'fields': ('status', 'deadline')
        }),
    )


# 3. Настройка админки для SubTask
class SubTaskAdmin(admin.ModelAdmin):
    # Что отображать в списке
    list_display = ('id', 'title', 'task', 'status', 'deadline', 'created_at')

    # По каким полям можно кликать для редактирования
    list_display_links = ('id', 'title')

    # Фильтры справа
    list_filter = ('status', 'task', 'deadline')

    # По каким полям можно искать
    search_fields = ('title', 'description')

    # Сортировка по умолчанию
    ordering = ('-created_at',)

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'task')
        }),
        ('Статус и время', {
            'fields': ('status', 'deadline')
        }),
    )


# Регистрируем модели с нашими настройками
admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)