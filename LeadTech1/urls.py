from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('chat/', include('chat.urls')),  # Replace with your app name
    path('memories/', include('memories.urls')),  # Include the memories app URLs
    path('logs/', include('logs.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)