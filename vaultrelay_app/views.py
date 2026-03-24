from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUp, SignIn,Reset,ContactMessageForm,SecureDocumentForm, EditProfileForm, FeedbackForm
from .models import UserSignup,ContactMessage, SecureDocument, Feedback, ChatMessage
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth import logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from functools import wraps
import random
from django.conf import settings
import tempfile,threading,os,tempfile
from django.db import connection
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
import uuid
import re
import csv

def session_login_required(view_func):
    """Custom decorator for session-based authentication"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('authenticated'):
            messages.error(request, "Please login to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUp(request.POST, request.FILES)  # <-- include request.FILES here
        if form.is_valid():
            data = form.cleaned_data
            user_email = data['user_email']
            
            # Check if user already exists
            if UserSignup.objects.filter(user_email=user_email).exists():
                form.add_error('user_email', 'An account with this email already exists!')
                return render(request, 'signup.html', {
                    'form': form,
                    'error': 'An account with this already exist!! Please Login'
                })

            fname = data['fname']
            mname = data['mname']
            lname = data['lname']
            dob = data['dob']
            trusted_email = data['trusted_email']
            trusted_name = data['trusted_name']
            pass1 = data['pass1']
            pass2 = data['pass2']
            secret = data['secret']
            profile_image = request.FILES.get('profile_image')  # <-- get image from form

            if pass1 != pass2:
                form.add_error('pass2', 'Passwords do not match!')
                return render(request, 'signup.html', {'form': form})
            else:
                UserSignup.objects.create(
                    fname=fname,
                    mname=mname,
                    lname=lname,
                    dob=dob,
                    user_email=user_email,
                    trusted_email=trusted_email,
                    trusted_name=trusted_name,
                    pass1=make_password(pass1),
                    secret=secret,
                    profile_image=profile_image  # <-- save image in DB
                )
                return redirect('login')
        else:
            # Surface form errors to the template so the user sees why it didn't submit
            # Aggregate first error per field into a simple string
            errors = []
            for field, field_errors in form.errors.items():
                for err in field_errors:
                    errors.append(f"{field.replace('_',' ').title()}: {err}")
            error_text = "; ".join(errors) if errors else "Please correct the errors in the form."
            return render(request, 'signup.html', {'form': form, 'error': error_text})
    else:
        form = SignUp()
        return render(request, 'signup.html', {'form': form})



def login(request):
    if request.method == "POST":
        form = SignIn(request.POST, request.FILES)  # Added request.FILES for image
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            pwd = data['pwd']
            profile_image = request.FILES.get('profile_image')  # Get uploaded image

            # Check for admin credentials
            if email == 'vaultrelay' and pwd == 'vaultrelay12':
                request.session['admin_authenticated'] = True
                return redirect('admin_dashboard')

            user_info = UserSignup.objects.filter(user_email=email).first()
            
            if user_info:
                if check_password(pwd, user_info.pass1):
                    # Save uploaded image to user profile if provided
                    if profile_image:
                        user_info.profile_image = profile_image
                        user_info.save()

                    # ✅ Store details in session
                    request.session['pending_user'] = email
                    request.session['user_name'] = user_info.fname  # Store name in session
                    # Store profile image URL if available
                    if user_info.profile_image:
                        request.session['profile_image_url'] = user_info.profile_image.url
                    else:
                        request.session['profile_image_url'] = None
                    
                    return redirect('otp')
                else:
                    messages.error(request, "Incorrect password entered!!")
                    return render(request, 'login.html', {'form': form})
            else:
                messages.error(request, f"No account found for: {email}")
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})
    
    form = SignIn()
    return render(request, 'login.html', {'form': form})



def thankyou(request):
     return render(request, 'thankyou.html')

def need_help_view(request):
    return render(request,'need_help.html')

def show_forgot_pwd(request):
    if request.method == 'POST':
        form = Reset(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            user = UserSignup.objects.filter(user_email=email).first()
            
            if not user:
                messages.error(request, "No account found with this email")
                return render(request, 'forgot_pwd.html', {'form': form})

            # Check if the new password is the same as the old password
            if check_password(new_password, user.pass1):
                messages.error(request, "Please enter a new password different from your current password")
                return render(request, 'forgot_pwd.html', {'form': form})

            # Validate new password
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                return render(request, 'forgot_pwd.html', {'form': form})
            if len(new_password) != 6:
                messages.error(request, "Password must be exactly 6 characters")
                return render(request, 'forgot_pwd.html', {'form': form})

            # Update password in database
            user.pass1 = make_password(new_password)
            user.save()

            # Clear any reset session flags if present
            for key in ['reset_email', 'reset_pending', 'reset_otp']:
                request.session.pop(key, None)

            messages.success(request, "Password updated successfully. Please login to continue.")
            return redirect('login')
            
    else:
        form = Reset()
    return render(request, 'forgot_pwd.html', {'form': form})

def index(request):
    return render(request,'index.html')

def show_otp(request):
    if 'pending_user' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('verification_code')
        stored_otp = request.session.get('otp')
        
        if entered_otp == stored_otp:
            # Keep the user email in session for document uploads
            email = request.session['pending_user']  # Don't remove it
            request.session.pop('otp', None)
            request.session['authenticated'] = True  # Add authentication flag
            request.session['user_email'] = email  # Store email for document uploads
            return redirect('homeuser')
        else:
            messages.error(request, "Invalid OTP entered")
            return render(request, 'otp.html')
    otp = str(random.randint(100000, 999999))
    request.session['otp'] = otp
    
    # Try to send OTP; if it fails (e.g., no internet), allow proceeding to OTP page
    if not send_otp_email(request.session['pending_user'], otp):
        messages.info(request, "OTP couldn't be sent right now. Please check later or use Resend.")
    
    return render(request, 'otp.html')
    


def resend_otp(request):
    from django.http import JsonResponse
    
    if 'pending_user' not in request.session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Session expired. Please login again.'})
        return redirect('login')
    
    otp = str(random.randint(100000, 999999))
    request.session['otp'] = otp
    
    if send_otp_email(request.session['pending_user'], otp):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'New OTP sent!'})
        messages.success(request, "New OTP sent!")
        return redirect('otp')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'We couldn\'t send the OTP right now. Please try again.'})
        messages.info(request, "We couldn't send the OTP right now. Please try again.")
        return redirect('otp')

def send_otp_email(email, otp):
    # Implement your email sending logic here
    try:
        subject = 'Your VaultRelay Verification Code'
        message = f'Your OTP code is: {otp}'
        send_mail(
            subject,
            message,
            'noreply@vaultrelay.com',
            [email],
            fail_silently=False,
        )
        return True
    except Exception:
        return False

@session_login_required
def show_home(request):
    feedbacks = Feedback.objects.all().order_by('-id')[:12]  # Get latest 12 feedbacks
    return render(request, 'home.html', {'feedbacks': feedbacks})

def show_about(request):
    return render(request, 'about.html')

def show_feature(request):
    return render(request,'features.html')

def show_price(request):
    return render(request,'price.html')




def contact_view(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Check if the email is registered
            if not UserSignup.objects.filter(user_email=email).exists():
                # Show registration popup
                return render(request, 'contact.html', {
                    'form': form,  # Keep the form data
                    'show_registration_popup': True,
                    'unregistered_email': email
                })

            # Save the contact message
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            # Show success popup and clear form (no duplicate messages)
            return render(request, 'contact.html', {
                'form': ContactMessageForm(),  # Empty form
                'show_popup': True
            })
        else:
            return render(request, 'contact.html', {'form': form})
    else:
        # Always show an empty form on GET
        form = ContactMessageForm()
        return render(request, 'contact.html', {'form': form})

def admin_dashboard(request):
    """Admin dashboard view - requires admin authentication"""
    if not request.session.get('admin_authenticated'):
        messages.error(request, "Admin access required!")
        return redirect('login')
    
    # Get some basic stats for admin dashboard
    total_users = UserSignup.objects.count()
    total_documents = SecureDocument.objects.count()
    total_contacts = ContactMessage.objects.count()
    
    context = {
        'total_users': total_users,
        'total_documents': total_documents,
        'total_contacts': total_contacts,
    }
    
    return render(request, 'admin_dashboard.html', context)

def logout_view(request):
    # Check if admin is logging out
    is_admin = request.session.get('admin_authenticated')
    
    # Clear all session data
    request.session.flush()
    request.session.clear()
    
    # Also clear any Django auth session
    try:
        logout(request)
    except:
        pass
    
    messages.success(request, "You have been successfully logged out.")
    if is_admin:
        return redirect('login')
    return redirect('login') 

@session_login_required
def edit_profile(request):
    user_email = request.session.get('user_email')
    user = UserSignup.objects.filter(user_email=user_email).first()
    if not user:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')

    if request.method == 'POST':
        # For comparing unchanged password: pass current raw (not possible). We instead allow empty to keep existing.
        form = EditProfileForm(request.POST, request.FILES, current_email=user.user_email)
        if form.is_valid():
            data = form.cleaned_data
            user.fname = data['fname']
            user.mname = data['mname']
            user.lname = data['lname']
            user.dob = data['dob']
            user.trusted_email = data['trusted_email']
            user.trusted_name = data['trusted_name']
            user.secret = data['secret']

            # Email change
            new_email = data['user_email']
            if new_email != user.user_email:
                user.user_email = new_email
                request.session['user_email'] = new_email

            # Optional password change
            p1 = data.get('pass1')
            p2 = data.get('pass2')
            if p1 and p2 and p1 == p2 and len(p1) == 6:
                user.pass1 = make_password(p1)

            # Optional profile image update
            img = request.FILES.get('profile_image')
            if img:
                user.profile_image = img
                request.session['profile_image_url'] = user.profile_image.url if user.profile_image else None

            user.save()
            request.session['user_name'] = user.fname
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_profile')
        else:
            return render(request, 'edit_profile.html', {'form': form})
    else:
        # Pre-fill form including masked current password equivalent (exact 6 chars). Since you hash passwords,
        # we cannot show the real password. We'll prefill with a placeholder of 6 asterisks that user can keep
        # (treated as unchanged) or overwrite with a new 6-char password.
        initial = {
            'fname': user.fname,
            'mname': user.mname,
            'lname': user.lname,
            'dob': user.dob,
            'user_email': user.user_email,
            'trusted_email': user.trusted_email,
            'trusted_name': user.trusted_name,
            'secret': user.secret,
            'pass1': '******',
            'pass2': '******',
        }
        form = EditProfileForm(initial=initial, current_email=user.user_email, initial_pass='******')
        return render(request, 'edit_profile.html', {'form': form, 'profile_image': user.profile_image})

@session_login_required
def show_add_document(request):
    if request.method == 'POST':
        form = SecureDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the logged-in user from session
            user_email = request.session.get('user_email')  # This is the email stored after OTP verification
            if user_email:
                try:
                    # Find the user by email
                    user = UserSignup.objects.get(user_email=user_email)
                    
                    # Create the document but don't save yet
                    document = form.save(commit=False)
                    document.user = user  # Set the user
                    
                    # Auto-detect file type if not set
                    if not document.file_type or document.file_type == '':
                        file_extension = document.file.name.split('.')[-1].upper()
                        if file_extension in ['PDF', 'DOC', 'DOCX', 'JPG', 'JPEG', 'PNG']:
                            document.file_type = file_extension
                        else:
                            document.file_type = 'OTHER'
                    
                    # The model's save method will handle encryption automatically
                    document.save()  # Now save to database
                    
                    messages.success(request, f"Document '{document.document_name}' uploaded successfully!")
                    # Redirect to listing page
                    return redirect('show_document')
                except UserSignup.DoesNotExist:
                    messages.error(request, "User not found. Please login again.")
                    return redirect('login')
            else:
                messages.error(request, "Please login to upload documents.")
                return redirect('login')
        else:
            # Show specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return render(request, 'add_document.html', {'form': form})
    else:
        form = SecureDocumentForm()
        return render(request, 'add_document.html', {'form': form})

@session_login_required
def show_document(request):
    user_email = request.session.get('user_email')
    user = UserSignup.objects.filter(user_email=user_email).first()
    if not user:
        messages.error(request, "User not found. Please login again.")
        return redirect('login')

    q = request.GET.get('q', '').strip()
    ftype = request.GET.get('type', '').strip().upper()

    docs = SecureDocument.objects.filter(user=user)
    if q:
        docs = docs.filter(document_name__icontains=q)
    if ftype in ['PDF','DOC','JPG','PNG','OTHER']:
        docs = docs.filter(file_type=ftype)

    # Pagination: 8 documents per page
    paginator = Paginator(docs.order_by('-uploaded_at'), 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'show_document.html', {
        'documents': page_obj,
        'q': q,
        'ftype': ftype,
        'page_obj': page_obj,
    })

@session_login_required
def export_documents_csv(request):
    """Export user's personal document list to CSV"""
    user_email = request.session.get('user_email')
    user = UserSignup.objects.filter(user_email=user_email).first()
    if not user:
        messages.error(request, "User not found. Please login again.")
        return redirect('login')
    
    # Get all documents for the user (no pagination for export)
    docs = SecureDocument.objects.filter(user=user).order_by('-uploaded_at')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="my_documents_{user.user_email}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    # Write header row
    writer.writerow([
        'Document Name', 'File Type', 'File Size', 'Uploaded At', 'Encrypted'
    ])
    
    # Write data rows
    for doc in docs:
        writer.writerow([
            doc.document_name,
            doc.file_type,
            doc.get_file_size_display(),
            doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if doc.uploaded_at else '',
            'Yes' if doc.is_encrypted else 'No'
        ])
    
    return response

