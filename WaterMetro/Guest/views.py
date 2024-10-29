from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from Guest.models import * 
from WebAdmin.models import *
from User.models import *
import random
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.http import JsonResponse
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth import get_user_model

# Create your views here.

def index(request):
    feedback = Feedback.objects.all()
    feedback_count = feedback.count()

    # Filter based on `sentiment_score`
    excellent_count = feedback.filter(sentiment_score=5).count()
    very_good_count = feedback.filter(sentiment_score=4).count()
    good_count = feedback.filter(sentiment_score=3).count()
    average_count = feedback.filter(sentiment_score=2).count()
    poor_count = feedback.filter(sentiment_score=1).count()

    # Calculate average sentiment score
    avg_sentiment = feedback.aggregate(Avg('sentiment_score'))['sentiment_score__avg']

    # Calculate percentage of ratings (make sure to handle zero division)
    if feedback_count > 0:
        excellent_percent = (excellent_count / feedback_count) * 100
        very_good_percent = (very_good_count / feedback_count) * 100
        good_percent = (good_count / feedback_count) * 100
        average_percent = (average_count / feedback_count) * 100
        poor_percent = (poor_count / feedback_count) * 100
    else:
        excellent_percent = 0
        very_good_percent = 0
        good_percent = 0
        average_percent = 0
        poor_percent = 0

    if avg_sentiment is None:
        avg_rating = 0.0  # or some default value
    else:
        avg_rating = round(avg_sentiment, 1)
    
    context = {
        'avg_rating': avg_rating,
        'feedback_count': feedback_count,
        'excellent_count': excellent_count,
        'very_good_count': very_good_count,
        'good_count': good_count,
        'average_count': average_count,
        'poor_count': poor_count,
        'excellent_percent': excellent_percent,
        'very_good_percent': very_good_percent,
        'good_percent': good_percent,
        'average_percent': average_percent,
        'poor_percent': poor_percent,
    }

    return redirect('WebGuest:Index')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('Email')
        password = request.POST.get('Password')
        
        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successful')
            
            # Redirect based on user role
            if user.role == 'Admin':
                return redirect(reverse('WebAdmin:Homepage'))  # Replace with your admin dashboard URL
            elif user.role == 'stationmaster':
                return redirect('WebStationMaster:HomePage')  # Replace with your station master URL
            else:
                return redirect('WebUser:HomePage')  # Include the namespace if applicable
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'Guest/Login.html')  # Make sure the path matches your template

def forgetpassword(request):
    if request.method=="POST":
        otp=random.randint(10000, 999999)
        request.session["otp"]=otp
        request.session["femail"]=request.POST.get('Email')
        send_mail(
            'Respected Sir/Madam ',#subject
            "\rYour OTP for Reset Password is "+str(otp),#body
            settings.EMAIL_HOST_USER,
            [request.POST.get('Email')],
        )
        return redirect("WebGuest:Verification")
    else:
        return render(request,"Guest/ForgetPassword.html")

def OtpVerification(request):
    if request.method=="POST":
        otp=int(request.session["otp"])
        if int(request.POST.get('txtotp'))==otp:
            return redirect("WebGuest:Create")
    return render(request,"Guest/OTPVerification.html")

def CreateNewPass(request):
    User = get_user_model()
    if request.method=="POST":
        if request.POST.get('Npassword')==request.POST.get('Cpassword'):
            usercount=User.objects.filter(email=request.session["femail"]).count()
            if usercount>0:
                user=User.objects.get(email=request.session["femail"])
                Npassword = request.POST.get('Npassword')
                user.set_password(Npassword)
                user.save()
                messages.success(request, "Password updated successfully.")
                return redirect("WebGuest:Login")
    else:       
        return render(request,"Guest/CreateNewPassword.html")

def ajaxemail(request):
    User = get_user_model()
    usercount=User.objects.filter(user_email=request.GET.get("email")).count() 
    if usercount>0:
        return render(request,"Guest/Ajaxemail.html",{'mess':1})
    else:
         return render(request,"Guest/Ajaxemail.html")

def user_registration(request):
    if request.method == "POST":
        fname = request.POST.get("fName")
        lname = request.POST.get("LName")
        email = request.POST.get("Email")
        contact = request.POST.get("Contact")
        gender = request.POST.get("Gender")
        address = request.POST.get("Address")
        password = request.POST.get("Password")
        confirm_password = request.POST.get("re-password")
        photo = request.FILES.get("Photo")
        
        User = get_user_model()
        
        # Check if the username already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Username already exists.")
            return render(request, "Guest/UserRegistration.html")
        
        # Optionally, check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "Guest/UserRegistration.html")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "Guest/UserRegistration.html")

        # Server-side validation (additional checks)
        try:
            validate_contact(contact)
            validate_address(address)
            validate_photo(photo)

            # Check for duplicates
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return render(request, "Guest/UserRegistration.html")
            if Profile.objects.filter(user_contact=contact).exists():
                messages.error(request, "Contact number already exists.")
                return render(request, "Guest/UserRegistration.html")

            # Create the user
            user = User.objects.create_user(
                username=email,  # using email as the username
                first_name=fname,
                last_name=lname,
                email=email,
                password=password,  # password is hashed by `create_user`
                role='user'
            )
            user.save()

            # Create the associated profile
            profile = Profile.objects.create(
                user=user,
                user_contact=contact,
                user_gender=gender,
                user_address=address,
                user_photo=photo,
            )
            profile.save()

            messages.success(request, "Registration successful!")
            return redirect("WebGuest:Login")

        except ValidationError as e:
            messages.error(request, str(e))

    return render(request, "Guest/UserRegistration.html")

def validate_contact(contact):
    if not contact.isdigit() or not contact.startswith(('6', '7', '8', '9')) or len(contact) != 10:
        raise ValidationError("Invalid contact number. Contact must be a 10-digit number starting with 6, 7, 8, or 9.")

def validate_address(address):
    if not all(x.isalnum() or x.isspace() or x in ",." for x in address):
        raise ValidationError("Address can only contain letters, numbers, spaces, commas, and periods.")

def validate_photo(photo):
    if not photo.name.endswith(('.jpg', '.jpeg', '.png')):
        raise ValidationError("Photo must be in JPG or PNG format.")
    
    
# View to handle email validation and send OTP
def validate_email(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        User = get_user_model()
        
        # Check if the email already exists in the system
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already exists!'})

        # Generate OTP and send email
        otp = random.randint(100000, 999999)  # 6-digit OTP
        
        subject = "Your OTP for email verification"
        message = f"Your OTP is {otp}"
        recipient_list = [email]
        
        try:
            # Send the OTP email
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

            # Store OTP and email in the session
            request.session['otp'] = otp
            request.session['email'] = email

            return JsonResponse({'success': True, 'message': 'OTP sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# View to verify the OTP
def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        # Retrieve OTP from session
        session_otp = request.session.get('otp')
        
        if session_otp and str(entered_otp) == str(session_otp):
            # OTP is correct, perform any further actions if needed
            # Optionally clear the session
            del request.session['otp']
            del request.session['email']
            
            return JsonResponse({'success': True, 'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid OTP'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def logoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('WebGuest:Index')  # Replace 'LogoutPage' with the name of the URL pattern for your logout page