from django.shortcuts import render, get_object_or_404, redirect
from WebAdmin.models import *
from User.models import *
from Guest.models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model

# Create your views here.

@never_cache
def homepage(request):
    return render(request,'WebAdmin/Homepage.html')

def district(request):
    disobj = tbl_district.objects.all()

    if request.method == "POST":
        district_name = request.POST.get("District")
        update_id = request.POST.get("update_id")
        
        # Check if the district already exists to avoid duplicates
        if tbl_district.objects.filter(district_name__iexact=district_name).exists() and not update_id:
            messages.error(request, 'District already exists.')
            return redirect('WebAdmin:District')
        
        status = 1  # Default to active status

        # If it's an update, modify the existing district
        if update_id:
            district = get_object_or_404(tbl_district, id=update_id)
            district.district_name = district_name
            district.status = status
            district.save()
            messages.success(request, 'District updated successfully.')
        else:
            # Create new district
            tbl_district.objects.create(district_name=district_name, status=status)
            messages.success(request, 'District added successfully.')

        return redirect('WebAdmin:District')
    else:
        return render(request, "WebAdmin/District.html", {'Data': disobj})

def toggle_status(request, did):
    district = get_object_or_404(tbl_district, id=did)
    district.status = 0 if district.status == 1 else 1
    district.save()
    return redirect('WebAdmin:District')

def place(request):
    # Fetch only active districts
    disdata = tbl_district.objects.filter(status=1)
    placedata = tbl_place.objects.all()

    if request.method == "POST":
        distid = request.POST.get("dropdown")
        place_name = request.POST.get("place")
        form_mode = request.POST.get("form_mode")  # Create or update

        if form_mode == "create":
            if not tbl_place.objects.filter(place_name__iexact=place_name, district_id=distid).exists():
                tbl_place.objects.create(district_id=distid, place_name=place_name)
                return JsonResponse({"success": True, "message": "Inserted Successfully!"})
            else:
                return JsonResponse({"success": False, "error": "Place Name already exists"})

        elif form_mode == "update":
            place_id = request.POST.get("place_id")
            place_record = get_object_or_404(tbl_place, pk=place_id)
            place_record.district_id = distid
            place_record.place_name = place_name
            place_record.save()
            return JsonResponse({"success": True, "message": "Updated Successfully!"})

    return render(request, "WebAdmin/Place.html", {"Ddata": disdata, "place": placedata})

def toggle_place_status(request, pid):
    place = tbl_place.objects.get(id=pid)
    place.status = 1 if place.status == 0 else 0
    place.save()
    return redirect('WebAdmin:Place')

def boat(request):
    BoatData = list(tbl_boat.objects.values())

    if request.method == "POST":
        name = request.POST.get("txt_name")
        service = request.POST.get("dropdown")
        capacity = request.POST.get("txt_capacity")
        date = request.POST.get("txt_date")
        deck_type = request.POST.get("deckType", None)

        if not name or not service or not capacity or not date:
            return JsonResponse({"error": "All fields are required"}, status=400)

        if len(name) < 3 or not name.replace(" ", "").isalpha():
            return JsonResponse({"error": "Boat Name must be at least 3 characters long and contain only letters and spaces"}, status=400)

        if not capacity.isdigit():
            return JsonResponse({"error": "Passenger Capacity must be a number"}, status=400)

        if tbl_boat.objects.filter(boat_name=name, boat_service=service).exists():
            return JsonResponse({"error": "Boat with this name and service already exists"}, status=400)

        if service == 'Tourism and Recreational Boat Services' and not deck_type:
            return JsonResponse({"error": "Please select a deck type for tourism services"}, status=400)
        elif service == 'Public Transport Boat Services':
            deck_type = 'Single Deck'

        tbl_boat.objects.create(
            boat_name=name,
            boat_service=service,
            boat_capacity=capacity,
            boat_entrydate=date,
            boat_deck=deck_type,
            status=1
        )

        BoatData = list(tbl_boat.objects.values())  # Fetch the updated boat list
        return JsonResponse({"success": True, "message": "Boat added successfully", "BoatData": BoatData}, status=200)

    else:
        return render(request, 'WebAdmin/Boat.html', {'Data': BoatData})

def update_boat(request, did):
    updata = get_object_or_404(tbl_boat, id=did)
    BoatData = list(tbl_boat.objects.values())

    if request.method == "POST":
        name = request.POST.get("txt_name")
        service = request.POST.get("dropdown")
        capacity = request.POST.get("txt_capacity")
        date_value = request.POST.get("txt_date")
        deck_type = request.POST.get("deckType", None)

        updata.boat_name = name
        updata.boat_service = service
        updata.boat_capacity = capacity
        updata.boat_entrydate = date_value

        if service == 'Tourism and Recreational Boat Services':
            updata.boat_deck = deck_type
        else:
            updata.boat_deck = 'Single Deck'

        updata.save()

        BoatData = list(tbl_boat.objects.values())  # Fetch the updated boat list
        return JsonResponse({"success": True, "message": "Boat updated successfully", "BoatData": BoatData}, status=200)

    else:
        return render(request, 'WebAdmin/Boat.html', {'updata': updata, 'Data': BoatData})

