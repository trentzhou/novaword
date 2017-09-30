from django.conf.urls import url

from testings.views import TestIndexView, CreateQuizView, EditQuizView

urlpatterns = [
    url(r'^$', TestIndexView.as_view(), name="testings.index"),
    url(r'^quiz/new$', CreateQuizView.as_view(), name="testings.create_quiz"),
    url(r'^quiz/edit/(?P<quiz_id>\d+)$', EditQuizView.as_view(), name="testings.edit_quiz"),
]