from django.core.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.schemas.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
from .. import filters, serializers


class ProcessListSchema(AutoSchema):
    def get_tags(self, path, method):
        return [self.view.flow_class.instance.flow_label]


class ProcessListView(generics.ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    fields = None
    flow_class = None
    filter_class = filters.ProcessFilter
    schema = ProcessListSchema()

    def check_permissions(self, request):
        super().check_permissions(request)

        if not self.flow_class.instance.has_view_permission(request.user):
            raise PermissionDenied

    def get_serializer_class(self):
        if self.serializer_class is None:
            return serializers.create_serializer(
                self.flow_class.process_class, serializers.ProcessSerializer
            )
        return self.serializer_class

    def get_queryset(self):
        process_class = self.flow_class.process_class
        return process_class._default_manager.filter_available(
            [self.flow_class], self.request.user
        )


class ProcessDetailView(generics.RetrieveAPIView):
    fields = None
    flow_class = None
    lookup_url_kwarg = "process_pk"
    schema = ProcessListSchema()

    def check_permissions(self, request):
        super().check_permissions(request)

        if not self.flow_class.instance.has_view_permission(request.user):
            raise PermissionDenied

    def get_serializer_class(self):
        if self.serializer_class is None:
            return serializers.create_serializer(
                self.flow_class.process_class, serializers.ProcessSerializer
            )
        return self.serializer_class

    def get_queryset(self):
        process_class = self.flow_class.process_class
        return process_class._default_manager.filter_available(
            [self.flow_class], self.request.user
        )