def toggle_boat_status(did):
    boat = get_object_or_404(tbl_boat, id=did)
    boat.status = 0 if boat.status == 1 else 1
    boat.save()
    return redirect('WebAdmin:Boat')


def stationmaster_registration(request):
    active_places = tbl_place.objects.filter(status=1)

    if request.method == "POST":
        fname = request.POST.get("txt_name")
        Lname = request.POST.get("txt_Lname")
        username = request.POST.get("txt_email")
        contact = request.POST.get("txt_contact")
        address = request.POST.get("txt_address")
        gender = request.POST.get("txt_gender", "Male")
        placeid = tbl_place.objects.get(id=request.POST.get("dropdown"))
        photo = request.FILES.get("txt_photo")
        proof = request.FILES.get("txt_proof")
        email = request.POST.get("txt_email")
        default_password = f"{fname}123"

        User = get_user_model()
        
        # Check if the username (email) already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'msg': 'Email already exists. Please use a different email.'})

        try:
            # Create a new user in the auth_user table
            user = User.objects.create_user(
                first_name=fname, 
                last_name=Lname, 
                username=username, 
                email=email, 
                password=default_password, 
                role='stationmaster'
            )
            user.save()

            # Create station master profile linked to the user
            tbl_stationmaster.objects.create(
                master_user=user,
                master_contact=contact,
                master_gender=gender,
                master_address=address,
                master_place=placeid,
                master_photo=photo,
                master_proof=proof,
                status=1
            )

            # Send a welcome email to the registered email address
            subject = 'Welcome to Aqua Motus'
            message = f"Dear {fname},\n\nYou have been successfully registered as a Station Master in Aqua Motus.\nYour default password is: {default_password}\n\nPlease log in and change your password at your earliest convenience.\n\nBest regards,\nAqua Motus Team"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            return JsonResponse({'success': True, 'msg': 'Station Master Registered Successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'msg': f'An error occurred: {str(e)}'})

    return render(request, 'WebAdmin/StationMasterRegistration.html', {'Ddata': active_places})

def station_master_list(request):
    station_masters = tbl_stationmaster.objects.select_related('master_user').all()  # Fetch all tbl_stationmaster records
    return render(request, 'WebAdmin/StationMasterList.html', {'station_masters': station_masters})

def toggle_station_master_status(request):
    if request.method == 'POST':
        master_id = request.POST.get('id')
        try:
            station_master = tbl_stationmaster.objects.get(id=master_id)
            if station_master.status == 1:
                station_master.status = 0
            else:
                station_master.status = 1
            station_master.save()
            return JsonResponse({'success': True, 'new_status': station_master.status})
        except tbl_stationmaster.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Station Master not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def event_type(request):
    eventobj = tbl_eventtype.objects.all()
    if request.method == "POST":
        eventtype = request.POST.get("txt_eventtype")
        eventrate = request.POST.get("txt_rate")
        eventdetails = request.POST.get("txt_details")
        
        if not eventtype or not eventtype.isalpha() or len(eventtype) < 3:
            return JsonResponse({"error": "Event Type must be at least 3 characters long and contain only characters"}, status=400)
        
        tbl_eventtype.objects.create(event_type=eventtype, event_rate=eventrate, event_details=eventdetails, status=1)
        return JsonResponse({"success": True}, status=200)
    else:
        return render(request, 'WebAdmin/EventType.html', {'Data': eventobj})

def update_eventtype(request, did):
    eventobj = tbl_eventtype.objects.all()
    updata = get_object_or_404(tbl_eventtype, id=did)
    if request.method == "POST":
        eventtype = request.POST.get("txt_eventtype")
        eventrate = request.POST.get("txt_rate")
        eventdetails = request.POST.get("txt_details")
        if not eventtype or not eventtype.isalpha() or len(eventtype) < 3:
            return JsonResponse({"error": "Event Type must be at least 3 characters long and contain only characters"}, status=400)
        
        updata.event_type = eventtype
        updata.event_rate = eventrate
        updata.event_details = eventdetails
        updata.save()
        return JsonResponse({"success": True}, status=200)
    else:
        return render(request, 'WebAdmin/EventType.html', {'Data': eventobj, 'updata': updata})

def toggle_eventtype_status(did):
    eventtype = get_object_or_404(tbl_eventtype, id=did)
    eventtype.status = 0 if eventtype.status == 1 else 1
    eventtype.save()
    return redirect('WebAdmin:EventType')

def report(request):
    booking = tbl_ticketbooking.objects.all()
    return render(request, 'WebAdmin/Report.html', {"booking": booking})

def ajaxreport(request):
    # Get filter parameters from the request
    fdate = request.GET.get("fdate", "")
    tdate = request.GET.get("tdate", "")
    status = request.GET.get("status", "")

    # Filter booking data based on the provided parameters
    booking = tbl_ticketbooking.objects.all()

    if fdate:
        booking = booking.filter(date__gte=fdate)
    if tdate:
        booking = booking.filter(date__lte=tdate)
    if status:
        booking = booking.filter(payment=status)

    # Render the filtered results in the AjaxReport template
    return render(request, "WebAdmin/AjaxReport.html", {"booking": booking})