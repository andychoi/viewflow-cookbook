from django.urls import path
from viewflow.urls import ViewsetMeta
from viewflow import viewprop
from . import utils


class RestNodeMixin(metaclass=ViewsetMeta):
    view_class = None

    @viewprop
    def view(self):
        """View for a task detail."""
        if self.view_class:
            return self.view_class.as_view()

    @property
    def index_path(self):
        if self.view:
            return path(
                f"<int:process_pk>/{self.name}/<int:task_pk>/",
                utils.wrap_rest_view(self, self.view),
                name="index",
            )


class NodeUndoMixin(metaclass=ViewsetMeta):
    """Allow to undo a completed task."""

    undo_view_class = None

    @viewprop
    def undo_view(self):
        """View for the admin to undo a task."""
        if self.undo_view_class:
            return self.undo_view_class.as_view()

    @property
    def undo_path(self):
        if self.undo_view:
            return path(
                f"<int:process_pk>/{self.name}/<int:task_pk>/undo/",
                utils.wrap_task_view(self, self.undo_view, permission=self.can_undo),
                name="undo",
            )

    def can_undo(self, user, task):
        return self.flow_class.instance.has_manage_permission(user)


class NodeCancelMixin(metaclass=ViewsetMeta):
    """Cancel a task action."""

    cancel_view_class = None

    @viewprop
    def cancel_view(self):
        """View for the admin to cancel a task."""
        if self.cancel_view_class:
            return self.cancel_view_class.as_view()

    @property
    def cancel_path(self):
        if self.cancel_view:
            return path(
                f"<int:process_pk>/{self.name}/<int:task_pk>/cancel/",
                utils.wrap_task_view(self, self.cancel_view, permission=self.can_cancel),
                name="cancel",
            )

    def can_cancel(self, user, task):
        return self.flow_class.instance.has_manage_permission(user)
