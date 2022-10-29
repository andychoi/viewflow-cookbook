from django.urls import re_path, include
from django.contrib import admin
from django.views import generic
from material.frontend import urls as frontend_urls

urlpatterns = [
    re_path(r'^$', generic.RedirectView.as_view(
        url='/workflow/', permanent=False)),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include('demo.website')),
    re_path(r'', include(frontend_urls)),
]
