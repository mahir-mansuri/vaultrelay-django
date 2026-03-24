from django.core.management.base import BaseCommand
from vaultrelay_app.models import UserSignup, SecureDocument
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import timedelta
import tempfile
import os
import threading

class Command(BaseCommand):
    help = 'Automatically delete accounts of users who did not respond to inactivity emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days after inactivity email to wait before deletion (default: 7)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_to_wait = options['days']
        
        # Calculate cutoff date - users who received inactivity email more than X days ago
        cutoff_date = timezone.now() - timedelta(days=days_to_wait)
        
        self.stdout.write(f"Looking for accounts marked for deletion since: {cutoff_date}")
        
        # Find users marked for deletion who haven't responded
        users_to_delete = UserSignup.objects.filter(
            is_marked_for_deletion=True,
            inactivity_email_sent__lt=cutoff_date
        )
        
        self.stdout.write(f"Found {users_to_delete.count()} accounts to delete")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No accounts will be deleted"))
            for user in users_to_delete:
                self.stdout.write(f"Would delete: {user.user_email} (Last login: {user.last_login})")
            return
        
        deleted_count = 0
        failed_count = 0
        deletion_threads = []
        
        for user in users_to_delete:
            try:
                self.stdout.write(f"Processing deletion for: {user.user_email}")
                
                # Start background deletion process as non-daemon thread
                thread = threading.Thread(
                    target=self.perform_account_deletion, 
                    args=(user.id, user.user_email, user.fname),
                    daemon=False
                )
                thread.start()
                deletion_threads.append(thread)
                
                deleted_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Deletion initiated for {user.user_email}"))
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f"❌ Failed to delete {user.user_email}: {e}"))
        
        # Wait for all deletion threads to complete
        for thread in deletion_threads:
            thread.join()
            
        self.stdout.write(f"\nDeletion Summary:")
        self.stdout.write(f"Successfully initiated: {deleted_count}")
        self.stdout.write(f"Failed: {failed_count}")

    def prepare_deletion_attachments(self, user, documents):
        """Decrypt all user documents into temporary files for emailing prior to deletion."""
        temp_file_paths = []
        attached = False
        
        for doc in documents:
            try:
                # Determine file extension and MIME type
                original_name = doc.document_name
                file_ext = os.path.splitext(original_name)[1] if '.' in original_name else ''
                mime_type = doc.MIME_TYPES.get(doc.file_type, 'application/octet-stream')
                
                if not file_ext:
                    # Map common extensions with proper associations
                    file_type_map = {
                        'JPG': '.jpg',
                        'PNG': '.png',
                        'PDF': '.pdf',
                        'DOC': '.doc',
                        'DOCX': '.docx',
                        'XLS': '.xls',
                        'XLSX': '.xlsx',
                        'TXT': '.txt',
                        'OTHER': ''
                    }
                    file_ext = file_type_map.get(doc.file_type, '')
                
                if doc.is_encrypted:
                    decrypted_data = doc.decrypt_file()
                    if decrypted_data:
                        # Create temp file with proper extension
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                            temp_file.write(decrypted_data)
                            temp_file.flush()
                            # Rename the file to include the original name
                            final_path = temp_file.name
                            new_path = os.path.join(os.path.dirname(final_path), original_name)
                            if os.path.exists(new_path):
                                os.remove(new_path)  # Remove if exists
                            os.rename(final_path, new_path)
                            temp_file_paths.append(new_path)
                            attached = True
                else:
                    # Copy raw file to temp so we can delete originals safely
                    if doc.file and os.path.exists(doc.file.path):
                        temp_file_path = os.path.join(tempfile.gettempdir(), original_name)
                        with open(doc.file.path, 'rb') as src, open(temp_file_path, 'wb') as dst:
                            dst.write(src.read())
                            temp_file_paths.append(temp_file_path)
                            attached = True
            except Exception as e:
                self.stdout.write(f"Attachment preparation error for {getattr(doc, 'document_name', 'unknown')}: {e}")
                continue
                
        return temp_file_paths, attached

    def send_deletion_email(self, user_email, user_name, temp_file_paths, attached, documents):
        """Send final email with user's documents before deletion."""
        subject = 'VaultRelay Account Deleted - Your Files Attached'
        
        # Prepare file opening instructions based on attached files
        file_instructions = ""
        if attached:
            instructions_list = []
            for doc in documents:
                if doc.file_type == 'PDF':
                    instructions_list.append("""
                    <li>For PDF files:
                        <ul>
                            <li>Download Adobe Acrobat Reader DC (free) from: <a href="https://get.adobe.com/reader/">https://get.adobe.com/reader/</a></li>
                            <li>Or use Microsoft Edge browser to open PDF files</li>
                        </ul>
                    </li>""")
                elif doc.file_type in ['JPG', 'PNG']:
                    instructions_list.append("""
                    <li>For image files:
                        <ul>
                            <li>Use Windows Photos app (pre-installed on Windows)</li>
                            <li>Or download IrfanView (free) from: <a href="https://www.irfanview.com/">https://www.irfanview.com/</a></li>
                        </ul>
                    </li>""")
            
            if instructions_list:
                file_instructions = f"""
                <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <p style="font-weight: bold; color: #333;">📋 Instructions for opening attached files:</p>
                    <ul>{"".join(list(set(instructions_list)))}</ul>
                    <p style="font-size: 12px; color: #666;">
                        Note: If you don't have the proper applications installed, Windows might show limited options for opening files.
                    </p>
                </div>
                """

        message = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <h2 style="color: #333;">Hi {user_name},</h2>
            <p style="font-size: 16px;">Your VaultRelay account has been automatically deleted due to inactivity.</p>
            
            <p style="font-size: 14px; color: #555;">
              {'Your files are attached to this email. Please see the instructions below for opening different file types.' if attached else 'No files were uploaded to your account.'}
            </p>
            
            {file_instructions}
            
            <p style="font-size: 12px; color: #666;">
              If you wish to create a new account, you can sign up again at {settings.SITE_URL}/signup/
            </p>
            
            <p style="font-size: 12px; color: #666;">
              Thank you for using VaultRelay.
            </p>
          </body>
        </html>
        """
        
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
        )
        email.content_subtype = "html"
        
        # Attach files with proper MIME types
        for doc, path in zip(documents, temp_file_paths):
            try:
                filename = os.path.basename(path)
                mime_type = doc.MIME_TYPES.get(doc.file_type, 'application/octet-stream')
                with open(path, 'rb') as f:
                    content = f.read()
                    email.attach(filename, content, mime_type)
            except Exception as e:
                self.stdout.write(f"Email attach error for {filename}: {e}")
        
        try:
            email.send()
            self.stdout.write(f"Final email sent to {user_email}")
        except Exception as e:
            self.stdout.write(f"Failed to send final email to {user_email}: {e}")
        finally:
            # Clean up temp files
            for path in temp_file_paths:
                try:
                    os.remove(path)
                except Exception as e:
                    self.stdout.write(f"Temp file cleanup error: {e}")

    def perform_account_deletion(self, user_id, user_email, user_name):
        """Background task: prepare attachments, send email, delete docs and user."""
        try:
            user = UserSignup.objects.filter(pk=user_id, user_email=user_email).first()
            if not user:
                self.stdout.write(f"User {user_email} not found for deletion")
                return
                
            # Get user documents
            user_docs = list(SecureDocument.objects.filter(user=user))
            temp_paths, attached = self.prepare_deletion_attachments(user, user_docs)
            
            try:
                # Send final email with documents
                self.send_deletion_email(user_email, user_name, temp_paths, attached, user_docs)
            except Exception as e:
                self.stdout.write(f"Final email failed for {user_email}: {e}")
            finally:
                # Clean up temp files if any were created
                for path in temp_paths:
                    try:
                        os.remove(path)
                    except Exception:
                        pass

            # Delete documents and files
            docs = SecureDocument.objects.filter(user=user)
            for doc in docs:
                try:
                    if doc.file:
                        doc.file.delete(save=False)
                except Exception:
                    pass
                doc.delete()
            
            # Delete user account
            try:
                user.delete()
                self.stdout.write(f"Account {user_email} deleted successfully")
            except Exception as e:
                self.stdout.write(f"Failed to delete user {user_email}: {e}")
                    
        except Exception as e:
            self.stdout.write(f"perform_account_deletion error for {user_email}: {e}")

