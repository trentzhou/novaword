from django.conf.urls import url

from learn.book_views import BookListView, BookDetailView, AjaxBookTreeView, AjaxBookListView, AjaxBookUnitsView, \
    AjaxNewBookView, AjaxEditBookView, AjaxDeleteBookView, AjaxBookAddMaintainer, AjaxBookDeleteMaintainer
from learn.unit_views import AjaxNewUnitView, AjaxBatchAddUnitView, AjaxEditUnitView, AjaxDeleteUnitView, \
    AjaxNewWordInUnitView, AjaxBatchInputWordView, AjaxDeleteWordInUnitView
from learn.views import LearningPlanView, LearningView, ReviewView, UnitDetailView, \
    AjaxAddUnitToLearningPlanView, AjaxDeleteUnitFromLearningPlanView, AjaxIsUnitInLearningPlan, \
    AjaxAddBookToLearningPlanView, AjaxUnitDataView, UnitWalkThroughView, UnitLearnView, UnitTestView, \
    AjaxSaveLearnRecordView, UnitReviewView, ErrorWordListView, AjaxErrorWordsView, AjaxAmendErrorWordsView, \
    AmendErrorWordView, StartLearnView, AjaxGetTodayUnitsView, \
    ErrorWordTextView, UnitWordsTextView, \
    AjaxChangeUnitWordMeaningView

urlpatterns = [
    url(r'^books/$', BookListView.as_view(), name="learn.books"),
    url(r'^books/(?P<book_id>\d+)/$', BookDetailView.as_view(), name="learn.book_detail"),
    url(r'^ajax-book-tree/$', AjaxBookTreeView.as_view(), name="learn.ajax_book_tree"),
    url(r'^ajax-book-list/$', AjaxBookListView.as_view(), name="learn.ajax_book_list"),
    url(r'^ajax-book-units/(?P<book_id>\d+)/$', AjaxBookUnitsView.as_view(), name="learn.ajax_book_units"),
    url(r'^ajax-new-book/$', AjaxNewBookView.as_view(), name="learn.ajax_new_book"),
    url(r'^ajax-edit-book/$', AjaxEditBookView.as_view(), name="learn.ajax_edit_book"),
    url(r'^ajax-delete-book/$', AjaxDeleteBookView.as_view(), name="learn.ajax_delete_book"),
    url(r'^ajax-book-add-maintainer', AjaxBookAddMaintainer.as_view(), name="learn.ajax_book_add_maintainer"),
    url(r'^ajax-book-delete-maintainer', AjaxBookDeleteMaintainer.as_view(), name="learn.ajax_book_delete_maintainer"),

    url(r'^ajax-new-unit/$', AjaxNewUnitView.as_view(), name="learn.ajax_new_unit"),
    url(r'^ajax-batch-new-unit/$', AjaxBatchAddUnitView.as_view(), name="learn.ajax_batch_new_unit"),
    url(r'^ajax-edit-unit/$', AjaxEditUnitView.as_view(), name="learn.ajax_edit_unit"),
    url(r'^ajax-unit-data/(?P<unit_id>\d+)/$', AjaxUnitDataView.as_view(), name="learn.ajax_unit_data"),
    url(r'^ajax-delete-unit/$', AjaxDeleteUnitView.as_view(), name="learn.ajax_delete_unit"),
    url(r'^ajax-new-word-in-unit/$', AjaxNewWordInUnitView.as_view(), name="learn.ajax_new_word_in_unit"),
    url(r'^ajax-batch-input-unit-words/$', AjaxBatchInputWordView.as_view(), name="learn.ajax_batch_input_unit_words"),
    url(r'^ajax-delete-word-in-unit/$', AjaxDeleteWordInUnitView.as_view(), name="learn.ajax_delete_word_in_unit"),
    url(r'^units/(?P<unit_id>\d+)$', UnitDetailView.as_view(), name="learn.unit_detail"),
    url(r'^units/(?P<unit_id>\d+)/text$', UnitWordsTextView.as_view(), name="learn.unit_words_text"),
    url(r'^ajax-change-word-meaning$', AjaxChangeUnitWordMeaningView.as_view(), name="learn.change_word_meaning"),

    url(r'^learning-plan/(?P<user_id>\d+)$', LearningPlanView.as_view(), name="learn.learning_plan"),
    url(r'^ajax-add-book-learning-plan/$', AjaxAddBookToLearningPlanView.as_view(), name="learn.ajax_add_book_learning_plan"),
    url(r'^ajax-add-learning-plan/$', AjaxAddUnitToLearningPlanView.as_view(), name="learn.ajax_add_learning_plan"),
    url(r'^ajax-del-learning-plan/$', AjaxDeleteUnitFromLearningPlanView.as_view(), name="learn.ajax_del_learning_plan"),
    url(r'^ajax-query-learning-plan/(?P<unit_id>\d+)/$', AjaxIsUnitInLearningPlan.as_view(), name="learn.ajax_query_learning_plan"),

    url(r'^start_learn/$', StartLearnView.as_view(), name='learn.start'),
    url(r'^ajax-today-units/$', AjaxGetTodayUnitsView.as_view(), name='learn.ajax_today_units'),
    url(r'^learning/(?P<user_id>\d+)$', LearningView.as_view(), name='learn.learning'),
    url(r'^review/$', ReviewView.as_view(), name='learn.review'),
    url(r'^unit_walkthrough/(?P<unit_id>\d+)/$', UnitWalkThroughView.as_view(), name="learn.unit_walkthrough"),
    url(r'^unit_learn/(?P<unit_id>\d+)/$', UnitLearnView.as_view(), name="learn.unit_learn"),
    url(r'^unit_test/(?P<unit_id>\d+)/$', UnitTestView.as_view(), name="learn.unit_test"),
    url(r'^unit_review/(?P<unit_id>\d+)/$', UnitReviewView.as_view(), name="learn.unit_review"),
    url(r'^ajax-save-learn-record/$', AjaxSaveLearnRecordView.as_view(), name="learn.save_record"),

    url(r'^error-words/$', ErrorWordListView.as_view(), name="learn.error_word_list"),
    url(r'^error-words-table/$', ErrorWordTextView.as_view(), name="learn.download_error_words"),
    url(r'^amend-error-words/$', AmendErrorWordView.as_view(), name="learn.amend_error_words"),
    url(r'^ajax-error-words$', AjaxErrorWordsView.as_view(), name="learn.ajax_error_words"),
    url(r'^ajax-amend-error-words', AjaxAmendErrorWordsView.as_view(), name="learn.ajax_amend_error_words"),
]
