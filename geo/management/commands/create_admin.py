import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Создаёт (или обновляет) администратора из переменных окружения для деплоя на Render.'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            password = 'admin12345'
            self.stdout.write(
                self.style.WARNING(
                    'Переменная DJANGO_SUPERUSER_PASSWORD не задана. '
                    'Используется временный пароль по умолчанию: admin12345. '
                    'Смените его после входа в админку.'
                )
            )

        self.stdout.write(f'Bootstrap admin user: {username}')

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            },
        )

        if created:
            user.set_password(password)
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Администратор {username} успешно создан.'))
            return

        updated_fields = []
        if email and user.email != email:
            user.email = email
            updated_fields.append('email')

        if not user.is_staff:
            user.is_staff = True
            updated_fields.append('is_staff')

        if not user.is_superuser:
            user.is_superuser = True
            updated_fields.append('is_superuser')

        # Для предсказуемого восстановления доступа при каждом деплое.
        user.set_password(password)
        updated_fields.append('password')

        user.save(update_fields=updated_fields)
        self.stdout.write(self.style.SUCCESS(f'Администратор {username} уже существовал и был обновлён.'))
