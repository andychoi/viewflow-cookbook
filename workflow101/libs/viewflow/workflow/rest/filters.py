from django.utils.translation import gettext_lazy as _

from django_filters import ChoiceFilter, DateRangeFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from viewflow.workflow.status import STATUS
from viewflow.workflow.fields import get_task_ref
from viewflow.workflow import models


DATERANGE_HELP = """
"empty" - Any date<br/>
1 - Today<br/>
2 - Past 7 days<br/>
3 - This month<br/>
4 - This year<br/>
5 - Yesterday<br/>
"""

STATUS_HELP = """
"empty" - All
NEW - Active
CANCELED - Canceled
DONE - Completed
"""


class ProcessFilter(FilterSet):
    status = ChoiceFilter(
        choices=(
            (STATUS.NEW.value, _("Active")),
            (STATUS.CANCELED.value, _("Canceled")),
            (STATUS.DONE.value, _("Completed")),
        ),
        required=False,
        help_text=STATUS_HELP,
    )
    created = DateRangeFilter(help_text=DATERANGE_HELP)
    finished = DateRangeFilter(help_text=DATERANGE_HELP)

    class Meta:
        model = models.Process
        exclude = [
            "flow_class",
            "data",
            "artifact_content_type",
            "artifact_object_id",
        ]


class TaskListFilter(ChoiceFilter):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices", None)
        if choices is None:
            choices = (
                ("INBOX", _("Inbox")),
                ("QUEUE", _("Queue")),
                ("ARCHIVE", _("Archive")),
                ("ACTIVE", _("Active")),
            )

        super(TaskListFilter, self).__init__(choices=choices, *args, **kwargs)

    def filter(self, qs, value):
        """
        Dump stub. All filter logic is in view
        """
        return qs


class TaskFilter(FilterSet):
    flow_task = ChoiceFilter(
        help_text="Flow task ref, for example: hellorest/flows.HelloRestFlow.approve"
    )
    created = DateRangeFilter(help_text=DATERANGE_HELP)
    process_id = ModelChoiceFilter(queryset=models.Process.objects.all(), help_text="")
    task_list = TaskListFilter(
        help_text="Empty or one of: INBOX, QUEUE, ARCHIVE, ACTIVE",
        required=False,
    )

    def __init__(self, data=None, queryset=None, **kwargs):
        if queryset is None:
            queryset = models.Task._default_manager.all()

        super(TaskFilter, self).__init__(data=data, queryset=queryset, **kwargs)
        self.filters["process_id"].field.queryset = models.Process.objects.filter(
            id__in=queryset.values_list("process", flat=True)
        )

        def task_name(flow_task):
            return "{}/{}".format(
                flow_task.flow_class.process_title, flow_task.name.title()
            )

        tasks = [
            (get_task_ref(flow_task), task_name(flow_task))
            for flow_task in queryset.order_by("flow_task")
            .distinct()
            .values_list("flow_task", flat=True)
        ]
        if "flow_task" in self.data and not any(
            task[0] == self.data["flow_task"] for task in tasks
        ):
            tasks += [(self.data["flow_task"], self.data["flow_task"])]

        self.filters["flow_task"].field.choices = [(None, "All")] + tasks
        self.form["flow_task"].field.choices = [(None, "All")] + tasks

    class Meta:
        fields = ["flow_task", "created"]
        model = models.Task
        exclude = [
            "data",
        ]