@session_login_required
def delete_document(request, doc_id: int):
    user_email = request.session.get('user_email')
    user = UserSignup.objects.filter(user_email=user_email).first()
    if not user:
        return redirect('login')

    doc = SecureDocument.objects.filter(id=doc_id, user=user).first()
    if not doc:
        messages.error(request, 'Document not found or not permitted.')
        return redirect('show_document')

    if request.method == 'POST':
        # confirmed delete
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('show_document')

    messages.info(request, 'Delete requires confirmation.')
    return redirect('show_document')

from django.http import HttpResponse, Http404

@session_login_required
def view_document(request, doc_id: int):
    user_email = request.session.get('user_email')
    user = UserSignup.objects.filter(user_email=user_email).first()
    if not user:
        return redirect('login')

    doc = SecureDocument.objects.filter(id=doc_id, user=user).first()
    if not doc:
        raise Http404('Document not found')

    # Decrypt and stream file content
    try:
        if doc.is_encrypted:
            content = doc.decrypt_file()
            if content is None:
                messages.error(request, 'Unable to open document.')
                return redirect('show_document')
        else:
            # read raw file
            with open(doc.file.path, 'rb') as f:
                content = f.read()
    except Exception:
        messages.error(request, 'Unable to open document.')
        return redirect('show_document')

    # Determine content type based on file_type
    ext = (doc.file.name.split('.')[-1] or '').lower()
    ct = 'application/octet-stream'
    if ext == 'pdf':
        ct = 'application/pdf'
    elif ext in ['doc','docx']:
        ct = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif ext in ['jpg','jpeg']:
        ct = 'image/jpeg'
    elif ext == 'png':
        ct = 'image/png'

    resp = HttpResponse(content, content_type=ct)
    # Inline display for PDFs/images; for DOC prompt download
    if ext in ['pdf', 'jpg', 'jpeg', 'png']:
        resp['Content-Disposition'] = f"inline; filename=\"{doc.document_name}\""
    else:
        resp['Content-Disposition'] = f"attachment; filename=\"{doc.document_name}\""
    return resp

