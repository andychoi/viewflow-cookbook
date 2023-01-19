# Copyright (c) 2017-2020, Mikhail Podgurskiy
# All Rights Reserved.

# This work is dual-licensed under AGPL defined in file 'LICENSE' with
# LICENSE_EXCEPTION and the Commercial license defined in file 'COMM_LICENSE',
# which is part of this source code package.

from copy import deepcopy

from django.db.models import Q
from django.forms import ModelChoiceField
from django.http import JsonResponse, QueryDict, HttpResponseBadRequest


def get_ajax_suggestions(field, query, max_results=25):
    """
    Default AJAX suggestion implementation
    """
    lookups = getattr(field.widget, "lookups")

    if not isinstance(field, ModelChoiceField) or lookups is None:
        return []

    search = Q()
    for lookup in lookups:
        search |= Q(**{lookup: query})

    return [
        {
            "value": field.label_from_instance(obj),
            "data": {"id": field.prepare_value(obj)},
        }
        for obj in field.queryset.filter(search)[:max_results]
    ]


def get_dependent_select_options(field, field_name, parent_field, parent_value):
    field = deepcopy(field)
    field.queryset = field.widget.queryset(parent_field.to_python(parent_value))

    return [
        {
            "name": name or "",
            "options": {
                key: str(value) if key == 'value' else value
                for key, value in options[0].items()
                if key not in ["template_name", "type", "wrap_label"]
            },
        }
        for name, options, _ in field.widget.optgroups(field_name, [])
    ]


class FormAjaxCompleteMixin:
    def options(self, request, *args, **kwargs):
        if "HTTP_X_REQUEST_AUTOCOMPLETE" in self.request.META:
            form = self.get_form()
            query = self.request.META.get(
                "HTTP_X_REQUEST_AUTOCOMPLETE", self.request.body
            )

            options = QueryDict(query, encoding=self.request.encoding)
            field_name = options.get("field", "")
            if field_name.startswith("formset-"):
                try:
                    _, formset_name, _, field_name = field_name.split("-")
                    formset_field = (
                        form.composite_fields.get(formset_name)
                        if hasattr(form, "composite_fields")
                        else None
                    )
                    field = (
                        formset_field.formset_class.form.declared_fields.get(field_name)
                        if formset_field
                        else None
                    )
                except ValueError:
                    pass
            else:
                field = form.fields.get(field_name)

            user_query = options.get("query")
            if field is None or user_query is None:
                return JsonResponse({"error": "Field or Query is missing"}, status=400)
            return JsonResponse(
                {"suggestions": get_ajax_suggestions(field, user_query)}
            )
        else:
            try:
                return super().options(request, *args, **kwargs)
            except AttributeError:
                return HttpResponseBadRequest()


class FormDependentSelectMixin:
    def options(self, request, *args, **kwargs):
        if "HTTP_X_REQUEST_SELECT_OPTIONS" in request.META:
            query = self.request.META.get("HTTP_X_REQUEST_SELECT_OPTIONS")
            options = QueryDict(query, encoding=self.request.encoding)
            field_name = options.get("field", "")
            parent_value = options.get("query", None)
            form = self.get_form()
            field = form.fields.get(field_name)
            if field is None:
                return HttpResponseBadRequest('Field is not provided')
            parent_field = form.fields.get(field.widget.depends_on)
            return JsonResponse(
                {"data": get_dependent_select_options(field, field_name, parent_field, parent_value)}
            )
        else:
            try:
                return super().options(request, *args, **kwargs)
            except AttributeError:
                return HttpResponseBadRequest()
