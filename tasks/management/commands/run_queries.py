from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, SubTask, Category


class Command(BaseCommand):
    help = 'Выполнение ORM запросов для менеджера задач'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== ВЫПОЛНЕНИЕ ORM ЗАПРОСОВ ==='))

        # Часть 1: Создание записей
        self.stdout.write('\n1. СОЗДАНИЕ ЗАПИСЕЙ:')

        # 1.1 Создаем задачу "Prepare presentation"
        task_deadline = timezone.now() + timedelta(days=3)

        task, created = Task.objects.get_or_create(
            title="Prepare presentation",
            defaults={
                'description': "Prepare materials and slides for the presentation",
                'status': 'new',
                'deadline': task_deadline
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Создана задача: {task.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Задача "{task.title}" уже существует'))

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
            subtask, created = SubTask.objects.get_or_create(
                title=subtask_data['title'],
                task=task,
                defaults=subtask_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создана подзадача: {subtask.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Подзадача "{subtask.title}" уже существует'))

        # Часть 2: Чтение записей
        self.stdout.write('\n2. ЧТЕНИЕ ЗАПИСЕЙ:')

        # 2.1 Все задачи со статусом "New"
        new_tasks = Task.objects.filter(status='new')
        self.stdout.write(f'✓ Задачи со статусом "New" ({new_tasks.count()} шт.):')
        for t in new_tasks:
            self.stdout.write(f'  - {t.title} (дедлайн: {t.deadline})')

        # 2.2 Все подзадачи со статусом "Done" и просроченным дедлайном
        expired_done_subtasks = SubTask.objects.filter(
            status='done',
            deadline__lt=timezone.now()  # дедлайн меньше текущего времени
        )
        self.stdout.write(
            f'\n✓ Подзадачи со статусом "Done" и просроченным дедлайном ({expired_done_subtasks.count()} шт.):')
        for st in expired_done_subtasks:
            self.stdout.write(f'  - {st.title} (дедлайн: {st.deadline})')

        # Часть 3: Изменение записей
        self.stdout.write('\n3. ИЗМЕНЕНИЕ ЗАПИСЕЙ:')

        # 3.1 Изменяем статус "Prepare presentation" на "In progress"
        updated = Task.objects.filter(title="Prepare presentation").update(status='in_progress')
        if updated:
            self.stdout.write(self.style.SUCCESS('✓ Статус задачи "Prepare presentation" изменен на "In progress"'))

        # 3.2 Изменяем срок выполнения для "Gather information" на два дня назад
        new_deadline = timezone.now() - timedelta(days=2)
        updated = SubTask.objects.filter(title="Gather information").update(deadline=new_deadline)
        if updated:
            self.stdout.write(self.style.SUCCESS('✓ Срок выполнения для "Gather information" изменен на два дня назад'))

        # 3.3 Изменяем описание для "Create slides"
        updated = SubTask.objects.filter(title="Create slides").update(
            description="Create and format presentation slides"
        )
        if updated:
            self.stdout.write(self.style.SUCCESS('✓ Описание для "Create slides" обновлено'))

        # Часть 4: Удаление записей
        self.stdout.write('\n4. УДАЛЕНИЕ ЗАПИСЕЙ:')

        # 4.1 Удаляем задачу "Prepare presentation" и все ее подзадачи
        # (сначала считаем сколько будет удалено)
        task_to_delete = Task.objects.filter(title="Prepare presentation").first()
        if task_to_delete:
            subtasks_count = task_to_delete.subtasks.count()

            # Удаляем (каскадное удаление автоматически удалит подзадачи)
            task_to_delete.delete()

            self.stdout.write(self.style.SUCCESS(
                f'✓ Удалена задача "Prepare presentation" и {subtasks_count} подзадач'
            ))
        else:
            self.stdout.write(self.style.WARNING('⚠ Задача "Prepare presentation" не найдена для удаления'))

        # Итог
        self.stdout.write('\n=== ОТЧЕТ ПО ВЫПОЛНЕНИЮ ===')
        self.stdout.write(f'Всего задач: {Task.objects.count()}')
        self.stdout.write(f'Всего подзадач: {SubTask.objects.count()}')
        self.stdout.write(self.style.SUCCESS('✓ Все запросы выполнены успешно!'))