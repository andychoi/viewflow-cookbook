from functools import update_wrapper

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404


def wrap_rest_view(wrapper_flow_task, origin_view):
    def get_wrapper(self, request, *args, **kwargs):
        self.flow_class = wrapper_flow_task.flow_class
        self.flow_task = wrapper_flow_task

        process_pk, task_pk = kwargs.get('process_pk'), kwargs.get('task_pk')
        if process_pk is None or task_pk is None:
            raise ImproperlyConfigured(
                'Task view URL path should contain <int:process_pk> and <int:task_pk> parameters'
            )

        task = get_object_or_404(self.flow_class.task_class, pk=task_pk)
        request.activation = self.flow_task.activation_class(task)

        if not self.flow_class.instance.has_view_permission(request.user):
            raise PermissionDenied

        return origin_get(self, request, *args, **kwargs)
    get_wrapper.viewflow_wrapped = True

    def post_wrapper(self, request, *args, **kwargs):
        self.flow_class = request.flow_class
        self.flow_task = request.flow_task

        process_pk, task_pk = kwargs.get('process_pk'), kwargs.get('task_pk')
        if process_pk is None or task_pk is None:
            raise ImproperlyConfigured(
                'Task view URL path should contain <int:process_pk> and <int:task_pk> parameters'
            )

        # TODO: permission check
        with self.flow_class.lock(process_pk), transaction.atomic():
            task = get_object_or_404(self.flow_class.task_class, pk=task_pk)
            request.activation = self.flow_task.activation_class(task)

            if not self.flow_task.can_execute(request.user, task=task):
                raise PermissionDenied

            return origin_post(self, request, *args, **kwargs)
    post_wrapper.viewflow_wrapped = True

    origin_get = getattr(origin_view.cls, 'get', None)
    origin_post = getattr(origin_view.cls, 'post', None)
    if origin_get and not getattr(origin_view.cls.get, 'viewflow_wrapped', False):
        origin_view.cls.get = get_wrapper
    if origin_post and not getattr(origin_view.cls.post, 'viewflow_wrapped', False):
        origin_view.cls.post = post_wrapper

    class Wrapper(origin_view.cls):
        flow_class = wrapper_flow_task.flow_class
        flow_task = wrapper_flow_task

    def view(request, *args, **kwargs):
        request.flow_class = wrapper_flow_task.flow_class
        request.flow_task = wrapper_flow_task
        return origin_view(request, *args, **kwargs)

    update_wrapper(view, origin_view)
    view.cls = Wrapper

    return view


def wrap_start_task_view(wrapper_flow_task, origin_view):
    origin_post = origin_view.cls.post

    def post_wrapper(self, request, *args, **kwargs):
        self.flow_class = request.flow_class
        self.flow_task = request.flow_task

        request.activation = self.flow_task.activation_class.create(self.flow_task, None, None)

        if not self.flow_task.can_execute(request.user, request.activation.task):
            raise PermissionDenied

        with transaction.atomic():
            request.activation.start(request)
            return origin_post(self, request, *args, **kwargs)
    post_wrapper.viewflow_wrapped = True

    if hasattr(origin_view.cls, 'post') and not getattr(origin_view.cls.post, 'viewflow_wrapped', False):
        origin_view.cls.post = post_wrapper

    class Wrapper(origin_view.cls):
        flow_class = wrapper_flow_task.flow_class
        flow_task = wrapper_flow_task

    def view(request, *args, **kwargs):
        request.flow_class = wrapper_flow_task.flow_class
        request.flow_task = wrapper_flow_task
        return origin_view(request, *args, **kwargs)
    update_wrapper(view, origin_view)
    view.cls = Wrapper

    return view


def wrap_view(wrapper_flow_task, origin_view):
    def get_wrapper(self, request, *args, **kwargs):
        self.flow_class = wrapper_flow_task.flow_class
        self.flow_task = wrapper_flow_task

        process_pk, task_pk = kwargs.get('process_pk'), kwargs.get('task_pk')
        if process_pk is None or task_pk is None:
            raise ImproperlyConfigured(
                'Task view URL path should contain <int:process_pk> and <int:task_pk> parameters'
            )

        task = get_object_or_404(self.flow_class.task_class, pk=task_pk)
        request.activation = self.flow_task.activation_class(task)

        # TODO permission check

        return origin_get(self, request, *args, **kwargs)
    get_wrapper.viewflow_wrapped = True

    def post_wrapper(self, request, *args, **kwargs):
        self.flow_class = request.flow_class
        self.flow_task = request.flow_task

        process_pk, task_pk = kwargs.get('process_pk'), kwargs.get('task_pk')
        if process_pk is None or task_pk is None:
            raise ImproperlyConfigured(
                'Task view URL path should contain <int:process_pk> and <int:task_pk> parameters'
            )

        # TODO: permission check
        with self.flow_class.lock(process_pk), transaction.atomic():
            task = get_object_or_404(self.flow_class.task_class, pk=task_pk)
            request.activation = self.flow_task.activation_class(task)

            if not self.flow_task.can_execute(request.user, task=task):
                raise PermissionDenied

            request.activation.start(request)
            return origin_post(self, request, *args, **kwargs)
    post_wrapper.viewflow_wrapped = True

    origin_get = getattr(origin_view.cls, 'get')
    origin_post = getattr(origin_view.cls, 'post', None)
    if origin_get and not getattr(origin_view.cls.get, 'viewflow_wrapped', False):
        origin_view.cls.get = get_wrapper
    if origin_post and not getattr(origin_view.cls.post, 'viewflow_wrapped', False):
        origin_view.cls.post = post_wrapper

    class Wrapper(origin_view.cls):
        flow_class = wrapper_flow_task.flow_class
        flow_task = wrapper_flow_task

    def view(request, *args, **kwargs):
        request.flow_class = wrapper_flow_task.flow_class
        request.flow_task = wrapper_flow_task
        return origin_view(request, *args, **kwargs)

    update_wrapper(view, origin_view)
    view.cls = Wrapper

    return view
