from django.shortcuts import render,redirect,get_object_or_404
from User.models import *
from Guest.models import *
from StationMaster.models import *
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import JsonResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required  


# Download required resources for NLTK
nltk.download('vader_lexicon')

# Create your views here.

@never_cache
@login_required
def homepage(request):
    return render(request, 'User/Homepage.html')

@never_cache
@login_required
def myprofile(request):
    user1 = request.user
    user = Profile.objects.get(user=user1)
    return render(request, 'User/MyProfile.html', {'user': user1, 'user1': user})

@never_cache
@login_required
def editprofile(request):
    user1 = request.user
    user = Profile.objects.get(user=user1)
    if request.method == "POST":
        user1.first_name = request.POST.get("txt_name")
        user1.last_name = request.POST.get("txt_lastname")
        user1.email = request.POST.get("txt_email")
        user.user_contact = request.POST.get("txt_contact")
        user.user_address = request.POST.get("txt_address")
        user1.save()
        user.save()
        request.session['profile_updated'] = True
        return redirect('WebUser:EditProfile')
    else:
        profile_updated = request.session.pop('profile_updated', False)
        return render(request, 'User/EditProfile.html', {'user': user1, 'user1': user, 'profile_updated': profile_updated})

@never_cache
@login_required
def changepassword(request):
    user1 = request.user
    user = Profile.objects.get(user=user1)
    
    if request.method == "POST":
        currentpass = request.POST.get("txt_currentpassword")
        
        # Use check_password to verify the current password
        if user1.check_password(currentpass):  # Updated line
            newpass = request.POST.get("txt_newpassword")
            conpass = request.POST.get("txt_confirmpassword")
            
            if newpass == conpass:
                user1.set_password(newpass)  # Use set_password to hash the new password
                user1.save()
                msg = "Password changed successfully."
                return render(request, 'Guest/Login.html')
            else:
                msg = "New password and confirm password do not match."
                return render(request, 'User/ChangePassword.html', {'msg': msg, 'user': user1, 'user1': user})
        else:
            msg = "Current password is incorrect."
            return render(request, 'User/ChangePassword.html', {'msg': msg, 'user': user1, 'user1': user})
    else:
        return render(request, 'User/ChangePassword.html', {'user': user1, 'user1': user})

@never_cache
@login_required
def service_detail(request):
    active_services = tbl_services.objects.filter(status=1)
    user1 = request.user
    services_with_end_time = []
    
    # Get the current system date
    current_date = datetime.today().date()

    for service in active_services:
        start_time = service.assignboat_starttime
        duration = service.duration
        
        # Calculate the end time of the service
        if duration:
            end_time = (datetime.combine(datetime.today(), start_time) + duration).time()
        else:
            end_time = start_time  # If no duration is specified, assume end time is the same as start time
        
        # Get the total booking count (adults + children) for the specific service on the current date
        total_bookings = tbl_ticketbooking.objects.filter(
            service=service, 
            date=current_date
        ).aggregate(total_adults=Sum('adults_count'), total_children=Sum('childrens_count'))
        
        total_adults = total_bookings['total_adults'] or 0
        total_children = total_bookings['total_children'] or 0
        total_booking_count = total_adults + total_children
        
        # Subtract the total booking count from the boat's available capacity
        available_seats = service.assignboat_boat.boat_capacity - total_booking_count

        services_with_end_time.append({
            'service': service,
            'end_time': end_time,
            'available_seats': available_seats
        })

    context = {
        'services_with_end_time': services_with_end_time,
        'user': user1
    }
    return render(request, 'User/service_detail.html', context)

