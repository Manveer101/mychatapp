# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from accounts.views import MyProfileView

# Chat views exposed directly here (no chat.urls include)
from chat.views import ReceivedMessagesView, SentMessagesView, EditMessageView, DeleteMessageView, ConversationsView, ThreadView, FileUploadView, AddReactionView, SentMessagesView


# (Optional) include if you have this view implemented
try:
    from chat.views import MarkReadView  # mark a single message as read
    HAS_MARK_READ = True
except Exception:
    HAS_MARK_READ = False

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),


    # Auth (signup/signin)
    path('api/', include('accounts.urls')),  # /api/auth/signup/ and /api/auth/signin/

    # =======================
    # CHAT ENDPOINTS (DIRECT)
    # =======================

    # Conversations list
    #   GET /api/chat/conversations/
    path('api/chat/conversations/', ConversationsView.as_view(), name='conversations'),

    # Thread with a user (list & send)
    #   GET  /api/chat/thread/<username>/?page=1
    #   POST /api/chat/thread/<username>/  {"content": "..."}
    path('api/chat/thread/<str:username>/', ThreadView.as_view(), name='thread'),

    # Received & Sent helpers (normalized under /api/chat/)
    #   GET /api/chat/received/
    path('api/chat/received/', ReceivedMessagesView.as_view(), name='received-messages'),
    #   GET /api/chat/sent/
    # path('api/chat/sent/', SentMessagesView.as_view(), name='sent-messages'),
    # path('chat/thread/<str:username>/send/', views.SendMessageView.as_view())
    path("api/chat/thread/<str:username>/send/", SentMessagesView.as_view(), name="send-message"),


    # Edit/Delete message helpers (kept under /api/chat/messages/<pk>/*)
    #   PATCH /api/chat/messages/<pk>/edit/
    path('api/chat/messages/<int:pk>/edit/', EditMessageView.as_view(), name='edit-message'),
    #   DELETE /api/chat/messages/<pk>/delete/
    path('api/chat/messages/<int:pk>/delete/', DeleteMessageView.as_view(), name='delete-message'),
    
    # File upload
    path("api/upload/", FileUploadView.as_view()),    
    # profile update 
    path('profile/', MyProfileView.as_view()),
    # reactins
    path('chat/message/<int:message_id>/react/', AddReactionView.as_view()),
]

# Optional: mark a single message as read
if HAS_MARK_READ:
    urlpatterns += [
        #   POST /api/chat/messages/<pk>/read/
        path('api/chat/messages/<int:pk>/read/', MarkReadView.as_view(), name='message-read'),
    ]

# ====== API Docs ======
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)