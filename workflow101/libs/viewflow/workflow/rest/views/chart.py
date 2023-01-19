import json

from django.core.exceptions import PermissionDenied
from rest_framework import views, renderers
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response

from viewflow.workflow import chart, Flow


PERMISSION_DENIED = """<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
  <g transform="translate(50,50)">
    <text x="0" y="0" font-size="35">
      {}
    </text>
  </g>
</svg>
"""


class SVGRenderer(renderers.BaseRenderer):
    media_type = "image/svg+xml"
    format = 'svg'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict):
            return PERMISSION_DENIED.format(data.get('detail', 'Error'))
        return chart.grid_to_svg(data)


class SVGJSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict):
            result = json.dumps(data, ensure_ascii=True)
            if isinstance(result, str):
                result = result.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
                return bytes(result.encode('utf-8'))
            return result
        data = {'svg': chart.grid_to_svg(data)}
        return super(SVGJSONRenderer, self).render(data, accepted_media_type=None, renderer_context=None)


class FlowChartSchema(AutoSchema):
    def get_tags(self, path, method):
        return [self.view.flow_class.instance.flow_label]

    def get_components(self, path, method):
        components = super().get_components(path, method)

        # response content
        content = {
            "type": "object",
            "properties": {
                "svg": {"type": "string", "readOnly": "true"},
            }
        }

        components.setdefault("Chart", content)

        return components

    def get_responses(self, path, method):
        return {
            '200': {
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Chart'}
                    },
                    'image/svg+xml': {
                    },
                },
                'description': ""
            }
        }


class FlowChartView(views.APIView):
    flow_class: Flow = None
    renderer_classes = (SVGRenderer, SVGJSONRenderer)
    schema = FlowChartSchema()

    def check_permissions(self, request):
        super().check_permissions(request)

        if not self.flow_class.instance.has_view_permission(request.user):
            raise PermissionDenied

    def get(self, request, *args, **kwargs):
        grid = chart.calc_layout_data(self.flow_class)
        return Response(grid)