@never_cache
@login_required
def ticketbooking(request):
    user1 = request.user
    if request.method == "POST":
        service_id = request.POST.get("service_id")
        service = get_object_or_404(tbl_services, id=service_id)
        amount=request.POST.get("txt_amount")
        # Validate adult count
        adults_count = request.POST.get("txt_number_adults")
        if not adults_count.isdigit() or not (0 <= int(adults_count) <= 99):
            return JsonResponse({'success': False, 'error': 'Invalid adult count. Please enter a number between 0 and 99.'})

        if isinstance(amount, str):
            amount = float(amount)
            booking = tbl_ticketbooking.objects.create(
            date=request.POST.get("txt_date"),
            adults_count=request.POST.get("txt_number_adults"),
            childrens_count=request.POST.get("txt_number_children"),
            book_amount=request.POST.get("txt_amount"), 
            service=service,
            user=user1
        )
         # Generate order id and create Razorpay order
        order_id = 'ORD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create(dict(amount=amount*100, currency='INR', receipt=order_id, payment_capture='1'))

        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'order_id': order['id'],
            'amount': amount
        })
    else:
        service_id = request.GET.get("service_id")
        service = get_object_or_404(tbl_services, id=service_id)
        return render(request, 'User/TicketBooking.html', {'user': user1, 'service': service})

def ajaxrate(request):
    num_adults = request.GET.get("adults")
    num_children = request.GET.get("children")
    service_id = request.GET.get("service_id")
    
    if num_adults.isdigit() and num_children.isdigit():
        # Get the selected service
        service = tbl_services.objects.get(id=service_id)
        service_rate = service.rate  # Assuming `rate` is a field in `tbl_services`
        
        total_amount = (int(num_adults) + int(num_children)) * service_rate
        return JsonResponse({"rate": total_amount})
    else:
        return JsonResponse({"rate": 0})

def payment_section(request):
    booking_id = request.GET.get('booking_id')
    
    try:
        booking = tbl_ticketbooking.objects.get(pk=booking_id)
        amount = booking.book_amount
        
        # Ensure amount is numeric
        if isinstance(amount, str):
            amount = float(amount)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({'amount': int(amount * 100), 'currency': 'INR', 'payment_capture': '1'})

        context = {
            'amount': amount,
            'order_id': payment['id'],
            'booking_id': booking_id,
        }
        return render(request, 'User/payment.html', context)

    except tbl_ticketbooking.DoesNotExist:
        return HttpResponseBadRequest("Booking not found.")
    except Exception as e:
        return HttpResponseBadRequest(f"An unexpected error occurred: {str(e)}")

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        try:
            # Retrieve POST data
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            booking_id = request.POST.get('booking_id')  # Retrieve the booking ID

            # Initialize Razorpay client with your credentials
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify the payment signature to ensure the payment is valid
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({'success': False, 'error': 'Payment verification failed'})

            # Fetch the booking record and update it with the payment details
            booking = tbl_ticketbooking.objects.get(pk=booking_id)
            booking.payment_id = payment_id
            booking.payment = True  # Mark payment as completed
            booking.save()

            # Respond with success
            return JsonResponse({'success': True})

        except tbl_ticketbooking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@never_cache
@login_required
def viewticketbooking(request):
    user1 = request.user
    bookings = tbl_ticketbooking.objects.filter(user=user1)
    
    for booking in bookings:
        start_time = booking.service.assignboat_starttime
        duration = booking.service.duration

        if start_time and duration:
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = start_datetime + duration
            booking.service_end_time = end_datetime.time()
        else:
            booking.service_end_time = "N/A"

    for booking in bookings:
        if booking.refund_amount:
            booking.refund_amount_display = booking.refund_amount / 100
    
    return render(request, "User/ViewTicketBooking.html", {"booking": bookings, 'user': user1})

@never_cache
@login_required
def cancel_booking(request):
    booking_id = request.GET.get('booking_id')
    booking = get_object_or_404(tbl_ticketbooking, id=booking_id)

    if booking.payment:
        booking.payment = 2  # Set status to 'Canceled'
        booking.save()
        return redirect('WebUser:ViewTicketBooking')
    else:
        booking.delete()
        messages.success(request, "Booking has been successfully canceled.")

    return redirect('WebUser:ViewTicketBooking')
    
