from django.urls import path
from import_export.mixins import BaseExportMixin
from viewflow.views import Action
from viewflow.urls import ViewsetMeta
from viewflow.utils import Icon, viewprop

from .views import ExportView, ImportView


class ExportViewsetMixin(BaseExportMixin, metaclass=ViewsetMeta):
    export_view_class = ExportView

    def get_list_bulk_actions(self, request, *actions):
        export_selected_action = Action(
            name="Export selected objects",
            url=self.reverse('export'),
            icon=Icon('download', class_="material-icons mdc-list-item__graphic")
        )
        return super().get_list_bulk_actions(request, * (export_selected_action, *actions))

    def get_export_view_kwargs(self, **kwargs):
        view_kwargs = {
            'filterset_class': self.list_filterset_class,
            'filter_fields': self.list_filter_fields,
            **self.export_view_kwargs,
            **kwargs
        }
        return self.filter_kwargs(self.export_view_class, **view_kwargs)

    @viewprop
    def export_view_kwargs(self):
        return {}

    @viewprop
    def export_view(self):
        return self.export_view_class.as_view(**self.get_export_view_kwargs())

    @property
    def export_path(self):
        return path('export/', self.export_view, name='export')


class ImportViewsetMixin(metaclass=ViewsetMeta):
    import_view_class = ImportView

    def get_list_page_actions(self, request, *actions):
        add_action = Action(
            name="Import",
            url=self.reverse('import'),
            icon=Icon('backup', class_="material-icons mdc-list-item__graphic")
        )
        return super().get_list_page_actions(request, *(add_action, *actions))

    def get_import_view_kwargs(self, **kwargs):
        view_kwargs = {
            **self.import_view_kwargs,
            **kwargs
        }
        return self.filter_kwargs(self.import_view_class, **view_kwargs)

    @viewprop
    def import_view_kwargs(self):
        return {}

    @viewprop
    def import_view(self):
        return self.import_view_class.as_view(**self.get_import_view_kwargs())

    @property
    def import_path(self):
        return path('import/', self.import_view, name='import')
