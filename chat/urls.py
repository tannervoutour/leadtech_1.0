from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
    path("end-conversation/", views.end_conversation, name="end_conversation"),
    path("search-source-page/", views.search_source_page, name="search_source_page"),
    path('select-machine/', views.machine_selection_view, name='select_machine'),
]
