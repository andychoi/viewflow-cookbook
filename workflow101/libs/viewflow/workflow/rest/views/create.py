from rest_framework import generics, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from .. import serializers, schemas
from .mixins import TaskAPIViewMixin


class CreateProcessView(
    TaskAPIViewMixin, CreateModelMixin, generics.GenericAPIView
):
    fields = None
    lookup_field = "task_pk"
    schema = schemas.ProcessViewSchema()

    def get_serializer_class(self):
        if self.serializer_class is None:
            return serializers.create_serializer(
                self.flow_class.process_class,
                serializers.ProcessSerializer,
                self.flow_task.name.title() + "Input",
            )
        return self.serializer_class

    def get_object(self):
        return self.request.activation.process

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        task_serializer = self.get_task_serializer(
            instance=self.request.activation.task
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            task_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()
        self.request.activation.execute()
