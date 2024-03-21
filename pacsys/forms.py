from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


# Signup Form
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    confirmation_token = forms.CharField(widget=forms.HiddenInput(), required=False)  # Add this field

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2', 'profile_picture')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
# LOGIN
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

#USER MODEL
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')


#password reset
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email')

from .models import Parcel

from django import forms
from .models import Parcel
from datetime import datetime

from django import forms
from .models import Parcel

class ParcelRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['delivery_date'].label = 'Delivery Date (YYYY-MM-DD)'
        
        # Check if the user is admin
        if user and user.is_superuser:
            # If user is admin, include status field
            self.fields['status'] = forms.ChoiceField(choices=Parcel.STATUS_CHOICES, label='Status')

    class Meta:
        model = Parcel
        fields = ['tracking_number', 'sender_name', 'sender_email', 'sender_phone', 'sender_address',
                  'recipient_name', 'recipient_email', 'recipient_phone', 'recipient_address',
                  'delivery_date', 'delivery_time', 'description', 'value', 'weight',
                  'insurance_required', 'signature_confirmation_required']  # Exclude status field
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_date = cleaned_data.get('delivery_date')
        delivery_time = cleaned_data.get('delivery_time')

        # Ensure both delivery date and time are provided together if any
        if (delivery_date and not delivery_time) or (delivery_time and not delivery_date):
            raise forms.ValidationError("Please provide both delivery date and time.")

        # Automate delivery date if only time is provided
        if delivery_time and not delivery_date:
            # Set delivery date to today's date
            cleaned_data['delivery_date'] = datetime.now().date()

        return cleaned_data
