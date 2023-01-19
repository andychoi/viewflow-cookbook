from rest_framework.schemas.openapi import AutoSchema


class ViewflowSchemaMixin:
    def get_operation_id_base(self, path, method, action):
        operation_id = super().get_operation_id_base(path, method, action)

        components = self.view.flow_task.name.split("_")
        suffix = "".join(x.title() for x in components)

        return f"{operation_id}{suffix}"

    def get_tags(self, path, method):
        return [
            f"{self.view.flow_class.instance.flow_label}|{self.view.flow_task.name}"
        ]


class ProcessViewSchema(ViewflowSchemaMixin, AutoSchema):
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

    def get_response_serializer(self, path, method):
        return self.view.get_task_serializer()


class TaskViewSchema(ViewflowSchemaMixin, AutoSchema):
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
