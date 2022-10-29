from django.contrib import admin
from django.views import generic
from django.urls import re_path, include
from material.frontend import urls as frontend_urls


urlpatterns = [
    re_path('^$', generic.RedirectView.as_view(url='/dashboard/', permanent=False)),
    re_path('^admin/', admin.site.urls),
    re_path(r'', include(frontend_urls)),
]
