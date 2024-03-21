from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import SignupForm, LoginForm
from django.contrib.auth import get_user_model

User = get_user_model()

# SIGNUP
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            send_confirmation_email(request, user)  # Send confirmation email
            messages.success(request, 'Please check your email to confirm your account.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def send_confirmation_email(request, user):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    confirmation_link = request.build_absolute_uri(reverse('confirm_email', kwargs={'uidb64': uidb64, 'token': token}))
    subject = 'Confirm your email address'
    message = f"Please click the following link to confirm your email address: {confirmation_link}"
    send_mail(subject, message, 'enote7y@gmail.com', [user.email])


from django.contrib import messages  # Make sure to import messages
 
# LOGIN
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.email_confirmed:
                    login(request, user)
                    return redirect('home')
                else:
                    form.add_error(None, 'Please confirm your email address to log in.')
            else:
                # Pass error message to the form
                form.add_error(None, 'Invalid email or password. Please try again.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


# EMAIL CONFIRMATION
def confirm_email(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.save()
        return render(request, 'email_confirmed.html')
    else:
        return render(request, 'email_confirmation_invalid.html')

def email_confirmation(request):
    return render(request, 'confirmation_email.html')

def email_confirmed(request):
    return render(request, 'email_confirmed.html')

def email_confirmation_invalid(request):
    return render(request, 'email_confirmation_invalid.html')

# PASSWORD RESET
def send_password_reset_email(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User with this email does not exist.')
        return None

    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))
    email_subject = 'Password Reset'
    email_body = render_to_string('password_reset_email.html', {'reset_url': reset_url})
    send_mail(email_subject, email_body, 'enote7y@gmail.com', [email])


@login_required
def home(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')

        # Check if the tracking number exists in the database
        try:
            parcel = Parcel.objects.get(tracking_number=tracking_number)
            message = f"Tracking number {tracking_number} is valid."
        except Parcel.DoesNotExist:
            message = "Invalid tracking number. Please check and try again."

        # Return the response as JSON
        return JsonResponse({'message': message})
    else:
        return render(request, 'home.html')

@login_required
def parcel_details(request):
    parcels = Parcel.objects.all()
    return render(request, 'details.html', {'parcels': parcels})

def parcel_search(request):
    search_query = request.GET.get('search_query')
    parcels = Parcel.objects.filter(tracking_number__icontains=search_query)
    return render(request, 'details.html', {'parcels': parcels})


def csrf_failure_view(request, reason=""):
    return render(request, 'csrf_failure.html', {'reason': reason})

def index(request, reason=""):
    return render(request, 'index.html')


from .models import Parcel  # Import your Parcel model (assuming you have one)
def track(request):
    if request.method == 'GET':
        tracking_number = request.GET.get('tracking_number')
        try:
            parcel = Parcel.objects.get(tracking_number=tracking_number)
        except Parcel.DoesNotExist:
            parcel = None
        return render(request, 'track.html', {'parcel': parcel})



from .forms import ParcelRegistrationForm

def register_parcel(request):
    if request.method == 'POST':
        form = ParcelRegistrationForm(request.POST, user=request.user)  # Pass the user object to the form
        if form.is_valid():
            form.save()
            messages.success(request, 'Parcel registered successfully!')
            return redirect('register_parcel')  # Redirect back to the same page to show the success message
    else:
        form = ParcelRegistrationForm(user=request.user)  # Pass the user object to the form
    return render(request, 'register_parcel.html', {'form': form})


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('index')  # Assuming your index page is named 'index'


from django.shortcuts import render, redirect
from .models import Parcel

def admin_panel(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    parcels = Parcel.objects.all()
    return render(request, 'admin.html', {'parcels': parcels})

def update_parcel_status(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('parcel')
        status = request.POST.get('status')
        
        parcel = Parcel.objects.get(tracking_number=tracking_number)
        if parcel:
            # Update parcel status
            if status == 'in_transit':
                parcel.status = 'In Transit'
            elif status == 'shipping':
                parcel.status = 'Shipping'
            elif status == 'reached':
                parcel.status = 'Reached and Ready for Pick'
            
            parcel.save()
            return redirect('admin_panel')  # Redirect back to admin panel after updating status
    return redirect('admin_panel')  # Redirect back to admin panel if request method is not POST
