"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chat.views import ReceivedMessagesView, SentMessagesView, EditMessageView, DeleteMessageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),  # This includes /api/auth/signup/ and /api/auth/signin/
    path('api/chat/', include('chat.urls')),  # This includes /api/chat/messages/
    path('messages/received/', ReceivedMessagesView.as_view(), name='received-messages'),
    path('api/sent-messages/', SentMessagesView.as_view(), name='sent-messages'),
    path('messages/<int:pk>/edit/', EditMessageView.as_view(), name='edit-message'),
    path('messages/<int:pk>/delete/', DeleteMessageView.as_view(), name='delete-message'),
]
