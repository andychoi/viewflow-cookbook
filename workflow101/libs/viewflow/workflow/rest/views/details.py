from rest_framework import mixins, generics
from .. import schemas
from .mixins import TaskAPIViewMixin


class DetailTaskView(
    TaskAPIViewMixin, mixins.RetrieveModelMixin, generics.GenericAPIView
):
    fields = None
    lookup_field = "task_pk"
    schema = schemas.TaskViewSchema()

    def get_object(self):
        return self.request.activation.task

    def get_serializer_class(self):
        if self.serializer_class is None:
            return self.get_task_serializer_class()
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
