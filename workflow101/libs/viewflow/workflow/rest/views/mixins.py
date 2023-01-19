from .. import serializers


class TaskAPIViewMixin:
    _ignore_model_permissions = True
    task_serializer_class = None
    viewset = None

    def get_task_serializer_class(self):
        if self.task_serializer_class is None:
            return serializers.create_serializer(
                self.flow_class.task_class, serializers.TaskListSerializer
            )
        return self.task_serializer_class

    def get_task_serializer_context(self):
        return self.get_serializer_context()

    def get_task_serializer(self, *args, **kwargs):
        task_serializer_class = self.get_task_serializer_class()
        kwargs.setdefault("context", self.get_task_serializer_context())
        return task_serializer_class(*args, **kwargs)
