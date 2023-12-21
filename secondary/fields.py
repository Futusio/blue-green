from django.db.migrations.operations import (
    CreateModel, DeleteModel, RemoveField, AddField, RenameField, RenameModel, AddIndex
)


class AddFieldPatched(AddField):

    def deconstruct(self):
        kwargs = {
            "model_name": self.model_name,
            "name": self.name,
            "field": self.field,
            "old_name": self.old_name,
        }
        if self.preserve_default is not True:
            kwargs["preserve_default"] = self.preserve_default
        return (self.__class__.__name__, [], kwargs)

    def __init__(self, model_name, name, field, old_name, preserve_default=False):
        self.old_name = old_name
        super().__init__(model_name=model_name, name=name, field=field, preserve_default=preserve_default)


class CreateModelPatched(CreateModel):
    def __init__(self, name, fields, old_name, options=None, bases=None, managers=None):
        self.old_name = old_name
        super().__init__(name, fields, options=options, bases=bases, managers=managers)


class AddIndexPatched(AddIndex):

    def __init__(self, model_name, index, old_name):
        self.old_name = old_name
        super().__init__(model_name=model_name, index=index)
