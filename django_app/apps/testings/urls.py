from django.conf.urls import url

from testings.views import TestIndexView, CreateQuizView, EditQuizView, AjaxGetQuizDataView, AjaxSaveQuiz, \
    AjaxShareQuizView

urlpatterns = [
    url(r'^$', TestIndexView.as_view(), name="testings.index"),
    url(r'^quiz/new$', CreateQuizView.as_view(), name="testings.create_quiz"),
    url(r'^quiz/edit/(?P<quiz_id>\d+)$', EditQuizView.as_view(), name="testings.edit_quiz"),
    url(r'^quiz/ajax-get-quiz-data/(?P<quiz_id>\d+)$', AjaxGetQuizDataView.as_view(), name="testings.ajax_get_quiz_data"),
    url(r'^quiz/ajax-save-quiz$', AjaxSaveQuiz.as_view(), name="testings.ajax_save_quiz"),
    url(r'^quiz/ajax-share-quiz$', AjaxShareQuizView.as_view(), name="testings.ajax_share_quiz"),
]