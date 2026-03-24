from django.db import models
import os
from cryptography.fernet import Fernet
from django.conf import settings
from django.utils import timezone

class UserSignup(models.Model):
    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100)
    dob = models.DateField()
    user_email = models.EmailField(max_length=30, unique=True)
    trusted_email = models.EmailField(max_length=30)
    trusted_name = models.CharField(max_length=100)
    # Store hashed password; 128 covers Django's PBKDF2 encoded length
    pass1 = models.CharField(max_length=128)
    secret = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True) 
    last_login = models.DateTimeField(default=timezone.now)
    # Track inactivity email notifications
    inactivity_email_sent = models.DateTimeField(null=True, blank=True)
    inactivity_email_count = models.PositiveIntegerField(default=0)
    is_marked_for_deletion = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.user_email})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=30)
    subject = models.CharField(max_length=200)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"




class SecureDocument(models.Model):
    FILE_TYPES = [
        ('JPG', 'JPEG Image'),
        ('PNG', 'PNG Image'),
        ('PDF', 'PDF Document'),
        ('DOC', 'Word Document'),
        ('OTHER', 'Other File Type'),
    ]
    
    # MIME type mapping for proper file handling
    MIME_TYPES = {
        'JPG': 'image/jpeg',
        'PNG': 'image/png',
        'PDF': 'application/pdf',
        'DOC': 'application/msword',
        'OTHER': 'application/octet-stream'
    }

    user = models.ForeignKey(UserSignup, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=5, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='secure_documents/')
    is_encrypted = models.BooleanField(default=True)
    encryption_key = models.BinaryField(blank=True, null=True)  # Store encryption key

    def __str__(self):
        return f"{self.document_name} ({self.user.fname} {self.user.lname})"

    def save(self, *args, **kwargs):
        # Ensure file is saved to disk before encrypting
        is_new = self.pk is None
        should_encrypt = is_new and self.is_encrypted and bool(self.file)
        if should_encrypt and not self.encryption_key:
            self.encryption_key = Fernet.generate_key()

        # First save to persist file on disk and the encryption key
        super().save(*args, **kwargs)

        # Encrypt only after the file exists on disk
        if should_encrypt:
            self.encrypt_file()

    def encrypt_file(self):
        """Encrypt the uploaded file"""
        if not self.encryption_key or not self.file:
            return
        
        try:
            # Ensure key is bytes (BinaryField may return memoryview)
            key = self.encryption_key
            if hasattr(key, 'tobytes'):
                key = key.tobytes()
            if isinstance(key, str):
                key = key.encode('utf-8')
            # Read the file
            with open(self.file.path, 'rb') as f:
                file_data = f.read()
            
            # Encrypt the data
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(file_data)
            
            # Write encrypted data back to file
            with open(self.file.path, 'wb') as f:
                f.write(encrypted_data)

            # Ensure DB knows file is now encrypted
            super(SecureDocument, self).save(update_fields=['file'])
                
        except Exception as e:
            print(f"Encryption error: {e}")

    def decrypt_file(self):
        """Decrypt the file for download"""
        if not self.encryption_key or not self.file:
            return None
        
        try:
            key = self.encryption_key
            if hasattr(key, 'tobytes'):
                key = key.tobytes()
            if isinstance(key, str):
                key = key.encode('utf-8')
            # Read the encrypted file
            with open(self.file.path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return decrypted_data
            
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def get_file_size_display(self):
        """Get human-readable file size"""
        if self.file:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "0 B"


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    feedback_text = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='feedback_images/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)  # Optional, if you show stars

    def __str__(self):
        return f"{self.name} - {self.rating} Stars"


class ChatMessage(models.Model):
    user = models.ForeignKey(UserSignup, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(max_length=1000)
    is_user_message = models.BooleanField(default=True)  # True for user, False for bot
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True)  # For anonymous users

    def __str__(self):
        return f"{'User' if self.is_user_message else 'Bot'}: {self.message[:50]}..."

