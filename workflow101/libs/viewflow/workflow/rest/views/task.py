from django.core.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.schemas.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
from .. import filters, serializers


class TaskListSchema(AutoSchema):
    def get_tags(self, path, method):
        return [self.view.flow_class.instance.flow_label]

    def map_field(self, field):
        if field.field_name == "actions":
            return {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "readOnly": "true"},
                        "url": {"type": "string", "readOnly": "true"},
                    },
                },
            }
        return super().map_field(field)


class TaskListView(generics.ListAPIView):
    serializer_class = serializers.TaskListSerializer
    flow_class = None
    filter_backends = (DjangoFilterBackend,)
    filter_class = filters.TaskFilter
    schema = TaskListSchema()

    def check_permissions(self, request):
        super().check_permissions(request)

        if not self.flow_class.instance.has_view_permission(request.user):
            raise PermissionDenied

    def get_queryset(self):
        task_class = self.flow_class.task_class
        queryset = task_class._default_manager.filter(
            process__flow_class=self.flow_class
        )
        task_list = self.request.GET.get("task_list")
        if task_list == "INBOX":
            queryset = queryset.inbox([self.flow_class], self.request.user)
        elif task_list == "QUEUE":
            queryset = queryset.queue([self.flow_class], self.request.user)
        elif task_list == "ARCHIVE":
            queryset = queryset.archive([self.flow_class], self.request.user)
        elif task_list == "ACTIVE":
            queryset = queryset.filter_available(
                [self.flow_class], self.request.user
            ).filter(finished__isnull=True)
        return queryset
