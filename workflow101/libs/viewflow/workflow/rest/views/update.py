from rest_framework.response import Response
from rest_framework import mixins, generics
from .. import serializers, schemas
from .mixins import TaskAPIViewMixin


class UpdateProcessView(
    TaskAPIViewMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView
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

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_task_serializer(self.request.activation.task)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        task_serializer = self.get_task_serializer(instance=request.activation.task)
        return Response(task_serializer.data)

    def perform_update(self, serializer):
        serializer.save()
        self.request.activation.execute()
