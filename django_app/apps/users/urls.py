from django.conf.urls import url

from users.views import UserInfoView, ClassListView

urlpatterns = [
    url(r'^profile/', UserInfoView.as_view(), name="users.profile"),
    url(r'^classes/', ClassListView.as_view(), name="users.classes"),
]