def continue_account(request, user_id):
    user = get_object_or_404(UserSignup, pk=user_id)
    
    # Reset inactivity tracking fields
    user.inactivity_email_sent = None
    user.inactivity_email_count = 0
    user.is_marked_for_deletion = False
    user.last_login = timezone.now()  # Update last login time
    user.save()
    
    messages.success(request, "Your account is now active and inactivity tracking has been reset.")
    return redirect('login')











def prepare_deletion_attachments(user, documents):
    """Decrypt all user documents into temporary files for emailing prior to deletion."""
    temp_file_paths = []
    attached = False
    for doc in documents:
        try:
            if doc.is_encrypted:
                decrypted_data = doc.decrypt_file()
                if decrypted_data:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{doc.document_name}") as temp_file:
                        temp_file.write(decrypted_data)
                        temp_file.flush()
                        temp_file_paths.append(temp_file.name)
                        attached = True
            else:
                # Copy raw file to temp so we can delete originals safely
                if doc.file and os.path.exists(doc.file.path):
                    with open(doc.file.path, 'rb') as src, tempfile.NamedTemporaryFile(delete=False, suffix=f"_{doc.document_name}") as dst:
                        dst.write(src.read())
                        dst.flush()
                        temp_file_paths.append(dst.name)
                        attached = True
        except Exception as e:
            print(f"Attachment preparation error for {getattr(doc, 'document_name', 'unknown')}: {e}")
            continue
    return temp_file_paths, attached


