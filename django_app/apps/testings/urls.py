from django.conf.urls import url

from testings.views import TestIndexView

urlpatterns = [
    url(r'^$', TestIndexView.as_view(), name="testings.index")
]