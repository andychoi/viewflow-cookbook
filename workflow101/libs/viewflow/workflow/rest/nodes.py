from django.urls import path
from viewflow import viewprop, this

from .. import nodes
from . import views, utils, mixins


class Start(mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.Start):
    """
    Task execution
    """
    @property
    def start_view(self):
        return this.resolve(self.flow_class.instance, self._start_view)

    @property
    def start_view_path(self):
        return path(f'{self.name}/', utils.wrap_start_task_view(self, self.start_view), name='start')

    """
    Task details
    """
    detail_view_class = views.DetailTaskView

    @viewprop
    def detail_view(self):
        """View for a task detail."""
        if self.detail_view_class:
            return self.detail_view_class.as_view()

    @property
    def detail_path(self):
        if self.detail_view_class:
            return path(
                f"<int:process_pk>/{self.name}/<int:task_pk>/",
                utils.wrap_rest_view(self, self.detail_view),
                name="index",
            )


class StartHandle(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.StartHandle):
    view_class = views.DetailTaskView


class End(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.End):
    view_class = views.DetailTaskView


class View(mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.View):
    @property
    def view(self):
        return this.resolve(self.flow_class.instance, self._view)

    @property
    def view_path(self):
        return path(
            f'<int:process_pk>/{self.name}/<int:task_pk>/',
            utils.wrap_view(self, self.view),
            name='index'
        )


class If(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.If):
    view_class = views.DetailTaskView


class Function(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.Function):
    view_class = views.DetailTaskView


class Handle(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.Handle):
    view_class = views.DetailTaskView


class Obsolete(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.Obsolete):
    view_class = views.DetailTaskView


class Join(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.Join):
    view_class = views.DetailTaskView


class Split(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.Split):
    view_class = views.DetailTaskView


class StartSubprocess(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.StartSubprocess):
    view_class = views.DetailTaskView


class Subprocess(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.Subprocess):
    view_class = views.DetailTaskView


class NSubprocess(mixins.RestNodeMixin, mixins.NodeCancelMixin, mixins.NodeUndoMixin, nodes.NSubprocess):
    view_class = views.DetailTaskView
