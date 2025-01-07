from django.urls import path
from . import views

urlpatterns = [
    path("", views.memory_list, name="memories"),
    path("verify/<int:memory_id>/", views.verify_memory, name="verify_memory"),
]
