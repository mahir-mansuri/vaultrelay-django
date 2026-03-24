from django import forms
from .models import SecureDocument, UserSignup

class SignUp(forms.Form):
    fname = forms.CharField(required=True, max_length=100)
    mname = forms.CharField(required=False, max_length=100)
    lname = forms.CharField(required=True, max_length=100)
    dob = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    user_email = forms.EmailField(max_length=30, required=True)
    trusted_email = forms.EmailField(max_length=30, required=True)
    trusted_name = forms.CharField(required=True, max_length=100)
    pass1 = forms.CharField(required=True, max_length=6, widget=forms.PasswordInput)
    pass2 = forms.CharField(required=True, max_length=6, widget=forms.PasswordInput)
    secret = forms.CharField(max_length=50, required=True)
    profile_image = forms.ImageField(required=False)

class SignIn(forms.Form):
    email = forms.EmailField(required=True, max_length=30)
    pwd = forms.CharField(required=True, max_length=6, widget=forms.PasswordInput)


class Reset(forms.Form):
    email = forms.EmailField(required=True, max_length=30)
    new_password = forms.CharField(required=True, max_length=6, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=True, max_length=6, widget=forms.PasswordInput)


class ContactMessageForm(forms.Form):
    name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True, max_length=30)
    subject = forms.CharField(required=True, max_length=200)
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 5}), max_length=1000)


class SecureDocumentForm(forms.ModelForm):
    class Meta:
        model = SecureDocument
        fields = ['document_name', 'file', 'file_type', 'is_encrypted']
        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '255'}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'file_type': forms.HiddenInput(),
            'is_encrypted': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Get file extension
            file_name = file.name
            extension = file_name.split('.')[-1].lower()
            
            # Video file extensions to block
            video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 
                              'm4v', '3gp', 'mpg', 'mpeg', 'ogv', 'ts', 'mts']
            
            if extension in video_extensions:
                raise forms.ValidationError('Videos are not allowed. You cannot add video files.')
        
        return file


class EditProfileForm(forms.Form):
    fname = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mname = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    lname = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dob = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    user_email = forms.EmailField(max_length=30, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    trusted_email = forms.EmailField(max_length=30, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    trusted_name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Password change optional
    pass1 = forms.CharField(
        required=False,
        max_length=6,
        widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'})
    )
    pass2 = forms.CharField(
        required=False,
        max_length=6,
        widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'})
    )
    secret = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.current_email = kwargs.pop('current_email', None)
        self.initial_pass = kwargs.pop('initial_pass', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('pass1')
        p2 = cleaned.get('pass2')
        # If both provided and equal to current stored pass, treat as unchanged
        if p1 and p2 and self.initial_pass is not None and p1 == p2 == self.initial_pass:
            cleaned['pass1'] = ''
            cleaned['pass2'] = ''
            return cleaned
        if p1 or p2:
            if not p1 or not p2:
                raise forms.ValidationError('Both password fields are required to change password.')
            if p1 != p2:
                raise forms.ValidationError('Passwords do not match.')
            if len(p1) != 6:
                raise forms.ValidationError('Password must be exactly 6 characters.')
        return cleaned

    def clean_user_email(self):
        email = self.cleaned_data.get('user_email')
        if email and email != self.current_email:
            if UserSignup.objects.filter(user_email=email).exists():
                raise forms.ValidationError('This email is already registered.')
        return email


class FeedbackForm(forms.Form):
    name = forms.CharField(
        required=True, 
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Your Name',
            'maxlength': '100'
        })
    )
    feedback_text = forms.CharField(
        required=True, 
        max_length=1000, 
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Share your experience with VaultRelay...',
            'rows': 5,
            'maxlength': '1000'
        })
    )
    image = forms.ImageField(
        required=False, 
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    rating = forms.ChoiceField(
        required=True,
        choices=[
            (1, '1 Star'),
            (2, '2 Stars'),
            (3, '3 Stars'),
            (4, '4 Stars'),
            (5, '5 Stars'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )