from .chart import FlowChartView
from .create import CreateProcessView
from .details import DetailTaskView
from .flow import FlowDetailView
from .mixins import TaskAPIViewMixin
from .process import ProcessListView, ProcessDetailView
from .task import TaskListView
from .update import UpdateProcessView


__all__ = (
    "FlowChartView",
    "CreateProcessView",
    "DetailTaskView",
    "FlowDetailView",
    "TaskAPIViewMixin",
    "UpdateProcessView",
    "ProcessListView",
    "ProcessDetailView",
    "TaskListView",
)
