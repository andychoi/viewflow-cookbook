from django.views import generic
from django.urls import re_path, include


urlpatterns = [
    re_path('^$', generic.TemplateView.as_view(template_name='index.html')),
    re_path('^parcel/', include('demo.parcel.urls')),
    re_path('^accounts/', include('django.contrib.auth.urls')),
]