def send_deletion_email(user_email, temp_file_paths, attached):
    email = EmailMessage(
        'Your VaultRelay Files',
        'Attached are your files before account deletion.' if attached else 'No files were uploaded to your account.',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )

    for path in temp_file_paths:
        try:
            email.attach_file(path)
        except Exception as e:
            print(f"Email attach error: {e}")

    try:
        email.send()
    finally:
        # Clean up temp files
        for path in temp_file_paths:
            try:
                os.remove(path)
            except Exception as e:
                print(f"Temp file cleanup error: {e}")





def perform_account_deletion(user_id: int, user_email: str):
    """Background task: prepare attachments, send email, delete docs and user."""
    try:
        user = UserSignup.objects.filter(pk=user_id, user_email=user_email).first()
        if not user:
            return
        user_docs = list(SecureDocument.objects.filter(user=user))
        temp_paths, attached = prepare_deletion_attachments(user, user_docs)
        try:
            send_deletion_email(user_email, temp_paths, attached)
        finally:
            # Delete documents and files regardless of email success
            docs = SecureDocument.objects.filter(user=user)
            for d in docs:
                try:
                    if d.file:
                        d.file.delete(save=False)
                except Exception:
                    pass
                d.delete()
            try:
                user.delete()
            except Exception:
                pass
    except Exception as e:
        print(f"perform_account_deletion error: {e}")