def cancel_event(request):
    booking_id = request.GET.get('booking_id')
    booking = get_object_or_404(tbl_eventbooking, id=booking_id)

    if booking.status:
        messages.error(request, "Cannot cancel a booking with completed payment.")
    else:
        booking.delete()
        messages.success(request, "Booking has been successfully canceled.")

    return redirect('WebUser:vieweventbooking')

def analyze_sentiment(feedback_text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(feedback_text)
    return sentiment['compound']  # Return the compound sentiment score

# Feedback submission view
@never_cache
@login_required
def feedback_view(request):
    if request.method == "POST":
        title = request.POST.get('txt_title')
        description = request.POST.get('txt_description')

        # Analyze the sentiment of the feedback
        sentiment_score = analyze_sentiment(description)
        
        # Save feedback with sentiment score
        feedback = Feedback.objects.create(
            user=request.user,
            title=title,
            description=description,
            sentiment_score=sentiment_score
        )
        feedback.save()

        return render(request, 'User/feedback.html', {'message': 'Feedback submitted successfully!'})

    feedback_list = Feedback.objects.filter(user=request.user)
    return render(request, 'User/feedback.html', {'feedback_list': feedback_list})

@never_cache
@login_required
def eventlist(request):
    event=tbl_eventtype.objects.all()
    return render(request,'User/EventList.html',{'event':event})

@never_cache
@login_required
def eventbooking(request, did):
    if request.method == 'POST':
        # Extract data from the form
        event_date = request.POST.get('txt_date')
        startpoint_id = request.POST.get('startpoint')
        endpoint_id = request.POST.get('endpoint')
        starttime = request.POST.get('starttime')
        duration_str = request.POST.get('duration')  # Get the duration as a string
        adult_count = request.POST.get('txt_number_adults')
        deck = request.POST.get('deckType')
        children_count = request.POST.get('txt_number_children')

        # Validate adult count
        adults_count = request.POST.get("txt_number_adults")
        if not adults_count.isdigit() or not (0 <= int(adults_count) <= 999):
            return JsonResponse({'success': False, 'error': 'Invalid adult count. Please enter a number between 0 and 999.'})

        
        # Parse the duration string into hours and minutes (and seconds if present)
        try:
            time_parts = list(map(int, duration_str.split(':')))
            if len(time_parts) == 2:
                hours, minutes = time_parts
                seconds = 0
            elif len(time_parts) == 3:
                hours, minutes, seconds = time_parts
            else:
                raise ValueError("Invalid duration format")
        except ValueError:
            return JsonResponse({"error": "Invalid duration format"}, status=400)

        # Convert to a timedelta object
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # Get event details
        event = tbl_eventtype.objects.get(id=did)
        user = request.user  # Assuming the user is logged in

        # Create a new booking entry with payment_id as None
        booking = tbl_eventbooking.objects.create(
            event_date=event_date,
            event_startpoint_id=startpoint_id,
            event_endpoint_id=endpoint_id,
            event_starttime=starttime,
            duration=duration,
            adult_count=adult_count,
            children_count=children_count,
            boat_deck = deck,
            event_type=event,
            user=user,
            payment_id=None  # Set payment_id to None initially
        )
        
        # Return booking number and success status
        return JsonResponse({"success": True, "booking_id": booking.id})

    # Render the booking page
    event = tbl_eventtype.objects.get(id=did)
    places = tbl_place.objects.filter(status=1)
    return render(request, 'User/EventBooking.html', {'Event': event, 'places': places})

# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment_process(request):
    # Handle both GET and POST to retrieve booking_id
    booking_id = request.GET.get('booking_id') if request.method == 'GET' else request.POST.get('booking_id')

    if not booking_id:
        return HttpResponseBadRequest("Booking ID is required")

    try:
        data = tbl_eventbooking.objects.get(id=booking_id)
    except tbl_eventbooking.DoesNotExist:
        return HttpResponseBadRequest("Booking does not exist")

    event_type_rate = data.event_type.event_rate

    # Ensure event_type_rate is numeric and calculate total_amount
    try:
        event_type_rate = float(event_type_rate)
        total_amount = int(event_type_rate * 100)  # Convert to paise
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid rate value")

    # Check if total_amount exceeds Razorpay's limit (100000000 paise)
    if total_amount > 100000000:
        return HttpResponseBadRequest("Amount exceeds the maximum allowed limit")

    if request.method == "POST":
        # Create Razorpay order only on POST
        razorpay_order = razorpay_client.order.create({
            "amount": total_amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        # Store the Razorpay order ID and booking ID in the session
        request.session['razorpay_order_id'] = razorpay_order['id']
        request.session['booking_id'] = booking_id

        # Pass the required parameters to the template
        context = {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": total_amount,
            "booking_number": data.event_number,
        }
        return render(request, 'User/payment_process.html', context)
    else:
        # Handle GET request to show payment details before processing
        razorpay_order = razorpay_client.order.create({
            "amount": total_amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        # Store the Razorpay order ID and booking ID in the session
        request.session['razorpay_order_id'] = razorpay_order['id']
        request.session['booking_id'] = booking_id

        # Pass the required parameters to the template
        context = {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": total_amount,
            "booking_number": data.event_number,
        }
        return render(request, 'User/payment_process.html', context)
    
def payment_callback(request):
    if request.method == "POST":
        # Get payment and order details from the POST request
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Fetch the booking ID stored in session during payment process
        booking_id = request.session.get('booking_id')
        if not booking_id:
            return HttpResponseBadRequest("Booking ID not found in session")

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            # Initialize Razorpay client with your credentials
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            # Verify the payment signature
            razorpay_client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'failed', 'message': 'Payment verification failed'})

        # Fetch the booking object using booking_id
        booking = get_object_or_404(tbl_eventbooking, id=booking_id)

        # Update the booking record with payment ID and set status to 1 (completed)
        booking.payment_id = payment_id
        booking.status = 1  # Assuming 1 indicates payment completed
        booking.save()

        # Clear the session data related to payment process
        del request.session['booking_id']
        del request.session['razorpay_order_id']

        # Redirect to the ViewEventBooking page or a success page
        return redirect('WebUser:vieweventbooking')  # Replace with your URL name

    return HttpResponseBadRequest("Invalid request method")

@never_cache
@login_required
def vieweventbooking(request):
    user1 = request.user
    ticketdata=tbl_eventbooking.objects.filter(user=user1)
    for ticket in ticketdata:
        if ticket.refund_amount:
            ticket.refund_amount_display = ticket.refund_amount / 100
    return render(request,'User/ViewEventBooking.html',{'ticket':ticketdata})

def cancel_events(request):
    booking_id = request.GET.get('booking_id')
    booking = get_object_or_404(tbl_eventbooking, id=booking_id)
    booking.status = 3  # Set status to 'Canceled'
    booking.save()
    return redirect('WebUser:vieweventbooking')

@csrf_exempt
def reschedule_event(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_date = request.POST.get('new_date')
        new_time = request.POST.get('new_time')

        event_booking = get_object_or_404(tbl_eventbooking, id=booking_id)

        if not new_date or not new_time:
            return JsonResponse({'error': 'Both date and time are required.'}, status=400)

        # Convert the new date and time to datetime object
        new_datetime = timezone.datetime.strptime(f"{new_date} {new_time}", '%Y-%m-%d %H:%M')

        # Update the event booking with the new date and time
        event_booking.event_date = new_datetime.date()
        event_booking.event_starttime = new_datetime.time()
        event_booking.save()

        return JsonResponse({'message': 'Event rescheduled successfully!'}, status=200)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)