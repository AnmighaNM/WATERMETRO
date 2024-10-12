from django.shortcuts import render,redirect,get_object_or_404
from StationMaster.models import *
from WebAdmin.models import *
from User.models import *
from django.urls import reverse
from datetime import timedelta
import re
from django.http import HttpResponseBadRequest
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required  

# Create your views here.

@never_cache
@login_required
def homepage(request):
    master = tbl_stationmaster.objects.get(user=request.user)  # Adjust based on your model's structure
    return render(request, 'StationMaster/MasterHome.html', {'masterdata': master})

@never_cache
@login_required
def myprofile(request):
    user1 = request.user  
    # Assuming the user exists in tbl_stationmaster
    master = tbl_stationmaster.objects.get(user=user1)  
    return render(request,'StationMaster/MyProfile.html',{'masterdata':master,'master':user1})

@never_cache
@login_required
def editprofile(request):
    user1 = request.user
    user = tbl_stationmaster.objects.get(user=user1)
    if request.method == "POST":
        user1.first_name = request.POST.get("txt_name")
        user1.last_name = request.POST.get("txt_lastname")
        user1.email = request.POST.get("txt_email")
        user1.username = request.POST.get("txt_email")
        user.master_contact = request.POST.get("txt_contact")
        user.master_address = request.POST.get("txt_address")
        user1.save()
        user.save()
        request.session['profile_updated'] = True
        return redirect('WebStationMaster:MyProfile')
    else:
        profile_updated = request.session.pop('profile_updated', False)
        return render(request, 'StationMaster/EditProfile.html', {'master': user, 'masterdata': user1, 'profile_updated': profile_updated})

@never_cache
@login_required
def changepassword(request):
    user1 = request.user
    master = tbl_stationmaster.objects.get(user=user1)
    
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
                return render(request, 'StationMaster/MyProfile.html', {'msg': msg, 'masterdata':master,'master':user1})
            else:
                msg = "New password and confirm password do not match."
                return render(request, 'StationMaster/ChangePassword.html', {'msg': msg, 'masterdata':master,'master':user1})
        else:
            msg = "Current password is incorrect."
            return render(request, 'StationMaster/ChangePassword.html', {'msg': msg, 'masterdata':master,'master':user1})
    else:
        return render(request, 'StationMaster/ChangePassword.html', {'masterdata':master,'master':user1})

@never_cache
@login_required
def services(request):
    places = tbl_place.objects.filter(status=1)
    boats = tbl_boat.objects.filter(status=1,boat_service = 'Public Transport Boat Services')
    services = tbl_services.objects.all()
    error_message = ""

    if request.method == "POST":
        startpoint_id = request.POST.get("services_startpoint")
        endpoint_id = request.POST.get("services_endpoint")
        rate = request.POST.get("rate")
        duration = request.POST.get("duration")
        starttime = request.POST.get("assignboat_starttime")
        boat_id = request.POST.get("assignboat_boat")

        if not (startpoint_id and endpoint_id and rate and duration and starttime and boat_id):
            error_message = "Please fill all fields."
        else:
            try:
                rate = float(rate)
                startpoint = tbl_place.objects.get(id=startpoint_id)
                endpoint = tbl_place.objects.get(id=endpoint_id)
                boat = tbl_boat.objects.get(id=boat_id)
                duration_parts = duration.split(':')
                duration_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
                duration = timedelta(seconds=duration_seconds)
                tbl_services.objects.create(
                    assignboat_boat=boat,
                    services_startpoint=startpoint,
                    services_endpoint=endpoint,
                    rate=rate,
                    duration=duration,
                    assignboat_starttime=starttime
                )
                return redirect('WebStationMaster:Services')
            except ValueError:
                error_message = "Please enter a valid rate."
            except Exception as e:
                error_message = str(e)

    return render(request, 'StationMaster/Services.html', {
        'places': places,
        'boats': boats,
        'services': services,
        'error_message': error_message
    })


def parse_duration(duration_str):
    """Convert a string in 'HH:MM:SS' format to a timedelta object."""
    if not duration_str:
        return None
    try:
        parts = re.split('[:]', duration_str)
        if len(parts) != 3:
            raise ValueError("Duration must be in 'HH:MM:SS' format.")
        hours, minutes, seconds = map(int, parts)
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except ValueError:
        raise ValueError("Invalid duration format. Use 'HH:MM:SS'.")

@never_cache
@login_required
def update_service(request, did):
    places = tbl_place.objects.filter(status=1)
    boats = tbl_boat.objects.filter(status=1)
    updata = get_object_or_404(tbl_services, id=did)
    error_message = ""

    if request.method == "POST":
        startpoint_id = request.POST.get("services_startpoint")
        endpoint_id = request.POST.get("services_endpoint")
        rate = request.POST.get("rate")
        duration_str = request.POST.get("duration")
        starttime = request.POST.get("assignboat_starttime")
        boat_id = request.POST.get("assignboat_boat")

        if not (startpoint_id and endpoint_id and rate and duration_str and starttime and boat_id):
            error_message = "Please fill all fields."
        else:
            try:
                rate = float(rate)
                duration = parse_duration(duration_str)
                updata.services_startpoint = tbl_place.objects.get(id=startpoint_id)
                updata.services_endpoint = tbl_place.objects.get(id=endpoint_id)
                updata.rate = rate
                updata.duration = duration
                updata.assignboat_starttime = starttime
                updata.assignboat_boat = tbl_boat.objects.get(id=boat_id)
                updata.save()
                return redirect('WebStationMaster:View_Services')
            except ValueError as e:
                error_message = str(e)
            except tbl_place.DoesNotExist:
                error_message = "Invalid start or end point."
            except tbl_boat.DoesNotExist:
                error_message = "Invalid boat."

    return render(request, 'StationMaster/Services.html', {
        'places': places,
        'boats': boats,
        'udata': updata,
        'error_message': error_message
    })


def toggle_service_status(request,did):
    service = get_object_or_404(tbl_services, id=did)
    service.status = 1 if service.status == 0 else 0
    service.save()
    return redirect(reverse('WebStationMaster:View_Services'))

@never_cache
@login_required
def view_services(request):
    services = tbl_services.objects.all()
    return render(request, 'StationMaster/AssignBoatsView.html', {
        'services': services
    })

@never_cache
@login_required
def viewticketbooking(request):
    bookings = tbl_ticketbooking.objects.all()
    for booking in bookings:
        if booking.refund_amount:
            booking.refund_amount_display = booking.refund_amount / 100
    return render(request, "StationMaster/ViewTicketBooking.html", {"booking": bookings})

@never_cache
@login_required
def vieweventbooking(request):
    bookings = tbl_eventbooking.objects.all()
    for booking in bookings:
        if booking.refund_amount:
            booking.refund_amount_display = booking.refund_amount / 100
    return render(request, "StationMaster/ViewEventBooking.html", {"booking": bookings})