def verify_password(request, user_id=None):
    # Resolve user either from session or provided user_id (backward compatible)
    session_email = request.session.get('user_email')
    user = None
    if session_email:
        user = UserSignup.objects.filter(user_email=session_email).first()
    if not user and user_id is not None:
        user = get_object_or_404(UserSignup, pk=user_id)

    if not user:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')

    if request.method == 'POST':
        password = (request.POST.get('password') or '').strip()

        if not password:
            messages.error(request, 'Password is required.')
            if user_id is not None:
                return redirect('delete_account_with_id', user_id=user_id)
            return redirect('delete_account')

        if check_password(password, user.pass1):
            # Store success info and start background deletion job, return immediately
            request.session['deletion_user_email'] = user.user_email
            request.session['deletion_fname'] = user.fname

            try:
                threading.Thread(target=perform_account_deletion, args=(user.id, user.user_email), daemon=True).start()
            except Exception as e:
                print(f"Failed to start deletion thread: {e}")

            # Mark session as not authenticated locally
            request.session['authenticated'] = False
            return redirect('deletion_success')

        messages.error(request, 'Incorrect password.')
        if user_id is not None:
            return redirect('delete_account_with_id', user_id=user_id)
        return redirect('delete_account')

    return render(request, 'confirm_delete.html', {'user_id': user_id})


