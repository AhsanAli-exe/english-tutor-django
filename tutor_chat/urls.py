from django.urls import path
from . import views

# App name for URL namespacing
app_name = 'tutor_chat'

urlpatterns = [
    # Main chat interface
    path('', views.chat_interface, name='chat_interface'),
    # Process chat messages
    path('api/message/', views.process_message, name='process_message'),
    
    path('api/clear/', views.clear_history, name='clear_history'),
]
