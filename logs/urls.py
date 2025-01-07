from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_log, name="create_log"),
    path("view/", views.view_logs, name="view_logs"),
    path("commit/<int:log_id>/", views.commit_log, name="commit_log"),
]