def deletion_success(request):
    user_email = request.session.pop('deletion_user_email', None)
    fname = request.session.pop('deletion_fname', 'User')

    return render(request, 'deletion_success.html', {
        'user_email': user_email,
        'fname': fname,
    })


def feedback_form(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            Feedback.objects.create(
                name=data['name'],
                feedback_text=data['feedback_text'],
                image=data.get('image'),
                rating=data['rating']
            )
            messages.success(request, "Thank you for your feedback! Your review has been submitted successfully.")
            # Check if request came from home page (inline form)
            if request.META.get('HTTP_REFERER') and 'home' in request.META.get('HTTP_REFERER', ''):
                return redirect('homeuser')
            return redirect('feedback_form')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            # Check if request came from home page (inline form)
            if request.META.get('HTTP_REFERER') and 'home' in request.META.get('HTTP_REFERER', ''):
                return redirect('homeuser')
            return render(request, 'feedback_form.html', {'form': form})
    else:
        form = FeedbackForm()
    return render(request, 'feedback_form.html', {'form': form})


# Chatbot functionality
def chatbot_view(request):
    """Main chatbot page"""
    return render(request, 'chatbot.html')


def chatbot_api(request):
    """API endpoint for chatbot messages"""
    if request.method == 'POST':
        try:
            message = request.POST.get('message', '').strip()
            session_id = request.session.get('chat_session_id')
            
            # Generate session ID if not exists
            if not session_id:
                session_id = str(uuid.uuid4())
                request.session['chat_session_id'] = session_id
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Get user info if logged in
            user = None
            user_name = "Guest"
            if request.session.get('authenticated'):
                user_email = request.session.get('user_email')
                user = UserSignup.objects.filter(user_email=user_email).first()
                if user:
                    user_name = user.fname
            
            # Save user message
            ChatMessage.objects.create(
                user=user,
                message=message,
                is_user_message=True,
                session_id=session_id
            )
            
            # Process message and generate bot response
            bot_response = process_chat_message(message, user_name)
            
            # Save bot response
            ChatMessage.objects.create(
                user=user,
                message=bot_response,
                is_user_message=False,
                session_id=session_id
            )
            
            return JsonResponse({
                'response': bot_response,
                'user_name': user_name
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def process_chat_message(message, user_name):
    """Process user message and return appropriate bot response"""
    message_lower = message.lower().strip()
    
    # Check for greeting patterns
    greeting_patterns = ['hiii', 'hi', 'hie', 'hello', 'hey', 'hiya']
    farewell_patterns = ['bye', 'byee', 'byiee', 'goodbye', 'see you', 'farewell']
    
    # Check if message matches greeting patterns
    for pattern in greeting_patterns:
        if re.search(r'\b' + re.escape(pattern) + r'\b', message_lower):
            return f"Hello {user_name}! How can I help you today?"
    
    # Check if message matches farewell patterns
    for pattern in farewell_patterns:
        if re.search(r'\b' + re.escape(pattern) + r'\b', message_lower):
            return f"Bye {user_name}! Have a great day!"
    
    # Default responses for other messages
    default_responses = [
        f"Hi {user_name}! I'm here to help you with VaultRelay. How can I assist you?",
        f"Hello {user_name}! What would you like to know about VaultRelay?",
        f"Hey {user_name}! I can help you with questions about our secure document storage service.",
        f"Hi {user_name}! Feel free to ask me anything about VaultRelay features."
    ]
    
    return random.choice(default_responses)


def get_chat_history(request):
    """Get chat history for the current session"""
    session_id = request.session.get('chat_session_id')
    if not session_id:
        return JsonResponse({'messages': []})
    
    messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
    message_list = []
    
    for msg in messages:
        message_list.append({
            'message': msg.message,
            'is_user': msg.is_user_message,
            'timestamp': msg.timestamp.strftime('%H:%M')
        })
    
    return JsonResponse({'messages': message_list})