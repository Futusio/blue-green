from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand, MigrationWriter, Migration
from django.core.management.base import BaseCommand, CommandError, no_translations
from django.db.migrations.operations import (
    CreateModel, DeleteModel, RemoveField, AddField, RenameField, RenameModel,
)
import os

from ...fields import AddFieldPatched

DESTRUCTION_MIGRATIONS = [RenameField]


class PatchedMigrationWriter(MigrationWriter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_operation(self):
        return AddFieldPatched()

    def blue_green(self, operation):
        if isinstance(operation, CreateModel):  # Clean
            return operation, None
        elif isinstance(operation, DeleteModel):  # Clean
            return None, operation
        elif isinstance(operation, RemoveField):  # Clean
            return None, operation
        elif isinstance(operation, AddField):  # Clean
            return operation, None
        elif isinstance(operation, RenameField):
            model = apps.get_app_config(self.migration.app_label).get_model(operation.model_name)
            field = list(filter(lambda x: x.name == operation.new_name, model._meta.fields))[0]
            # return operation, None
            add_operation = AddFieldPatched(
                model_name=model.__name__.lower(),
                name=operation.new_name,
                old_name=operation.old_name,
                field=field.clone(),
                preserve_default=True
            )
            drop_operation = RemoveField(
                model_name=model.__name__.lower(),
                name=operation.old_name,
            )
            return add_operation, drop_operation

    def create_blue(self, lst: list) -> Migration:
        operations = list(filter(None, lst))
        migration = Migration(self.migration.name + "_blue", self.migration.app_label)
        migration.dependencies = self.migration.dependencies
        migration.operations = operations
        migration.replaces = self.migration.replaces
        migration.run_before = self.migration.run_before
        migration.initial = self.migration.initial
        # migration.path = self.migration.path
        return migration

    def create_green(self, migration_blue: Migration, lst: list) -> Migration:
        operations = list(filter(None, lst))
        migration = Migration(self.migration.name + "_green", self.migration.app_label)
        migration.dependencies = [(migration_blue.app_label, migration_blue.name), ]
        migration.operations = operations
        # migration.path = self.migration.path
        migration.replaces = self.migration.replaces
        migration.run_before = self.migration.run_before
        migration.initial = self.migration.initial
        return migration

    def split_migrations(self):
        blue_list, green_list = list(), list()
        for operation in self.migration.operations:
            model = apps.get_app_config(self.migration.app_label).get_model(operation.model_name)
            x = 1
            # field = model._meta.get_field(operation.)
            blue, green = self.blue_green(operation)
            blue_list.append(blue)
            green_list.append(green)
        blue = self.create_blue(blue_list)
        green = self.create_green(blue, green_list)
        a, b = MigrationWriter(migration=blue), MigrationWriter(migration=green)
        return a, b


class Command(MakeMigrationsCommand):
    help = "Closes the specified poll for voting"

    TODO = \
    """
        Type of Operation:
        
        Safe: 
        - CREATE TABLE
        - ALTER table ADD COLUMN
        - 
        
        Unsafe:
        - DROP table ...
        - ALTER table ALTER/DELETE COLUMN ...
        - ALTER table ALTER NAE ...
    """



    def write_migration_files(self, changes, update_previous_migration_paths=None):
        """
        Take a changes dict and write them out as migration files.
        """
        directory_created = {}
        for app_label, app_migrations in changes.items():
            if self.verbosity >= 1:
                self.log(self.style.MIGRATE_HEADING("Migrations for '%s':" % app_label))
            for i, migration in enumerate(app_migrations):

                writer = PatchedMigrationWriter(migration, self.include_header)

                for writer in writer.split_migrations():
                    if self.verbosity >= 1:
                        # Display a relative path if it's below the current working
                        # directory, or an absolute path otherwise.
                        migration_string = self.get_relative_path(writer.path)
                        self.log("  %s\n" % self.style.MIGRATE_LABEL(migration_string))
                        for operation in migration.operations:
                            self.log("    - %s" % operation.describe())
                        if self.scriptable:
                            self.stdout.write(migration_string)
                    if not self.dry_run:
                        # Write the migrations file to the disk.
                        migrations_directory = os.path.dirname(writer.path)
                        if not directory_created.get(app_label):
                            os.makedirs(migrations_directory, exist_ok=True)
                            init_path = os.path.join(migrations_directory, "__init__.py")
                            if not os.path.isfile(init_path):
                                open(init_path, "w").close()
                            # We just do this once per app
                            directory_created[app_label] = True
                        migration_string = writer.as_string()
                        with open(writer.path, "w", encoding="utf-8") as fh:
                            fh.write(migration_string)
                            self.written_files.append(writer.path)
                        if update_previous_migration_paths:
                            prev_path = update_previous_migration_paths[app_label]
                            rel_prev_path = self.get_relative_path(prev_path)
                            if writer.needs_manual_porting:
                                migration_path = self.get_relative_path(writer.path)
                                self.log(
                                    self.style.WARNING(
                                        f"Updated migration {migration_path} requires "
                                        f"manual porting.\n"
                                        f"Previous migration {rel_prev_path} was kept and "
                                        f"must be deleted after porting functions manually."
                                    )
                                )
                            else:
                                os.remove(prev_path)
                                self.log(f"Deleted {rel_prev_path}")
                    elif self.verbosity == 3:
                        # Alternatively, makemigrations --dry-run --verbosity 3
                        # will log the migrations rather than saving the file to
                        # the disk.
                        self.log(
                            self.style.MIGRATE_HEADING(
                                "Full migrations file '%s':" % writer.filename
                            )
                        )
                        self.log(writer.as_string())
        # run_formatters(self.written_files)