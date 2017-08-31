from django.conf.urls import url

from learn.views import BookListView, UnitListView, LearningView, ReviewView

urlpatterns = [
    url(r'^books/$', BookListView.as_view(), name="learn.books"),
    url(r'^units/$', UnitListView.as_view(), name="learn.units"),
    url(r'^learning/$', LearningView.as_view(), name='learn.learning'),
    url(r'^review/$', ReviewView.as_view(), name='learn.review'),
]