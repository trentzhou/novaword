from django.conf.urls import url

from testings.views import TestIndexView, CreateQuizView, EditQuizView, AjaxGetQuizDataView, AjaxSaveQuizWords, \
    AjaxShareQuizView, AjaxSaveQuizInfo, AjaxDeleteQuizView, QuizStateView, QuizTakeView, AjaxSaveQuizResultView

urlpatterns = [
    url(r'^$', TestIndexView.as_view(), name="testings.index"),
    url(r'^quiz/new$', CreateQuizView.as_view(), name="testings.create_quiz"),
    url(r'^quiz/edit/(?P<quiz_id>\d+)$', EditQuizView.as_view(), name="testings.edit_quiz"),
    url(r'^quiz/ajax-get-quiz-data/(?P<quiz_id>\d+)$', AjaxGetQuizDataView.as_view(), name="testings.ajax_get_quiz_data"),
    url(r'^quiz/ajax-save-quiz-words$', AjaxSaveQuizWords.as_view(), name="testings.ajax_save_quiz_words"),
    url(r'^quiz/ajax-save-quiz-info$', AjaxSaveQuizInfo.as_view(), name="testings.ajax_save_quiz_info"),
    url(r'^quiz/ajax-share-quiz$', AjaxShareQuizView.as_view(), name="testings.ajax_share_quiz"),
    url(r'^quiz/ajax-delete-quiz$', AjaxDeleteQuizView.as_view(), name="testings.ajax_delete_quiz"),
    url(r'^quiz/state/(?P<quiz_id>\d+)$', QuizStateView.as_view(), name="testings.quiz_state"),
    url(r'^quiz/take/(?P<quiz_id>\d+)$', QuizTakeView.as_view(), name="testings.quiz_take"),
    url(r'^quiz/ajax-save-quiz-result', AjaxSaveQuizResultView.as_view(), name="testings.ajax_save_quiz_result"),

]