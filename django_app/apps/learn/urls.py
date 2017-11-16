from django.conf.urls import url

from learn.views import BookListView, UnitListView, LearningView, ReviewView, BookDetailView, UnitDetailView, \
    AjaxAddUnitToLearningPlanView, AjaxDeleteUnitFromLearningPlanView, AjaxIsUnitInLearningPlan, \
    AjaxAddBookToLearningPlanView, AjaxUnitDataView, UnitWalkThroughView, UnitLearnView, UnitTestView, \
    AjaxSaveLearnRecordView, UnitReviewView, ErrorWordListView, AjaxErrorWordsView, AjaxAmendErrorWordsView, \
    AmendErrorWordView, AjaxBookTreeView, AjaxBookUnitsView, AjaxBookListView

urlpatterns = [
    url(r'^books/$', BookListView.as_view(), name="learn.books"),
    url(r'^books/(?P<book_id>\d+)/$', BookDetailView.as_view(), name="learn.book_detail"),
    url(r'^ajax-book-tree/$', AjaxBookTreeView.as_view(), name="learn.ajax_book_tree"),
    url(r'^ajax-book-list/$', AjaxBookListView.as_view(), name="learn.ajax_book_list"),
    url(r'^ajax-book-units/(?P<book_id>\d+)/$', AjaxBookUnitsView.as_view(), name="learn.ajax_book_units"),
    url(r'^units/$', UnitListView.as_view(), name="learn.units"),
    url(r'^units/(?P<unit_id>\d+)$', UnitDetailView.as_view(), name="learn.unit_detail"),
    url(r'^ajax-add-book-learning-plan/$', AjaxAddBookToLearningPlanView.as_view(), name="learn.ajax_add_book_learning_plan"),
    url(r'^ajax-add-learning-plan/$', AjaxAddUnitToLearningPlanView.as_view(), name="learn.ajax_add_learning_plan"),
    url(r'^ajax-del-learning-plan/$', AjaxDeleteUnitFromLearningPlanView.as_view(), name="learn.ajax_del_learning_plan"),
    url(r'^ajax-query-learning-plan/(?P<unit_id>\d+)/$', AjaxIsUnitInLearningPlan.as_view(), name="learn.ajax_query_learning_plan"),
    url(r'^learning/$', LearningView.as_view(), name='learn.learning'),
    url(r'^review/$', ReviewView.as_view(), name='learn.review'),
    url(r'^ajax-unit-data/(?P<unit_id>\d+)/$', AjaxUnitDataView.as_view(), name="learn.ajax_unit_data"),
    url(r'^unit_walkthrough/(?P<unit_id>\d+)/$', UnitWalkThroughView.as_view(), name="learn.unit_walkthrough"),
    url(r'^unit_learn/(?P<unit_id>\d+)/$', UnitLearnView.as_view(), name="learn.unit_learn"),
    url(r'^unit_test/(?P<unit_id>\d+)/$', UnitTestView.as_view(), name="learn.unit_test"),
    url(r'^unit_review/(?P<unit_id>\d+)/$', UnitReviewView.as_view(), name="learn.unit_review"),
    url(r'^ajax-save-learn-record/$', AjaxSaveLearnRecordView.as_view(), name="learn.save_record"),
    url(r'^error-words/$', ErrorWordListView.as_view(), name="learn.error_word_list"),
    url(r'^amend-error-words/$', AmendErrorWordView.as_view(), name="learn.amend_error_words"),
    url(r'^ajax-error-words$', AjaxErrorWordsView.as_view(), name="learn.ajax_error_words"),
    url(r'^ajax-amend-error-words', AjaxAmendErrorWordsView.as_view(), name="learn.ajax_amend_error_words"),
]
