from django.urls import path

from . import views

app_name = "chatbot"

urlpatterns = [
    path("chatbot/", views.chatbot_page, name="chatbot_page"),
    path("api/chatbot/dataset/", views.api_chatbot_upload_dataset,
         name="api_chatbot_upload_dataset"),
    path("api/chatbot/message/", views.api_chatbot_message,
         name="api_chatbot_message"),
]
