from django.apps import AppConfig
from django.core import management
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand


# class Command(MakeMigrationsCommand):
#
#     def handle(self, *args, **options):
#         # Ваша кастомная логика
#         super().handle(*args, **options)
#
#
# management.get_commands()
# management._commands['makemigrations'] = 'your_app.custom_makemigrations'
#


class SecondaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'secondary'