def assign_boat(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        boat_id = request.POST.get('boat_id')
        
        booking = get_object_or_404(tbl_eventbooking, id=booking_id)
        boat = get_object_or_404(tbl_boat, id=boat_id)
        
        # Assign the selected boat to the booking
        booking.assign = boat
        booking.status = 2  # Change status to assigned
        booking.save()
        
        return redirect('WebStationMaster:vieweventbooking')

def get_active_boats(request):
    boat_deck = request.GET.get('boat_deck')
    # Filter boats that are active and in the services 'Tourism' or 'Recreational Boat Services'
    boats = tbl_boat.objects.filter(status=1,boat_deck = boat_deck, boat_service__in=['Tourism and Recreational Boat Services'])
    boat_list = [{'id': boat.id, 'boat_name': boat.boat_name , 'boat_capacity': boat.boat_capacity} for boat in boats]
    return JsonResponse({'boats': boat_list})


@never_cache
@login_required
def viewcomplaints(request):
    complaintdata = Feedback.objects.filter(status=0)
    return render(request, 'StationMaster/ViewComplaint.html', {'Data': complaintdata})

@never_cache
@login_required
def repliedcomplaints(request):
    replydata = Feedback.objects.filter(status=1)
    return render(request, 'StationMaster/RepliedComplaints.html', {'ReplyData': replydata})

@never_cache
@login_required
def reply(request, did):
    data = Feedback.objects.get(id=did)
    if request.method == "POST":
        reply = request.POST.get('txt_reply')
        data.reply = reply
        data.status = 1
        data.save()
        return redirect('WebStationMaster:ViewComplaint')
    else:
        return render(request, 'StationMaster/reply.html', {'data': data})
    
# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def initiate_refund(request):
    # Fetch the booking object using booking_id
    booking_id = request.POST.get('booking_id')
    
    if not booking_id:
        return HttpResponseBadRequest("Booking ID is missing")

    # Fetch the booking object using booking_id
    booking = get_object_or_404(tbl_eventbooking, id=booking_id)
    
    if booking.status != 3:
        return HttpResponseBadRequest("Refund is not allowed for this booking status")

    event_type_rate = booking.event_type.event_rate

    # Ensure event_type_rate is numeric and calculate 80% refund amount
    try:
        event_type_rate = float(event_type_rate)
        refund_amount = int(event_type_rate * 80 / 100 * 100)  # Convert to paise
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid rate value")

    booking.refund_amount = refund_amount
    booking.save()
    
    if request.method == "POST":
        # Process the refund via Razorpay
        razorpay_order = razorpay_client.order.create({
            "amount": refund_amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        request.session['booking_id'] = booking_id
        request.session['razorpay_order_id'] = razorpay_order['id']
        
        # Render the payment page for refund
        context = {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": refund_amount,
            "booking_number": booking.event_number,
        }
        return render(request, 'StationMaster/payment_process.html', context)
    else:
        return HttpResponseBadRequest("Invalid request method")

def payment_callback(request):
    if request.method == "POST":
        # Fetch the booking ID stored in session during payment process
        booking_id = request.session.get('booking_id')
        if not booking_id:
            return HttpResponseBadRequest("Booking ID not found in session")

        # Fetch the booking object using booking_id
        booking = get_object_or_404(tbl_eventbooking, id=booking_id)

        # Update the booking record and set status to 4 (refunded)
        booking.status = 4  # Assuming 4 indicates refund completed
        booking.save()

        # Clear the session data related to payment process
        del request.session['booking_id']
        del request.session['razorpay_order_id']

        # Redirect to the ViewEventBooking page or a success page
        return redirect('WebStationMaster:vieweventbooking')

    return HttpResponseBadRequest("Invalid request method")

def refund(request):
    # Fetch the booking object using booking_id
    booking_id = request.POST.get('booking_id')
    
    if not booking_id:
        return HttpResponseBadRequest("Booking ID is missing")

    # Fetch the booking object using booking_id
    booking = get_object_or_404(tbl_ticketbooking, id=booking_id)
    
    if booking.payment != 2:
        return HttpResponseBadRequest("Refund is not allowed for this booking status")

    rate = booking.service.rate
    adults  = booking.adults_count 
    childrens  = booking.childrens_count
    event_type_rate = int((rate*float(adults))) + int((rate*float(childrens)))
    

    # Ensure event_type_rate is numeric and calculate 80% refund amount
    try:
        event_type_rate = float(event_type_rate)
        refund_amount = int(event_type_rate * 50 / 100 * 100)  # Convert to paise
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid rate value")

    booking.refund_amount = refund_amount
    booking.save()
    
    if request.method == "POST":
        # Process the refund via Razorpay
        razorpay_order = razorpay_client.order.create({
            "amount": refund_amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        request.session['booking_id'] = booking_id
        request.session['razorpay_order_id'] = razorpay_order['id']
        
        # Render the payment page for refund
        context = {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": refund_amount,
            "booking_number": booking.ticket_number,
        }
        return render(request, 'StationMaster/payment.html', context)
    else:
        return HttpResponseBadRequest("Invalid request method")

def callback(request):
    if request.method == "POST":
        # Fetch the booking ID stored in session during payment process
        booking_id = request.session.get('booking_id')
        if not booking_id:
            return HttpResponseBadRequest("Booking ID not found in session")

        # Fetch the booking object using booking_id
        booking = get_object_or_404(tbl_ticketbooking, id=booking_id)

        # Update the booking record and set status to 4 (refunded)
        booking.payment = 3  # Assuming 4 indicates refund completed
        booking.save()

        # Clear the session data related to payment process
        del request.session['booking_id']
        del request.session['razorpay_order_id']

        # Redirect to the ViewEventBooking page or a success page
        return redirect('WebStationMaster:ViewTicketBooking')

    return HttpResponseBadRequest("Invalid request method")

@never_cache
@login_required
def report(request):
    booking = tbl_ticketbooking.objects.all()
    eventbooking = tbl_eventbooking.objects.all()
    combined_list = []
    counter = 1
    for item in booking:
        combined_list.append({
            'type': 'booking',
            'data': item,
            'counter': counter
        })
        counter += 1

    # Add eventbooking items to combined list with a counter
    for item in eventbooking:
        combined_list.append({
            'type': 'eventbooking',
            'data': item,
            'counter': counter
        })
        counter += 1
    return render(request, 'StationMaster/Report.html', {"combined_list": combined_list})


def ajaxreport(request):
    # Get filter parameters from the request
    fdate = request.GET.get("fdate", "")
    tdate = request.GET.get("tdate", "")
    status = request.GET.get("status", "")
    ticket_type = request.GET.get("ticketType", "")

    # Initialize empty queryset
    booking = tbl_ticketbooking.objects.none()
    eventbooking = tbl_eventbooking.objects.none()
    combined_list = []
    counter = 1
    # Filter based on ticket type
    if ticket_type == "1":  # Public Transport Boat Services (ticket booking)
        booking = tbl_ticketbooking.objects.all()
        if fdate:
            booking = booking.filter(date__gte=fdate)
        if tdate:
            booking = booking.filter(date__lte=tdate)
        if status:
            booking = booking.filter(payment=status)

    elif ticket_type == "2":  # Tourism and Recreational Boat Services (event booking)
        eventbooking = tbl_eventbooking.objects.all()
        if fdate:
            eventbooking = eventbooking.filter(event_date__gte=fdate)
        if tdate:
            eventbooking = eventbooking.filter(event_date__lte=tdate)
        if status:
            eventbooking = eventbooking.filter(status=status)

    else:  # Show both ticket and event bookings (All)
        booking = tbl_ticketbooking.objects.all()
        eventbooking = tbl_eventbooking.objects.all()
        if fdate:
            booking = booking.filter(date__gte=fdate)
            eventbooking = eventbooking.filter(event_date__gte=fdate)
        if tdate:
            booking = booking.filter(date__lte=tdate)
            eventbooking = eventbooking.filter(event_date__lte=tdate)
        if status:
            booking = booking.filter(payment=status)
            eventbooking = eventbooking.filter(status=status)
            
    for item in booking:
        combined_list.append({
            'type': 'booking',
            'data': item,
            'counter': counter
        })
        counter += 1

    # Add eventbooking items to combined list with a counter
    for item in eventbooking:
        combined_list.append({
            'type': 'eventbooking',
            'data': item,
            'counter': counter
        })
        counter += 1
    # Render the filtered results in the AjaxReport template
    return render(request, "StationMaster/AjaxReport.html", {"combined_list": combined_list})
