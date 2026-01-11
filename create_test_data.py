import os
import django
import sys
from datetime import timedelta

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject8.settings')

try:
    django.setup()
    print("✓ Django настроен успешно")
except Exception as e:
    print(f"✗ Ошибка настройки Django: {e}")
    sys.exit(1)

from django.utils import timezone
from tasks.models import Task, SubTask, Category


def create_test_data():
    print("=" * 60)
    print("СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ ДЛЯ ПРОВЕРКИ")
    print("=" * 60)

    # 1. Создаем категории
    print("\n1. Создаем категории...")
    categories_data = ['Работа', 'Личное', 'Учеба', 'Проект', 'Дом']

    for cat_name in categories_data:
        category, created = Category.objects.get_or_create(name=cat_name)
        if created:
            print(f"  ✓ Создана категория: {cat_name}")
        else:
            print(f"  ⓘ Категория уже существует: {cat_name}")

    # 2. Создаем задачи с разной длиной названий
    print("\n2. Создаем задачи...")

    # Задачи с очень длинными названиями (для проверки обрезки)
    long_tasks = [
        "Очень длинное название задачи которое нужно обрезать в админке чтобы не портить внешний вид",
        "Другая задача с очень длинным заголовком для тестирования работы функции Truncator в Django",
        "Короткая задача",
        "Еще одна очень длинная задача для проверки работы укороченных названий в админ панели Django",
        "Подготовка к важному совещанию с клиентом по проекту разработки нового веб-приложения",
        "Анализ требований и составление технического задания для команды разработчиков",
        "Короткая",
        "Тестирование и отладка модуля авторизации пользователей в системе",
    ]

    # Статусы для разнообразия
    statuses = ['new', 'in_progress', 'pending', 'blocked', 'done']

    work_category = Category.objects.get(name='Работа')
    personal_category = Category.objects.get(name='Личное')

    for i, title in enumerate(long_tasks):
        # Выбираем статус по порядку
        status = statuses[i % len(statuses)]

        task, created = Task.objects.get_or_create(
            title=title,
            defaults={
                'description': f'Тестовое описание для задачи "{title[:50]}..."',
                'status': status,
                'deadline': timezone.now() + timedelta(days=i + 1)  # Разные дедлайны
            }
        )

        if created:
            # Добавляем категории
            if i % 2 == 0:
                task.categories.add(work_category)
            else:
                task.categories.add(personal_category)

            # Добавляем подзадачи для некоторых задач
            if i < 5:  # Только для первых 5 задач
                for j in range(1, 4):  # По 3 подзадачи
                    SubTask.objects.create(
                        title=f"Подзадача {j} для '{title[:30]}...'",
                        description=f"Описание подзадачи {j} для задачи {task.id}",
                        task=task,
                        status='new' if j == 1 else 'in_progress',
                        deadline=timezone.now() + timedelta(days=j)
                    )
                print(f"  ✓ Создана задача с подзадачами: {title[:50]}...")
            else:
                print(f"  ✓ Создана задача: {title[:50]}...")
        else:
            print(f"  ⓘ Задача уже существует: {title[:50]}...")

    # 3. Создаем подзадачи со статусом Done и просроченным дедлайном
    print("\n3. Создаем просроченные подзадачи...")

    # Находим существующие задачи
    tasks = Task.objects.all()[:3]  # Берем первые 3 задачи

    for task in tasks:
        # Создаем просроченную подзадачу
        subtask, created = SubTask.objects.get_or_create(
            title=f"Просроченная подзадача для {task.title[:20]}...",
            task=task,
            defaults={
                'description': 'Эта подзадача просрочена для тестирования фильтрации',
                'status': 'done',
                'deadline': timezone.now() - timedelta(days=10)  # Просрочена на 10 дней
            }
        )

        if created:
            print(f"  ✓ Создана просроченная подзадача для: {task.title[:30]}...")

    # 4. Итог
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 60)
    print(f"Всего категорий: {Category.objects.count()}")
    print(f"Всего задач: {Task.objects.count()}")
    print(f"Всего подзадач: {SubTask.objects.count()}")
    print(f"Подзадач со статусом 'done': {SubTask.objects.filter(status='done').count()}")
    print(f"Подзадач с просроченным дедлайном: {SubTask.objects.filter(deadline__lt=timezone.now()).count()}")
    print("\n✓ Тестовые данные созданы успешно!")
    print("\nЗапустите сервер и проверьте:")
    print("1. python manage.py runserver")
    print("2. Перейдите на http://127.0.0.1:8000/admin/")
    print("3. Логин: admin, пароль: ваш пароль")


if __name__ == "__main__":
    create_test_data()