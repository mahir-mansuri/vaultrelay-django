from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('need_help/', views.need_help_view, name='need_help'),
    path('forgot_pwd/', views.show_forgot_pwd, name='forgot_pwd'),
    path('otp/', views.show_otp, name='otp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('home/', views.show_home, name='homeuser'),
    path('about/', views.show_about, name='about'),
    path('features/', views.show_feature, name='feature'),
    path('price/', views.show_price, name='price'),
    path('contact/', views.contact_view, name='contact'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('add_doc/', views.show_add_document, name='doc'),
    path('documents/', views.show_document, name='show_document'),
    path('documents/export-csv/', views.export_documents_csv, name='export_documents_csv'),
    path('documents/<int:doc_id>/view/', views.view_document, name='view_document'),
    path('documents/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
    path('continue_account/<int:user_id>/', views.continue_account, name='continue_account'),

    # Delete account: support with or without user_id
    path('delete_account/', views.verify_password, name='delete_account'),
    path('delete_account/<int:user_id>/', views.verify_password, name='delete_account_with_id'),
    path('verify_password/<int:user_id>/', views.verify_password, name='verify_password'),

    # ✅ Success page after deletion
    path('deletion_success/', views.deletion_success, name='deletion_success'),
    
    # Feedback form
    path('feedback/', views.feedback_form, name='feedback_form'),
    
    # Chatbot
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),
    path('chatbot/history/', views.get_chat_history, name='chat_history'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)