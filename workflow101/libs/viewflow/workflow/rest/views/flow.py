from django.core.exceptions import PermissionDenied
from rest_framework import views
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from ..serializers import FlowClassSerializer


class FlowDetailSchema(AutoSchema):
    def get_operation_id(self, path, method):
        return self.view.flow_class.instance.flow_label

    def get_tags(self, path, method):
        return [self.view.flow_class.instance.flow_label]

    def get_components(self, path, method):
        components = super().get_components(path, method)

        # response content
        content = {
            "type": "object",
            "properties": {
                "flow_class": {"type": "string", "readOnly": "true"},
                "title": {
                    "type": "string",
                    "readOnly": "true",
                },
                "description": {
                    "type": "string",
                    "readOnly": "true",
                },
                "start_actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "readOnly": "true"},
                            "flow_task": {"type": "string", "readOnly": "true"},
                            "title": {"type": "string", "readOnly": "true"},
                            "description": {"type": "string", "readOnly": "true"},
                            "url": {"type": "string", "readOnly": "true"},
                        },
                    },
                },
            },
        }

        components.setdefault("Flow", content)

        return components

    def get_responses(self, path, method):
        return {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Flow"}
                    }
                },
                "description": "",
            }
        }


class FlowDetailView(views.APIView):
    _ignore_model_permissions = True
    flow_class = None
    serializer_class = FlowClassSerializer
    schema = FlowDetailSchema()

    def check_permissions(self, request):
        super().check_permissions(request)

        if not self.flow_class.instance.has_view_permission(request.user):
            raise PermissionDenied

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            context={
                "request": self.request,
                "view": self,
            }
        )
        return Response(serializer.data)
