from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import Task, SubTask, Category


# 1. Инлайн форма для отображения подзадач внутри задачи
class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1  # Количество пустых форм для добавления подзадач
    fields = ('title', 'description', 'status', 'deadline')
    readonly_fields = ('created_at',)

    # Устанавливаем максимальное количество подзадач (опционально)
    max_num = 10

    def get_formset(self, request, obj=None, **kwargs):
        """
        Настройка формсета для инлайн форм
        """
        formset = super().get_formset(request, obj, **kwargs)

        # Если создаем новую задачу (obj=None), показываем все поля
        # Если редактируем существующую, можно добавить логику
        return formset


# 2. Настройка админки для Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


# 3. Настройка админки для Task
class TaskAdmin(admin.ModelAdmin):
    # Используем кастомный метод для отображения укороченного названия
    list_display = ('id', 'short_title', 'status', 'deadline', 'created_at', 'subtasks_count')
    list_display_links = ('id', 'short_title')
    list_filter = ('status', 'categories', 'deadline')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)
    ordering = ('-created_at',)

    # Добавляем инлайн формы для подзадач
    inlines = [SubTaskInline]

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'categories')
        }),
        ('Статус и время', {
            'fields': ('status', 'deadline')
        }),
    )

    # Кастомные методы для админки

    def short_title(self, obj):
        """
        Отображает только первые 10 символов названия задачи
        с добавлением '...' если название длиннее
        """
        # Обрезаем до 10 символов
        truncated = Truncator(obj.title).chars(10)

        # Если название было обрезано, добавляем многоточие
        if len(obj.title) > 10:
            return f"{truncated}..."
        return truncated

    # Настраиваем отображение заголовка колонки
    short_title.short_description = 'Название задачи'
    short_title.admin_order_field = 'title'  # Позволяет сортировать по полному названию

    def subtasks_count(self, obj):
        """
        Показывает количество подзадач у задачи
        """
        count = obj.subtasks.count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'gray',
            f"{count} подзадач"
        )

    subtasks_count.short_description = 'Подзадачи'


# 4. Настройка админки для SubTask
class SubTaskAdmin(admin.ModelAdmin):
    # Кастомный action для массового изменения статуса
    actions = ['mark_as_done']

    list_display = ('id', 'title', 'task_with_full_title', 'status', 'deadline', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('status', 'task', 'deadline')
    search_fields = ('title', 'description')
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

    # Кастомные методы для админки

    def task_with_full_title(self, obj):
        """
        Отображает полное название родительской задачи
        """
        return obj.task.title

    task_with_full_title.short_description = 'Задача'
    task_with_full_title.admin_order_field = 'task__title'

    # Кастомный action
    @admin.action(description='Пометить выбранные подзадачи как "Done"')
    def mark_as_done(self, request, queryset):
        """
        Action для массового изменения статуса подзадач на "Done"
        """
        # Проверяем, что выбран хотя бы один объект
        if not queryset.exists():
            self.message_user(request, "Не выбрано ни одной подзадачи.", level='warning')
            return

        # Обновляем статус у всех выбранных подзадач
        updated = queryset.update(status='done')

        # Показываем сообщение об успехе
        if updated == 1:
            message = "1 подзадача помечена как 'Done'"
        else:
            message = f"{updated} подзадачи(ей) помечены как 'Done'"

        self.message_user(request, message, level='success')

    # Переопределяем метод formfield_for_foreignkey для отображения полных названий задач
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Настройка поля ForeignKey для отображения полных названий задач
        при создании/редактировании подзадачи
        """
        if db_field.name == "task":
            # Используем строковое представление задачи (__str__ метод)
            # которое возвращает полное название
            kwargs["queryset"] = Task.objects.all().order_by('title')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Регистрируем модели с нашими настройками
admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)