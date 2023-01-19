from django.urls import path, include
from viewflow import viewprop
from viewflow.urls import Application, Viewset, ViewsetMeta
from . import serializers, views


class BaseFlowAPIMixin(metaclass=ViewsetMeta):
    def __init__(self, flow_class, **kwargs):
        super().__init__(**kwargs)
        self.flow_class = flow_class

    """
    Flow description
    """
    flow_serializer_class = serializers.FlowClassSerializer

    @property
    def flow_path(self):
        return path(
            "",
            views.FlowDetailView.as_view(
                flow_class=self.flow_class,
                serializer_class=self.flow_serializer_class
            ),
        )

    """
    Process list
    """
    @property
    def process_list_path(self):
        return path(
            "process/",
            views.ProcessListView.as_view(
                flow_class=self.flow_class,
            ),
            name="process_list",
        )

    """
    Process detail
    """
    @property
    def process_detail_path(self):
        return path(
            "process/<path:process_pk>/",
            views.ProcessDetailView.as_view(
                flow_class=self.flow_class,
            ),
            name="process_detail",
        )

    """
    Task list
    """
    @property
    def task_list_path(self):
        return path(
            "task/",
            views.TaskListView.as_view(
                flow_class=self.flow_class,
            ),
        )

    """
    Chart View
    """
    @property
    def chart_path(self):
        return path(
            "chart/",
            views.FlowChartView.as_view(
                flow_class=self.flow_class,
            ),
        )


class FlowRestViewset(BaseFlowAPIMixin, Viewset):
    process_serializer_class = None
    task_serializer_class = None

    """
    Inbox
    """

    """
    Queue
    """

    """
    Archive
    """

    """
    Other staff
    """

    def _get_urls(self):
        own_patterns = super()._get_urls()
        flow_patterns, _, _ = self.flow_class.instance.urls
        self.flow_class.parent = self
        self.flow_class.app_name = None

        return own_patterns + [path("task/", include(flow_patterns))]

    @viewprop
    def app_name(self):
        return self.flow_class.instance.app_name

    @viewprop
    def title(self):
        return self.flow_class.process_title

    def _get_resolver_extra(self):
        return {
            'flow_viewset': self,
            **super()._get_resolver_extra()
        }


class WorkflowRestViewset(Application):
    pass
