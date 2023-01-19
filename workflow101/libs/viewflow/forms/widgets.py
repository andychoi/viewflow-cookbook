# Copyright (c) 2017-2020, Mikhail Podgurskiy
# All Rights Reserved.

# This work is dual-licensed under AGPL defined in file 'LICENSE' with
# LICENSE_EXCEPTION and the Commercial license defined in file 'COMM_LICENSE',
# which is part of this source code package.

from django import forms
from django.forms import widgets


class InlineCalendar(widgets.DateInput):
    pass


class FormWidget(forms.Widget):
    template_name = 'viewflow/formfield.html'
    value_context_name = 'form'

    def format_value(self, value):
        return value


class FormSetWidget(forms.Widget):
    template_name = 'viewflow/formsetfield.html'
    value_context_name = 'formset'

    def format_value(self, value):
        return value


class AjaxModelSelect(forms.TextInput):
    """A widget for ModelChoiceField with ajax based autocomplete.

    To get AJAX results, GET requests with the additional
    `X-Requested-Content=Autocomplete` http header are performed to the same url as
    the form view.

    Expected response is json like::

        {
            suggestions: [
                { value: 'Chicago Blackhawks', data: { id: 1 } },
                { value: 'Chicago Bulls', data: { id: 2 } }
            ]
        ]

    :keyword lookups: list of field to query a model

    Example::

        class AddressForm(forms.Form):
            city = forms.ModelChoiceField(
                queryset=models.City.objects.all(),
                widget=AjaxModelSelect(loopups=['name__icontains'])
            )

    """
    def __init__(self, *args, **kwargs):
        self.lookups = kwargs.pop('lookups', None)
        if not self.lookups:
            raise ValueError('AjaxModelSelect need `lookups` to be provided')
        super().__init__(*args, **kwargs)


class AjaxMultipleModelSelect(forms.TextInput):
    """A widget for ModelMultipleChoiceField with ajax based autocomplete.

    .. seealso::
        :class: material.form.widgets.AjaxModelSelect

    """
    def __init__(self, *args, **kwargs):
        self.lookups = kwargs.pop('lookups', None)
        if not self.lookups:
            raise ValueError('AjaxMultiModelSelect need `lookups` to be provided')
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)


class TrixEditorWidget(forms.TextInput):
    """A WYSIWYG editor widget.

    .. seealso::
        https://trix-editor.org/
    """
    def __init__(self, options=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Media:
        js = [
            'viewflow/js/trix.js',
        ]
        css = {
            'all': ('viewflow/css/trix.css',)
        }


class DependentModelSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.depends_on = kwargs.pop('depends_on', None)
        self.queryset = kwargs.pop('queryset', None)
        # TODO exclute_self option for queryset

        if not self.depends_on or self.queryset is None:
            raise ValueError('DependentModelSelect need both depends_on and queryset been provided')
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['parent'] = self.depends_on
        return context
