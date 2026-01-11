import os
import django
from datetime import datetime, timedelta

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject8.settings')
django.setup()

from django.utils import timezone
from tasks.models import Task, SubTask, Category

print("=" * 60)
print("ВЫПОЛНЕНИЕ ORM ЗАПРОСОВ В PYTHON SHELL")
print("=" * 60)

# Часть 1: Создание записей
print("\n1. СОЗДАНИЕ ЗАПИСЕЙ:")
print("-" * 40)

# 1.1 Создаем задачу "Prepare presentation"
task_deadline = timezone.now() + timedelta(days=3)

try:
    task = Task.objects.create(
        title="Prepare presentation",
        description="Prepare materials and slides for the presentation",
        status='new',
        deadline=task_deadline
    )
    print(f"✓ Создана задача: {task.title}")
    print(f"  ID: {task.id}, Дедлайн: {task.deadline}")
except django.db.utils.IntegrityError:
    print("⚠ Задача 'Prepare presentation' уже существует (уникальное поле title)")
    task = Task.objects.get(title="Prepare presentation")

# 1.2 Создаем подзадачи для "Prepare presentation"
subtasks_data = [
    {
        'title': "Gather information",
        'description': "Find necessary information for the presentation",
        'status': 'new',
        'deadline': timezone.now() + timedelta(days=2)
    },
    {
        'title': "Create slides",
        'description': "Create presentation slides",
        'status': 'new',
        'deadline': timezone.now() + timedelta(days=1)
    }
]

for subtask_data in subtasks_data:
    try:
        subtask = SubTask.objects.create(
            title=subtask_data['title'],
            description=subtask_data['description'],
            task=task,
            status=subtask_data['status'],
            deadline=subtask_data['deadline']
        )
        print(f"✓ Создана подзадача: {subtask.title}")
        print(f"  ID: {subtask.id}, Задача: {subtask.task.title}")
    except django.db.utils.IntegrityError:
        print(f"⚠ Подзадача '{subtask_data['title']}' уже существует")

# Часть 2: Чтение записей
print("\n2. ЧТЕНИЕ ЗАПИСЕЙ:")
print("-" * 40)

# 2.1 Все задачи со статусом "New"
new_tasks = Task.objects.filter(status='new')
print(f"✓ Задачи со статусом 'New' ({new_tasks.count()} шт.):")
for t in new_tasks:
    print(f"  - {t.title} (ID: {t.id}, Дедлайн: {t.deadline})")

# 2.2 Все подзадачи со статусом "Done" и просроченным дедлайном
expired_done_subtasks = SubTask.objects.filter(
    status='done',
    deadline__lt=timezone.now()  # дедлайн меньше текущего времени
)
print(f"\n✓ Подзадачи со статусом 'Done' и просроченным дедлайном ({expired_done_subtasks.count()} шт.):")
for st in expired_done_subtasks:
    print(f"  - {st.title} (ID: {st.id}, Дедлайн: {st.deadline})")

# Часть 3: Изменение записей
print("\n3. ИЗМЕНЕНИЕ ЗАПИСЕЙ:")
print("-" * 40)

# 3.1 Изменяем статус "Prepare presentation" на "In progress"
updated = Task.objects.filter(title="Prepare presentation").update(status='in_progress')
if updated:
    print(f"✓ Статус задачи 'Prepare presentation' изменен на 'In progress'")
    print(f"  Обновлено записей: {updated}")

# 3.2 Изменяем срок выполнения для "Gather information" на два дня назад
new_deadline = timezone.now() - timedelta(days=2)
updated = SubTask.objects.filter(title="Gather information").update(deadline=new_deadline)
if updated:
    print(f"✓ Срок выполнения для 'Gather information' изменен на два дня назад")
    print(f"  Новый дедлайн: {new_deadline}")

# 3.3 Изменяем описание для "Create slides"
updated = SubTask.objects.filter(title="Create slides").update(
    description="Create and format presentation slides"
)
if updated:
    print(f"✓ Описание для 'Create slides' обновлено")
    print(f"  Новое описание: 'Create and format presentation slides'")

# Часть 4: Удаление записей
print("\n4. УДАЛЕНИЕ ЗАПИСЕЙ:")
print("-" * 40)

# 4.1 Удаляем задачу "Prepare presentation" и все ее подзадачи
task_to_delete = Task.objects.filter(title="Prepare presentation").first()
if task_to_delete:
    # Считаем подзадачи перед удалением
    subtasks_count = task_to_delete.subtasks.count()
    print(f"✓ Найдена задача для удаления: {task_to_delete.title}")
    print(f"  ID: {task_to_delete.id}, Подзадач: {subtasks_count}")

    # Удаляем (каскадное удаление автоматически удалит подзадачи)
    task_to_delete.delete()
    print(f"✓ Удалена задача 'Prepare presentation' и {subtasks_count} подзадач")
else:
    print("⚠ Задача 'Prepare presentation' не найдена")

# Итог
print("\n" + "=" * 60)
print("ИТОГОВЫЙ ОТЧЕТ:")
print("=" * 60)
print(f"Всего задач в базе: {Task.objects.count()}")
print(f"Всего подзадач в базе: {SubTask.objects.count()}")
print(f"Всего категорий в базе: {Category.objects.count()}")

# Выводим оставшиеся задачи
print("\nОставшиеся задачи:")
tasks = Task.objects.all()
for t in tasks:
    print(f"  - {t.title} (Статус: {t.get_status_display()})")