from django.urls import re_path, include
from viewflow.flow.viewset import FlowViewSet
from .flows import DeliveryFlow


delivery_urls = FlowViewSet(DeliveryFlow).urls

app_name = 'parcel'
urlpatterns = [
     re_path(r'^delivery/', include((delivery_urls, 'delivery')))
]
