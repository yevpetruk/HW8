from django.contrib import admin
from .models import Task, SubTask, Category

# Простая регистрация всех моделей
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(Category)
