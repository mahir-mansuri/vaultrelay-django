from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import UserSignup, SecureDocument, ContactMessage, Feedback

@admin.register(UserSignup)
class UserSignupAdmin(admin.ModelAdmin):
    list_display = (
        'profile_image_thumb', 'fname', 'mname', 'lname',
        'dob', 'user_email', 'trusted_email', 'trusted_name', 'secret'
    )
    search_fields = ('fname', 'lname', 'user_email')
    list_filter = ('dob',)
    readonly_fields = ('profile_image_preview',)
    actions = ['export_users_csv']
    
    def export_users_csv(self, request, queryset):
        """Export selected users to CSV file"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        # Write header row
        writer.writerow([
            'First Name', 'Middle Name', 'Last Name', 'Date of Birth',
            'Email', 'Trusted Email', 'Trusted Name', 'Secret',
            'Last Login', 'Inactivity Email Count', 'Marked for Deletion'
        ])
        
        # Write data rows
        for user in queryset:
            writer.writerow([
                user.fname,
                user.mname or '',
                user.lname,
                user.dob.strftime('%Y-%m-%d') if user.dob else '',
                user.user_email,
                user.trusted_email,
                user.trusted_name,
                user.secret,
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                user.inactivity_email_count,
                'Yes' if user.is_marked_for_deletion else 'No'
            ])
        
        return response
    
    export_users_csv.short_description = "Export selected users to CSV"

    def profile_image_thumb(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="height:40px;width:40px;border-radius:50%;object-fit:cover;" />', obj.profile_image.url)
        return '-'
    profile_image_thumb.short_description = 'Photo'

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height:200px;border-radius:8px;object-fit:cover;" />', obj.profile_image.url)
        return 'No image'
    profile_image_preview.short_description = 'Preview'


@admin.register(SecureDocument)
class SecureDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_name', 'file_type', 'user_info', 'file_size', 'is_encrypted', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at', 'is_encrypted')
    search_fields = ('document_name', 'user__fname', 'user__lname', 'user__user_email')
    readonly_fields = ('uploaded_at', 'encryption_key', 'file_size')
    
    def user_info(self, obj):
        return f"{obj.user.fname} {obj.user.lname} ({obj.user.user_email})"
    user_info.short_description = 'User'
    
    def file_size(self, obj):
        return obj.get_file_size_display()
    file_size.short_description = 'File Size'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('created_at', 'is_read')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'feedback_text', 'image', 'rating')
    search_fields = ('name', 'feedback_text')