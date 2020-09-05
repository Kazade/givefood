from django.conf.urls import include, url
from views import *

urlpatterns = (
    url(r'^$', index, name="index"),
    url(r'^foodbanks/$', foodbanks, name="foodbanks"),
    url(r'^foodbank/(?P<slug>[-\w]+)/$', foodbank, name="foodbank"),
    url(r'^foodbanks/search/$', foodbank_search, name="foodbank_search"),
    url(r'^needs/$', needs, name="needs"),
)