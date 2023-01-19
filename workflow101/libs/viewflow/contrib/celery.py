# Copyright (c) 2017-2020, Mikhail Podgurskiy
# All Rights Reserved.

# This work is licensed under the Commercial license defined in file
# 'COMM_LICENSE', which is part of this source code package.
from celery.result import AsyncResult

from django.utils.timezone import now
from django.db import connection
from django.http import HttpResponseRedirect

from viewflow.workflow import Activation, STATUS
from viewflow.workflow.activation import has_manage_permission
from viewflow.workflow.nodes import AbstractJob, AbstractJobActivation
from viewflow.workflow.flow import views
from viewflow.workflow.flow.mixins import (
    NodeDetailMixin,
    NodeReviveMixin,
    NodeCancelMixin,
)
from viewflow.workflow.flow.views import mixins


class CeleryDetailTaskView(mixins.TaskSuccessUrlMixin, views.DetailTaskView):
    success_url = None
    template_name = "viewflow/workflow/celery_task_detail.html"

    def get(self, request, *args, **kwargs):
        if "_reload_attempts" in request.GET:
            if self.request.activation.task.status in [STATUS.DONE, STATUS.ERROR]:
                request.POST = request.POST.copy()
                request.POST["_continue"] = 1
                return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)


class JobActivation(AbstractJobActivation):
    @Activation.status.transition(source=STATUS.NEW, target=STATUS.SCHEDULED)
    def activate(self):
        app = self.flow_task._celery_task._get_app()
        eager = getattr(app.conf, "task_always_eager", False)

        self.task.save()

        if eager:
            self.flow_task._celery_task.apply(
                args=[self.ref()], task_id=self.task.external_task_id
            )
        else:
            apply_kwargs = {}
            if self.flow_task._eta is not None:
                apply_kwargs["eta"] = self.flow_task._eta(self.task)
            elif self.flow_task._delay is not None:
                delay = self.flow_task._delay
                if callable(delay):
                    delay = delay(self.task)
                apply_kwargs["countdown"] = delay
            else:
                apply_kwargs["countdown"] = 1

            connection.on_commit(
                lambda: self.flow_task._celery_task.apply_async(
                    args=[self.ref()],
                    task_id=self.task.external_task_id,
                    **apply_kwargs
                )
            )

    @Activation.status.transition(
        source=STATUS.SCHEDULED,
        target=STATUS.CANCELED,
        permission=has_manage_permission,
    )
    def cancel(self):
        AsyncResult(self.task.external_task_id).revoke(terminate=True)

        self.task.finished = now()
        self.task.save()


class Job(NodeDetailMixin, NodeReviveMixin, NodeCancelMixin, AbstractJob):
    """
    Run celery a task in background

    Example.

    tasks.py::

        from celery import shared_task
        from viewflow.flow import flow_job


        @shared_task
        def sample_task(activation):
            ...

    flows.py::

        from viewflow.contrib import celery

        class MyFlow(Flow):
            ...
            task = celery.Job(tasks.sample_task)
            ...._
    """

    activation_class = JobActivation

    index_view_class = views.IndexTaskView
    cancel_view_class = views.CancelTaskView
    revive_view_class = views.ReviveTaskView
    detail_view_class = CeleryDetailTaskView

    def __init__(self, celery_task, undo_func=None, *args, **kwargs):
        self._eta = None
        self._delay = None
        self._celery_task = celery_task
        self._undo_func = undo_func
        super(Job, self).__init__(*args, **kwargs)

    def Eta(self, eta_callable):
        """
        Expects callable that would get the task and return datetime for
        task execution
        """
        self._eta = eta_callable
        return self

    def Delay(self, delay):
        """
        Async task execution delay
        """
        self._delay = delay
        return self


try:
    from viewflow.workflow import rest  # noqa

    class RJob(Job):  # TODO REST API
        pass

except ImportError:
    pass
