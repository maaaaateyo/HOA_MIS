from django.conf import settings
import base64
import requests
import calendar as cal
from django.conf import settings
from django.http import HttpResponseRedirect
from collections import Counter
from datetime import date, timedelta, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import MemberSignUpForm, OfficerSignUpForm, ReservationForm, CustomLoginForm, HouseholdForm, ResidentForm, RememberMeAuthenticationForm, ReservationStatusForm, ServiceRequestForm, ServiceRequestStatusForm, BillingStatusForm, NewsfeedForm, NewsletterForm, OfficerChangeForm, MemberChangeForm, ContactForm, AnnouncementForm, GrievanceForm, GrievanceStatusForm, NoteForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Household, Resident, Reservation, Billing, ServiceRequest, Newsfeed, Officer, User, Announcement, GrievanceAppointment, Note, Notification, Member, Officer
from django.contrib import messages
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.http import JsonResponse
from django.db import IntegrityError, models
from django.utils.timezone import now
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal



User = get_user_model()

# Create your views here.

#views for initial
def home(request):
    return render(request, 'initial/home.html')

def communitymap(request):
    return render(request, 'initial/communitymap.html')

def get_month_calendar(year, month):
    cal_obj = cal.Calendar()
    month_days = cal_obj.monthdayscalendar(year, month)  # List of weeks, each a list of days
    calendar_data = []

    for week in month_days:
        week_data = []
        for day in week:
            if day != 0:  # Avoid 0 days, which are placeholders for empty days in the month
                # Get reservations and announcements for this day
                day_reservations = Reservation.objects.filter(
                    reservation_date=date(year, month, day),
                    status='Confirmed'
                )
                day_appointments = GrievanceAppointment.objects.filter(
                    reservation_date=date(year, month, day),
                    status='Confirmed'
                )
                day_announcements = Announcement.objects.filter(
                    date=date(year, month, day)
                )
                day_data = {
                    'day': day,
                    'reservations': day_reservations,
                    'grievance_appointments': day_appointments,
                    'announcements': day_announcements
                }
            else:
                day_data = {'day': day, 'reservations': [], 'grievance_appointments': [], 'announcements': []}  # No data for placeholder days
            week_data.append(day_data)
        calendar_data.append(week_data)
    
    return calendar_data

def calendar(request, year=None, month=None): 
    today = date.today()

    # Check if a month is selected from the input form
    selected_month_str = request.GET.get('selected_month')
    if selected_month_str:
        # Parse the selected month (format YYYY-MM) to set year and month
        selected_date = datetime.strptime(selected_month_str, "%Y-%m")
        year = selected_date.year
        month = selected_date.month
    elif year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    # The rest of the logic remains the same as before.
    month_calendar = get_month_calendar(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    current_month = date(year, month, 1)
    prev_month_name = (date(year, prev_month, 1)).strftime('%B')
    next_month_name = (date(year, next_month, 1)).strftime('%B')

    context = {
        'calendar': month_calendar,
        'year': year,
        'month': current_month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month_name': prev_month_name,
        'next_month_name': next_month_name,
    }

    return render(request, 'initial/calendar.html', context)

def news(request):
    latest_news = Newsfeed.objects.filter(created_at__lte=now()).order_by('-created_at').first()
    
    # Fetch all newsfeeds excluding the latest news
    if latest_news:
        newsfeeds = Newsfeed.objects.exclude(pk=latest_news.pk).order_by('-created_at')
    else:
        newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    
    # Fetch the latest announcement with a future or current date
    latest_announcement = Announcement.objects.filter(date__gte=now()).order_by('-date').first()
    
    return render(request, 'initial/news.html', {'newsfeeds': newsfeeds, 'latest_announcement': latest_announcement, 'latest_news': latest_news})
    
def news_article(request, pk):
    newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    return render(request, 'initial/news-single.html', {'newsfeeds': newsfeeds, 'newsfeed': newsfeed})

def about(request):
    officer_hierarchy = {
        'President': 1,
        'Vice President': 2,
        'Secretary': 3,
        'Treasurer': 4,
        'Auditor': 5,
        'P.R.O': 6,
    }
    officers = list(Officer.objects.all())
    officers.sort(key=lambda x: officer_hierarchy.get(x.officer_position, 999))

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")  # Add success message
            return redirect('about')  # Redirect to the same page to clear the form
    else:
        form = ContactForm()

    return render(request, 'initial/about.html', {
        'form': form,
        'officers': officers
    })

def signup(request):
    return render(request, 'initial/reghome.html')

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('subscribe_newsletter')
            except IntegrityError:
                form.add_error('email', 'This email is already subscribed!')
    else:
        form = NewsletterForm()
    return render(request, 'initial/home.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'initial/login.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        user = self.request.user

        # Ensure the user is authenticated
        if not user.is_authenticated:
            return reverse_lazy('login')  # Redirect to login if user is not authenticated

        # Redirect based on user role
        if user.is_user_officer():
            return reverse_lazy('officer_landing_page', kwargs={'username': user.username})
        else:
            return reverse_lazy('member_landing_page', kwargs={'username': user.username})

    def form_valid(self, form):
        # Log in the user
        remember_me = form.cleaned_data.get('remember_me', False)
        if not remember_me:
            self.request.session.set_expiry(0)  # Session expires when browser is closed
        login(self.request, form.get_user())
        return super().form_valid(form)

class MemberSignUpView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'initial/member_signup.html', {'form': MemberSignUpForm()})

    def post(self, request, *args, **kwargs):
        form = MemberSignUpForm(request.POST)
        if form.is_valid():
            # Save user with commit=True to ensure it gets saved to the database
            user = form.save(commit=False)  # Save the user but don't commit to the database yet
            user.is_active = False  # Make the user inactive initially
            user.save()  # Save the user instance fully to the database
            
            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)  # Assuming the User model has the 'is_officer' flag
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Link to officer directly
                    content=f"A new member has signed up and is awaiting activation: {user.fname} {user.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            login(request, user)
            return redirect('login')

        return render(request, 'initial/member_signup.html', {'form': form})

class OfficerSignUpView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'initial/officer_signup.html', {'form': OfficerSignUpForm()})

    def post(self, request, *args, **kwargs):
        form = OfficerSignUpForm(request.POST)
        if form.is_valid():
            # Save user with commit=False to ensure it gets saved to the database
            user = form.save(commit=False)  # Save the user but don't commit to the database yet
            user.is_active = False  # Make the user inactive initially
            user.save()  # Save the user instance fully to the database
            
            # Create a notification for all officers, excluding the newly registered officer
            officers = User.objects.filter(is_officer=True).exclude(id=user.id)  # Exclude the new officer
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Link to officer directly
                    content=f"A new officer has signed up and is awaiting activation: {user.fname} {user.lname}.",
                    created_at=timezone.now()  # Current time using timezone-aware datetime
                )
                notification.save()

            login(request, user)  # Log in the newly registered officer
            return redirect('login')

        return render(request, 'initial/officer_signup.html', {'form': form})

def logout_view(request):
    # Log out the user.
    logout(request)
    # Redirect to a success page.
    return redirect('home')

#member_views_dashboard
@login_required
def member_landing_page(request, username):
    user = request.user

    # Initialize all counts to zero
    household_count = 0
    reservation_count = 0
    appointment_count = 0
    request_count = 0
    overdue_count = 0

    try:
        # Fetch the household where the logged-in user is the owner
        household = Household.objects.get(owner_name=user)

        # Count the total number of residents in the household
        household_count = Resident.objects.filter(household=household).count()

        # Count total reservations
        reservation_count = Reservation.objects.filter(household=household, status='Pending').count()

        # Count total appointments
        appointment_count = GrievanceAppointment.objects.filter(household=household, status='Pending').count()

        # Count total requests
        request_count = ServiceRequest.objects.filter(household=household, status='Pending').count()

        # Count total overdues
        overdue_count = Billing.objects.filter(household=household, status='Overdue').count()

    except Household.DoesNotExist:
        # All counts are already initialized to 0

        pass  # You can remove this line, as it's not needed

    # Note functionality
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = user
            note.save()
            return redirect('member_landing_page', username=username)
    else:
        form = NoteForm()

    # Get existing notes
    user_notes = Note.objects.filter(user=user).order_by('-created_at')
    latest_announcement = Announcement.objects.order_by('-date', '-time').first()

    context = {
        'household_count': household_count,
        'reservation_count': reservation_count,
        'appointment_count': appointment_count,
        'request_count': request_count,
        'overdue_count': overdue_count,
        'form': form,
        'user_notes': user_notes,
        'latest_announcement': latest_announcement,
    }

    return render(request, 'member/homeowner_dashboard.html', context)
    
def delete_note(request, username, note_id):
    note = get_object_or_404(Note, id=note_id, user__username=username)  # Adjust as necessary based on your Note model structure
    if request.method == 'POST':
        note.delete()
        return redirect('member_landing_page', username=username)  # Redirect back to the landing page after deletion
    return redirect('member_landing_page', username=username)

#member_views_news    
@login_required
def newsfeed(request, username):
    latest_news = Newsfeed.objects.filter(created_at__lte=now()).order_by('-created_at').first()
    # Fetch all newsfeeds excluding the latest news
    if latest_news:
        newsfeeds = Newsfeed.objects.exclude(pk=latest_news.pk).order_by('-created_at')
    else:
        newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    
    # Fetch the latest announcement with a future or current date
    latest_announcement = Announcement.objects.filter(date__gte=now()).order_by('-date').first()
    
    return render(request, 'member/newsfeed/newsfeed.html', {'newsfeeds': newsfeeds, 'latest_announcement': latest_announcement, 'latest_news': latest_news})

@login_required
def newsarticle(request, username, pk):
    newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    return render(request, 'member/newsfeed/newsarticle.html', {'newsfeed': newsfeed, 'newsfeeds': newsfeeds})

#member_views_household
class HouseholdDetailsView(TemplateView):
    template_name = 'member/household/household_detail.html'

    def get(self, request, username):
        user = request.user
        try:
            household = Household.objects.get(owner_name=user)
        except Household.DoesNotExist:
            return redirect('add_household', username=request.user.get_username())  # Redirect if no household exists

        # Fetch residents and billings related to the household
        residents = Resident.objects.filter(household=household)
        billings = Billing.objects.filter(household=household)

        context = {
            'household': household,
            'residents': residents,
            'billings': billings
        }
        return render(request, self.template_name, context)

@login_required
def add_household(request, username):
    user = request.user
    if request.method == 'POST':
        form = HouseholdForm(request.POST)
        if form.is_valid():
            household = form.save(commit=False)
            household.owner_name = request.user
            household.save()
            
            # Create a notification for all officers
            from django.contrib.auth import get_user_model
            User = get_user_model()  # Ensure you are using the correct User model
            officers = User.objects.filter(is_officer=True)  # Assuming the User model has the 'is_officer' flag
            
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,  # Link to the officer directly
                    content=f"A new household has been added by {user.fname} {user.lname}.",
                    created_at=timezone.now()
                )

            return redirect('household_detail', username=request.user.get_username())
    else:
        form = HouseholdForm()

    # Pass the choices to the template context
    block_choices = Household.BLOCK_CHOICES
    street_choices = Household.STREET_CHOICES
    home_tenure_choices = Household.HOME_TENURE_CHOICES
    land_tenure_choices = Household.LAND_TENURE_CHOICES
    construction_choices = Household.CONSTRUCTION_CHOICES
    kitchen_choices = Household.KITCHEN_CHOICES
    water_facility_choices = Household.WATER_FACILITY_CHOICES
    toilet_facility_choices = Household.TOILET_FACILITY_CHOICES

    return render(request, 'member/household/add_household.html', {
        'form': form,
        'block_choices': block_choices,
        'street_choices': street_choices,
        'home_tenure_choices': home_tenure_choices,
        'land_tenure_choices': land_tenure_choices,
        'construction_choices': construction_choices,
        'kitchen_choices': kitchen_choices,
        'water_facility_choices': water_facility_choices,
        'toilet_facility_choices': toilet_facility_choices,
    })

class edit_household(View):
    def get(self, request, username):
        household = get_object_or_404(Household, owner_name=request.user)
        form = HouseholdForm(instance=household)
        return render(request, 'member/household/edit_household.html', {'form': form, 'household': household})

    def post(self, request, username):
        household = get_object_or_404(Household, owner_name=request.user)
        form = HouseholdForm(request.POST, instance=household)
        
        if form.is_valid():
            form.save()

            # Create a notification for all officers after successfully editing the household
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                # Create the notification content (you can customize this message)
                content = f"The household of {household.owner_name} has been updated."

                # Create and save the notification
                Notification.objects.create(
                    recipient=officer,
                    content=content,
                    created_at=timezone.now()
                )

            return redirect('household_detail', username=username)
        
        return render(request, 'member/household/edit_household.html', {'form': form, 'household': household})

#member_views_resident
@login_required
def resident_detail(request, username, pk):
    resident = get_object_or_404(Resident, pk=pk)
    return render(request, 'member/household/resident_detail.html', {'resident': resident})

@login_required
def add_resident(request, username):
    household = get_object_or_404(Household, owner_name=request.user)
    
    if request.method == "POST":
        form = ResidentForm(request.POST)
        if form.is_valid():
            resident = form.save(commit=False)
            resident.household = household  # Assign the household
            resident.save()

            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                content = f"A new resident has been added to the household of {household.owner_name}: {resident.first_name} {resident.last_name}."

                # Create and save the notification
                Notification.objects.create(
                    recipient=officer,
                    content=content,
                    created_at=timezone.now()  # Current time using timezone-aware datetime
                )

            return redirect('household_detail', username=username)
    else:
        form = ResidentForm()

    gender_choices = Resident.GENDER_CHOICES
    civil_status_choices = Resident.CIVIL_STATUS_CHOICES
    religion_choices = Resident.RELIGION_CHOICES
    educational_attainment_choices = Resident.EDUCATIONAL_ATTAINMENT_CHOICES

    return render(request, 'member/household/add_edit_resident.html', {
        'form': form, 
        'household': household,
        'gender_choices': gender_choices,
        'civil_status_choices': civil_status_choices,
        'religion_choices': religion_choices,
        'educational_attainment_choices': educational_attainment_choices
    })

@login_required
def edit_resident(request, username, pk):
    resident = get_object_or_404(Resident, pk=pk)
    
    if request.method == "POST":
        form = ResidentForm(request.POST, instance=resident)
        if form.is_valid():
            # Save the updated resident
            resident = form.save()

            # Create a notification for all officers about the update
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                content = f"The details of the resident {resident.first_name} {resident.last_name} have been updated in the household of {resident.household.owner_name}."

                # Create and save the notification
                Notification.objects.create(
                    recipient=officer,
                    content=content,
                    created_at=timezone.now()  # Current time using timezone-aware datetime
                )

            return redirect('resident_detail', username=username, pk=resident.pk)
    else:
        form = ResidentForm(instance=resident)

    gender_choices = Resident.GENDER_CHOICES
    civil_status_choices = Resident.CIVIL_STATUS_CHOICES
    religion_choices = Resident.RELIGION_CHOICES
    educational_attainment_choices = Resident.EDUCATIONAL_ATTAINMENT_CHOICES

    return render(request, 'member/household/add_edit_resident.html', {
        'form': form, 
        'resident': resident,
        'gender_choices': gender_choices,
        'civil_status_choices': civil_status_choices,
        'religion_choices': religion_choices,
        'educational_attainment_choices': educational_attainment_choices
    })

@login_required
def delete_resident(request, username, pk):
    resident = get_object_or_404(Resident, pk=pk)
    
    if request.method == 'POST':
        # Store the name of the resident to be deleted for notification content
        deleted_resident_name = f"{resident.first_name} {resident.last_name}"

        # Delete the resident
        resident.delete()
        
        # Create a notification for all officers about the resident's deletion
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            content = f"The resident {deleted_resident_name} has been deleted from the household of {resident.household.owner_name}."
            
            # Create and save the notification
            Notification.objects.create(
                recipient=officer,
                content=content,
                created_at=timezone.now()  # Current time using timezone-aware datetime
            )

        messages.success(request, "Resident deleted successfully.")
        return redirect('household_detail', username=username)
    
    else:
        messages.error(request, "Invalid request method.")
        return redirect('household_detail', username=username)

#member_views_reservation
class MyReservation(ListView):
    model = Reservation
    template_name = 'member/reservation/my_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        # Attempt to get the household of the currently logged-in user
        try:
            self.household = Household.objects.get(owner_name=self.request.user)
        except Household.DoesNotExist:
            # If no household exists, return an empty queryset
            self.household = None
            return Reservation.objects.none()

        # If a household exists, filter the reservations by this household
        queryset = super().get_queryset().filter(household=self.household)

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(amenities__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        # Check if the user has a household
        context['no_household'] = self.household is None

         # Add pagination
        reservations = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(reservations, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['reservations'] = page_obj

        return context

@login_required
def make_reservation(request, username):
    user = request.user
    try:
        # Ensure we're getting the correct Household instance
        household = Household.objects.get(owner_name=user)
    except Household.DoesNotExist:
        # Handle the case where the user has no associated household
        messages.error(request, "You do not have an associated household.")
        return redirect('add_household', username=username)  # Redirect to a page to create a household

    is_owner = household.owner_name == user
    reservations = household.reservations.all()

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            # Assign the household instance, not the user
            reservation.household = household
            reservation.save()
            
            # Create a notification for all officers, except the user who made the reservation
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Link to officer directly
                    content=f"A new reservation has been made by {user.fname} {user.lname} for the household {household.owner_name}.",
                    created_at=timezone.now()  # Use current time for the notification
                )
                notification.save()

            messages.success(request, 'Reservation created successfully!')
            # Redirect to a success page or the same page with a success message
            return redirect('make_reservation', username=username)  # Adjust the redirect as needed
    else:
        form = ReservationForm()

    return render(request, 'member/reservation/reservation_form.html', {
        'form': form,
        'user': user,
        'household': household,
        'reservations': reservations,
        'is_owner': is_owner,
    })

@login_required
def update_reservation(request, username, request_id):
    reservation = get_object_or_404(Reservation, id=request_id)
    user = request.user
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, request.FILES, instance=reservation)
        if form.is_valid():
            form.save()
            
            # Create a notification for all officers, except the user who updated the reservation
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Link to officer directly
                    content=f"The reservation for household {reservation.household.owner_name} has been updated by {user.fname} {user.lname}.",
                    created_at=timezone.now()  # Use current time for the notification
                )
                notification.save()

            messages.success(request, 'Reservation updated successfully!')
            # Redirect to a success page or the same page with a success message
            return redirect('update_reservation', username=username, request_id=request_id)  # Use 'request_id'
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'member/reservation/update_reservation.html', {
        'form': form,
        'reservation': reservation,
    })

@login_required
def cancel_reservation(request, username, request_id):
    reservation = get_object_or_404(Reservation, id=request_id)
    user = request.user
    
    if request.method == 'POST':
        reservation.status = 'Canceled'  # Update the status to 'Canceled' or your equivalent status
        reservation.save()

        # Create a notification for all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The reservation for household {reservation.household.owner_name} has been canceled by {user.fname} {user.lname}.",
                created_at=timezone.now()  # Use the current time for the notification
            )
            notification.save()

        messages.success(request, 'Reservation has been canceled successfully!')
        return redirect('my_reservation', username=request.user.username)
    else:
        # If it's a GET request, show the confirmation page
        return render(request, 'member/reservation/cancel_confirmation.html', {'reservation': reservation})

#member_views_request
class MyRequest(ListView):
    model = ServiceRequest
    template_name = 'member/services/my_requests.html'
    context_object_name = 'service_requests'
    
    def get_queryset(self):
        # Attempt to get the household of the currently logged-in user
        try:
            self.household = Household.objects.get(owner_name=self.request.user)
        except Household.DoesNotExist:
            # If no household exists, return an empty queryset
            self.household = None
            return ServiceRequest.objects.none()

        queryset = super().get_queryset().filter(household=self.household)

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(service_type__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        context['no_household'] = self.household is None

         # Add pagination
        service_requests = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(service_requests, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['service_requests'] = page_obj

        return context

@login_required
def submit_request(request, username):
    user = request.user
    try:
        # Ensure we're getting the correct Household instance
        household = Household.objects.get(owner_name=user)
    except Household.DoesNotExist:
        # Handle the case where the user has no associated household
        messages.error(request, "You do not have an associated household.")
        return redirect('add_household', username=username)  # Redirect to a page to create a household
    
    is_owner = household.owner_name == user
    servicerequests = household.service_requests.all()

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            service_request = form.save(commit=False)
            # Assign the household instance, not the user
            service_request.household = household
            service_request.save()

            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A new request has been submitted by {user.fname} {user.lname} for household {household.owner_name}.",
                    created_at=timezone.now()  # Use the current time for the notification
                )
                notification.save()

            messages.success(request, 'Request created successfully!')
            # Redirect to a success page or the same page with a success message
            return redirect('submit_request', username=username)
    else:
        form = ServiceRequestForm()

    return render(request, 'member/services/submit_request.html', {
        'form': form,
        'user': user,
        'household': household,
        'servicerequests': servicerequests,
        'is_owner': is_owner,
    })

@login_required
def update_request(request, username, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES, instance=service_request)
        if form.is_valid():
            form.save()

            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"The request #{service_request.id} has been updated by {request.user.fname} {request.user.lname}.",
                    created_at=timezone.now()  # Use the current time for the notification
                )
                notification.save()

            messages.success(request, 'Request updated successfully!')
            return redirect('update_request', username=username, request_id=request_id)
    else:
        form = ServiceRequestForm(instance=service_request, initial={'image': service_request.image})
    
    return render(request, 'member/services/update_request.html', {'form': form, 'service_request': service_request})

@login_required
def cancel_request(request, username, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    if request.method == 'POST':
        service_request.status = 'Canceled'  # Or your equivalent status
        service_request.save()

        # Create a notification for all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The request #{service_request.id} has been canceled by {request.user.fname} {request.user.lname}.",
                created_at=timezone.now()  # Use the current time for the notification
            )
            notification.save()

        return redirect('my_request', username=username)
    else:
        # If it's a GET request, show the confirmation page
        return render(request, 'member/services/cancel_confirmation.html', {'service_request': service_request})

#member_views_appointment
class MyAppointment(ListView):
    model = GrievanceAppointment
    template_name = 'member/grievance/my_appointments.html'
    context_object_name = 'grievance_appointments'
    
    def get_queryset(self):
        # Attempt to get the household of the currently logged-in user
        try:
            self.household = Household.objects.get(owner_name=self.request.user)
        except Household.DoesNotExist:
            # If no household exists, return an empty queryset
            self.household = None
            return GrievanceAppointment.objects.none()

        queryset = super().get_queryset().filter(household=self.household)

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(appointment_type__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        context['no_household'] = self.household is None
        
         # Add pagination
        grievance_appointments = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(grievance_appointments, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['grievance_appointments'] = page_obj

        return context

@login_required
def make_appointment(request, username):
    user = request.user
    try:
        household = Household.objects.get(owner_name=user)
    except Household.DoesNotExist:
        # Handle the case where the user has no associated household
        messages.error(request, "You do not have an associated household.")
        return redirect('add_household', username=username)  # Redirect to a page to create a household

    is_owner = household.owner_name == user if household else False
    grievanceappointments = household.grievance_appointments.all() if household else []

    if request.method == 'POST':
        form = GrievanceForm(request.POST, request.FILES)
        if form.is_valid():
            grievance_appointment = form.save(commit=False)
            grievance_appointment.household = household
            grievance_appointment.save()

            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A new appointment has been created by {request.user.fname} {request.user.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            messages.success(request, 'Appointment created successfully!')
            return redirect('make_appointment', username=username)
    else:
        form = GrievanceForm()

    return render(request, 'member/grievance/make_appointment.html', {
        'form': form,
        'user': user,
        'household': household,
        'grievanceappointments': grievanceappointments,
        'is_owner': is_owner,
    })

@login_required
def update_appointment(request, username, request_id):
    grievance = get_object_or_404(GrievanceAppointment, id=request_id)
    if request.method == 'POST':
        form = GrievanceForm(request.POST, request.FILES, instance=grievance)
        if form.is_valid():
            form.save()

            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"The appointment #{grievance.id} has been updated by {request.user.fname} {request.user.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            messages.success(request, 'Appointment updated successfully!')
            return redirect('update_appointment', username=username, request_id=request_id)
    else:
        form = GrievanceForm(instance=grievance, initial={'image': grievance.image})
    return render(request, 'member/grievance/update_appointment.html', {'form': form, 'grievance': grievance})

@login_required
def cancel_appointment(request, username, request_id):
    grievance = get_object_or_404(GrievanceAppointment, id=request_id)
    if request.method == 'POST':
        grievance.status = 'Canceled'  # Or your equivalent status
        grievance.save()

        # Create a notification for all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The appointment #{grievance.id} has been canceled by {request.user.fname} {request.user.lname}.",
                created_at=timezone.now()
            )
            notification.save()

        return redirect('my_appointment', username=username)
    else:
        # If it's a GET request, show the confirmation page
        return render(request, 'member/grievance/cancel_confirmation.html', {'grievance': grievance})

#member_views_profile
@login_required
def member_profile_info(request, username):
    user = request.user
    return render(request, 'member/profile/profile_info.html', {
        'user': user
    })

@login_required
def member_update_profile(request, username):
    user = User.objects.get(username=username) 

    if request.method == 'POST':
        form = MemberChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

            # Send notifications to all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"The profile of member {user.fname} {user.lname} has been updated.",
                    created_at=timezone.now()
                )
                notification.save()

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('member_profile_info', username=user.username)  # Ensure this view and URL are correctly configured
    else:
        form = MemberChangeForm(instance=user)

    return render(request, 'member/profile/profile_update.html', {'form': form})

@login_required
def member_delete_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()

        # Send notifications to all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The profile of member {user.fname} {user.lname} has been deleted.",
                created_at=timezone.now()
            )
            notification.save()

        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    else:
        messages.error(request, "Invalid request.")
        return redirect('member_profile_info', username=request.user.username)

#member_views_notifications
class MemberNotificationsView(View):
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(recipient=request.user).all()

        return render(request, 'member/sidebar.html', {
            'notifications': notifications
        })

#member_views_calendar
def eventscalendar(request, username, year=None, month=None): 
    today = date.today()

    # Check if a month is selected from the input form
    selected_month_str = request.GET.get('selected_month')
    if selected_month_str:
        # Parse the selected month (format YYYY-MM) to set year and month
        selected_date = datetime.strptime(selected_month_str, "%Y-%m")
        year = selected_date.year
        month = selected_date.month
    elif year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    # The rest of the logic remains the same as before.
    month_calendar = get_month_calendar(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    current_month = date(year, month, 1)
    prev_month_name = (date(year, prev_month, 1)).strftime('%B')
    next_month_name = (date(year, next_month, 1)).strftime('%B')

    context = {
        'calendar': month_calendar,
        'year': year,
        'month': current_month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month_name': prev_month_name,
        'next_month_name': next_month_name,
    }

    return render(request, 'member/events/calendar.html', context)

#officer_views_dashboard
@login_required
def officer_landing_page(request, username):
    total_households = Household.objects.count()
    total_residents = Resident.objects.count()
    pending_reservations = Reservation.objects.filter(status='Pending').count()
    pending_requests = ServiceRequest.objects.filter(status='Submitted').count()
    pending_appointments = GrievanceAppointment.objects.filter(status='Pending').count()
    overdue_count = Billing.objects.filter(status='Overdue').count()
    total_users = User.objects.filter(is_superuser=False).count()

    # For graphs:
    # Fetch confirmed reservations grouped by amenity
    amenity_usage = Reservation.objects.filter(status='Confirmed').values('amenities').annotate(count=models.Count('amenities'))

    # Demographics
    sex_demographics = Resident.objects.values('gender').annotate(total=Count('gender'))
    
    # Calculate age demographics (for example, you can create ranges)
    today = date.today()
    age_ranges = [
        ('0-17', 0, 17),
        ('18-24', 18, 24),
        ('25-34', 25, 34),
        ('35-44', 35, 44),
        ('45-54', 45, 54),
        ('55-64', 55, 64),
        ('65+', 65, 100)
    ]
    age_demographics = []
    for label, min_age, max_age in age_ranges:
        count = Resident.objects.filter(birthdate__year__gte=today.year - max_age).filter(birthdate__year__lt=today.year - min_age).count()
        age_demographics.append({'age_range': label, 'total': count})

    home_tenure_demographics = Household.objects.values('home_tenure').annotate(total=Count('home_tenure'))
    land_tenure_demographics = Household.objects.values('land_tenure').annotate(total=Count('land_tenure'))

    # Initialize a counter for vehicle types
    vehicle_count = Counter()

    # Iterate over all households and count each vehicle type
    households = Household.objects.all()
    for household in households:
        if household.vehicles_owned:
            # Split the vehicles owned and count them
            vehicles = household.vehicles_owned.split(', ')
            vehicle_count.update(vehicles)

    # Prepare the vehicle demographics as a list of dictionaries
    vehicle_demographics = [{'vehicles_owned': vehicle, 'total': count} for vehicle, count in vehicle_count.items()]
    # Count entries for the chart
    reservation_count = Reservation.objects.count()
    appointment_count = GrievanceAppointment.objects.count()
    request_count = ServiceRequest.objects.count()
    
    context = {
        'total_households': total_households,
        'total_residents': total_residents,
        'pending_reservations': pending_reservations,
        'pending_requests': pending_requests,
        'pending_appointments': pending_appointments,
        'overdue_count': overdue_count,
        'total_users': total_users,
        'amenity_usage': list(amenity_usage),
        'sex_demographics': list(sex_demographics),
        'age_demographics': age_demographics,
        'home_tenure_demographics': list(home_tenure_demographics),
        'land_tenure_demographics': list(land_tenure_demographics),
        'vehicle_demographics': vehicle_demographics,
        'reservation_count': reservation_count,
        'appointment_count': appointment_count,
        'request_count': request_count
    }

    return render(request, 'officer/officer_dashboard.html', context)

@login_required
def news_feed(request, username):
    # Retrieve newsfeeds and announcements
    newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    announcements = Announcement.objects.all().order_by('-date', '-time')
    
    # Paginate newsfeeds (example: 5 per page)
    paginator_newsfeeds = Paginator(newsfeeds, 2)  # Show 5 newsfeeds per page
    page_number_newsfeeds = request.GET.get('page_newsfeeds')  # Get the current page number for newsfeeds
    page_obj_newsfeeds = paginator_newsfeeds.get_page(page_number_newsfeeds)  # Retrieve the page object for newsfeeds

    # Paginate announcements (example: 3 per page)
    paginator_announcements = Paginator(announcements, 1)  # Show 3 announcements per page
    page_number_announcements = request.GET.get('page_announcements')  # Get the current page number for announcements
    page_obj_announcements = paginator_announcements.get_page(page_number_announcements)  # Retrieve the page object for announcements

    # Context for the template
    context = {
        'newsfeeds': page_obj_newsfeeds,  # Use the paginated page object for newsfeeds
        'announcements': page_obj_announcements,  # Use the paginated page object for announcements
        'page_obj_newsfeeds': page_obj_newsfeeds,  # Optional: explicitly pass page_obj_newsfeeds for pagination controls
        'page_obj_announcements': page_obj_announcements,  # Optional: explicitly pass page_obj_announcements for pagination controls
    }

    # Render the template with the context
    return render(request, 'officer/newsfeed/news_list.html', context)
    
@login_required
def news_single(request, username, pk):
    newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    return render(request, 'officer/newsfeed/news_article.html', {'newsfeeds': newsfeeds, 'newsfeed': newsfeed})

@login_required
def add_news(request, username):
    if request.method == "POST":
        form = NewsfeedForm(request.POST, request.FILES)  # Add request.FILES to handle image files
        if form.is_valid():
            newsfeed = form.save(commit=False)
            newsfeed.written_by = request.user  # Correctly assign the current user
            newsfeed.save()

            # Send notifications to all officers except the one who wrote the news article
            officers = User.objects.filter(is_officer=True).exclude(id=request.user.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A new news article has been posted by {request.user.fname} {request.user.lname}: {newsfeed.title}",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"A new news article has been posted: {newsfeed.title}",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('news_feed', username=username)
    else:
        form = NewsfeedForm()

    return render(request, 'officer/newsfeed/add_edit_news.html', {'form': form})

@login_required
def delete_news(request, username, pk):
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    if request.method == 'POST':
        newsfeed.delete()
        return redirect('news_feed', username=username)
    return redirect('news_feed', username=username)

@login_required
def edit_news(request, username, pk):
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    if request.method == "POST":
        form = NewsfeedForm(request.POST, request.FILES, instance=newsfeed)  # Ensure to include request.FILES for image handling
        if form.is_valid():
            # Store the officer who is editing the news article
            editing_officer = request.user
            
            # Save the updated newsfeed
            form.save()
            
            # Send notifications to all officers except the one who edited the news article
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A news article titled '{newsfeed.title}' has been updated by {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"A news article titled '{newsfeed.title}' has been updated.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('news_feed', username=username)
    else:
        form = NewsfeedForm(instance=newsfeed)  # Correctly use NewsForm with the news instance

    return render(request, 'officer/newsfeed/add_edit_news.html', {'form': form, 'newsfeed': newsfeed})

#officer_views_announcement
@login_required
def create_announcement(request, username):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            # Store the officer who is creating the announcement
            creating_officer = request.user
            
            # Save the new announcement
            announcement = form.save()

            # Send notifications to all officers except the one who updated the announcement
            officers = User.objects.filter(is_officer=True).exclude(id=creating_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"New announcement: {announcement.what} has been created by {creating_officer.fname} {creating_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"New announcement: {announcement.what}",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('news_feed', username=username)
    else:
        form = AnnouncementForm()
    return render(request, 'officer/newsfeed/announcement_form.html', {'form': form})

@login_required
def update_announcement(request, username, pk):
    announcement = Announcement.objects.get(pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            # Store the officer who is updating the announcement
            updating_officer = request.user
            
            # Save the updated announcement
            form.save()

            # Send notifications to all officers except the one who updated the announcement
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"Announcement: '{announcement.what}' has been updated by {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"Announcement: '{announcement.what}' has been updated.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('news_feed', username=username)
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'officer/newsfeed/announcement_form.html', {'form': form, 'announcement': announcement})

@login_required   
def delete_announcement(request, username, pk):
    announcement = get_object_or_404(Announcement, pk=pk)  # Adjust as necessary based on your Note model structure
    if request.method == 'POST':
        announcement.delete()
        return redirect('news_feed', username=username)  # Redirect back to the landing page after deletion
    return redirect('news_feed', username=username)

#officer_views_household
class HouseholdListView(ListView):
    model = Household
    template_name = 'officer/household/household_list.html'
    context_object_name = 'households'

    def get_queryset(self):
        queryset = Household.objects.prefetch_related('billings').annotate(
            number_of_residents=Count('residents')
        )

        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(owner_name__fname__icontains=search_query) |
                Q(owner_name__lname__icontains=search_query) |
                Q(block__icontains=search_query) |
                Q(street__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'owner_name__fname')
        direction = self.request.GET.get('direction', 'asc')

        # Exclude overall_billing_status from the queryset sort
        if sort_by != 'overall_billing_status':
            order_by = sort_by if direction == 'asc' else f'-{sort_by}'
            queryset = queryset.order_by(order_by)

        return queryset

    def post(self, request, *args, **kwargs):
        billing_month = request.POST.get("billing_month")
        amount = request.POST.get("amount")
        
        # Modify billing_month to add the day part
        billing_month += "-01"  # Convert from YYYY-MM to YYYY-MM-DD format

        try:
            # Get the officer who added the billing
            adding_officer = request.user

            # Create billing for each household
            for household in Household.objects.all():
                Billing.objects.create(
                    household=household,
                    billing_month=billing_month,
                    amount=amount,
                    status="Unpaid",
                )
            # Send notifications to all users (members and officers) except the officer who added the billing
            users = User.objects.exclude(id=adding_officer.id)  # Exclude the officer who added the billing
            for user in users:
                # Create a notification for each user
                Notification.objects.create(
                    recipient=user,
                    content=f"New billing for {billing_month} has been added by Officer {adding_officer.fname} {adding_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Monthly billing added for all households.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            print("Error while saving billing:", e)  # Debugging output

        return redirect(reverse('household_list', kwargs={'username': self.kwargs['username']}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filtered and sorted queryset
        households_queryset = self.get_queryset()

        # Add pagination
        paginator = Paginator(households_queryset, 6)  # Show 6 households per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Calculate the overall billing status for each household on the current page
        for household in page_obj:
            billing_statuses = household.billings.values_list('status', flat=True)
            if not billing_statuses:
                household.overall_billing_status = 'Empty'
            elif 'Overdue' in billing_statuses:
                household.overall_billing_status = 'Overdue'
            elif 'Unpaid' in billing_statuses:
                household.overall_billing_status = 'Unpaid'
            else:
                household.overall_billing_status = 'Updated'

        # Handle sorting by overall billing status
        sort_by = self.request.GET.get('sort', 'owner_name__fname')
        direction = self.request.GET.get('direction', 'asc')
        if sort_by == 'overall_billing_status':
            page_obj.object_list = sorted(
                page_obj.object_list,
                key=lambda h: h.overall_billing_status,
                reverse=(direction == 'desc')
            )

        # Add context for pagination and sorting
        context['households'] = page_obj
        context['sort_by'] = sort_by
        context['direction'] = direction
        context['search_query'] = self.request.GET.get('search', '')

        return context

class HouseholdDetailView(View):
    def get(self, request, username, pk):
        user = request.user
        household = get_object_or_404(Household, pk=pk)

        # Get all residents that belong to the household
        residents = Resident.objects.filter(household=household)

        # Get all billings related to the household
        billings = Billing.objects.filter(household=household).order_by('-billing_month')

        # Prepare the context with household, residents, and billing information
        context = {
            'household': household,
            'residents': residents,
            'billings': billings,
            'fields': [
                {'display_name': 'First Name'},
                {'display_name': 'Relation to Head'},
                {'display_name': 'Email'},
                {'display_name': 'Birth Date'},
                {'display_name': 'Contact Number'},
                {'display_name': 'Actions'},
            ]
        }

        return render(request, 'officer/household/view_household.html', context)

class EditHousehold(View):
    def get(self, request, username, pk):
        household = get_object_or_404(Household, pk=pk)
        form = HouseholdForm(instance=household)
        return render(request, 'officer/household/edithousehold.html', {'form': form, 'household': household})

    def post(self, request, username, pk):
        household = get_object_or_404(Household, pk=pk)
        form = HouseholdForm(request.POST, instance=household)
        
        if form.is_valid():
            # Save the household form
            household = form.save()

            # Get the officer who is editing the household
            editing_officer = request.user
            
            # Get the member associated with the household
            member = household.owner_name  # Assuming 'owner_name' is the user who is the member

            # Create a notification for the member (who owns the household)
            notification = Notification.objects.create(
                recipient=member,  # Send notification to the member
                content=f"Your household details have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

            # Send notifications to all officers except the one who edited the household
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to the officer
                    content=f"The details of household '{household.owner_name}' have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Redirect to the view page for the updated household
            messages.success(request, "Household updated successfully!")
            return redirect('view_household', username=username, pk=pk)
        
        return render(request, 'officer/household/edithousehold.html', {'form': form, 'household': household})

#officer_views_resident
class ViewResidentInfo(View):
    def get(self, request, username, pk, resident_id):
        household = get_object_or_404(Household, pk=pk)
        resident = get_object_or_404(Resident, id=resident_id)
        return render(request, 'officer/household/view_resident_info.html', {'resident': resident, 'household': household})

class EditResident(View):
    def get(self, request, username, pk, resident_id):
        household = get_object_or_404(Household, pk=pk)
        resident = get_object_or_404(Resident, id=resident_id)
        form = ResidentForm(instance=resident)
        return render(request, 'officer/household/editresident.html', {'form': form, 'resident': resident, 'household': household})

    def post(self, request, username, pk, resident_id):
        household = get_object_or_404(Household, pk=pk)
        resident = get_object_or_404(Resident, id=resident_id)
        form = ResidentForm(request.POST, instance=resident)
        
        if form.is_valid():
            # Save the form
            resident = form.save()

            # Get the officer who made the edit
            editing_officer = request.user

            member = household.owner_name

            # Send a notification to the household (connected resident)
            notification = Notification.objects.create(
                recipient=member,  # Assuming the notification relates to the household
                content=f"The details for resident {resident.first_name} {resident.last_name} have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

            # Send notifications to all other officers
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,
                    content=f"Resident details for {resident.first_name} {resident.last_name} have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('view_resident_info', username=username, pk=household.id, resident_id=resident.id)
        else:
            form = ResidentForm(instance=resident)

        return render(request, 'officer/household/editresident.html', {'form': form, 'resident': resident, 'household': household})

@login_required
def dlt_resident(request, username, pk, resident_id):
    household = get_object_or_404(Household, pk=pk)
    resident = get_object_or_404(Resident, id=resident_id)

    if request.method == 'POST':
        # Get the officer who is performing the deletion
        deleting_officer = request.user

        member = household.owner_name
        # Send a notification to the household (connected resident)
        notification = Notification.objects.create(
            recipient=member,  # Notification is related to the household
            content=f"The details for resident {resident.first_name} {resident.last_name} have been removed from the household by Officer {deleting_officer.fname} {deleting_officer.lname}.",
            created_at=timezone.now()
        )
        notification.save()

        # Send notifications to all other officers
        officers = User.objects.filter(is_officer=True).exclude(id=deleting_officer.id)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,
                content=f"The details for resident {resident.first_name} {resident.last_name} have been removed from household {household.owner_name} by Officer {deleting_officer.fname} {deleting_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

        # Delete the resident
        resident.delete()

        messages.success(request, "Resident deleted successfully.")
        return redirect('view_household', username=username, pk=pk)
    else:
        messages.error(request, "Invalid request method.")
    return redirect('view_household', username=username, pk=pk)

#officer_views_billing
class edit_billing_status(View):
    def get(self, request, username, pk, billing_id):
        household = get_object_or_404(Household, pk=pk)
        billing = get_object_or_404(Billing, id=billing_id)
        form = BillingStatusForm(instance=billing)
        return render(request, 'officer/household/edit_billing.html', {'form': form, 'billings': billing, 'household': household})

    def post(self, request, username, pk, billing_id):
        household = get_object_or_404(Household, pk=pk)
        billing = get_object_or_404(Billing, id=billing_id)
        form = BillingStatusForm(request.POST, instance=billing)

        if form.is_valid():
            # Get the officer who is making the change
            editing_officer = request.user

            # Save the form (which updates the billing status)
            billing = form.save()

            # Create a notification for the household owner (member)
            member = household.owner_name  # The member (household owner) who will receive the notification
            notification = Notification.objects.create(
                recipient=member,  # Send to the household owner (member)
                content=f"Your billing status for household {household.owner_name} has been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

            # Send notifications to other officers (excluding the officer who edited)
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,
                    content=f"The billing status for household {household.owner_name} has been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Redirect to the household view page after updating the billing status
            return redirect('view_household', username=username, pk=pk)

        return render(request, 'officer/household/edit_billing.html', {'form': form, 'billings': billing, 'household': household})

#officer_views_reservation
class ReservationListView(ListView):
    model = Reservation
    template_name = 'officer/reservation/reservation_list.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(household__owner_name__fname__icontains=search_query) |
                Q(household__owner_name__lname__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(amenities__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

         # Add pagination
        reservations = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(reservations, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['reservations'] = page_obj

        return context

@login_required
def update_reservation_status(request, username, reservation_id):
    # Fetch the reservation instance or return a 404 error if not found
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        form = ReservationStatusForm(request.POST, instance=reservation)
        if form.is_valid():
            # Update the reservation status and set the officer flag
            updated_reservation = form.save(commit=False)
            updated_reservation.status_changed_by_officer = True
            updated_reservation.save()

            # Get the officer who updated the reservation
            updating_officer = request.user

            # Send a notification to the member who made the reservation (household owner)
            member = reservation.household.owner_name  # Adjust this if your model has a different relationship
            Notification.objects.create(
                recipient=member,  # Assuming you have a way to get the member from the reservation
                content=f"Your reservation for {reservation.amenities} has been {reservation.status} by Officer {updating_officer.fname} {updating_officer.lname}.",
                created_at=timezone.now()
            )

            # Send notifications to all officers (except the one who updated the reservation)
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"Reservation of {member} for {reservation.amenities} has been {reservation.status} by Officer {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Reservation status updated successfully!")
            return redirect('reservation_list', username=request.user.username)
    else:
        form = ReservationStatusForm(instance=reservation)

    return render(request, 'officer/reservation/update_reservation.html', {
        'form': form,
        'reservation': reservation,
    })

#officer_views_request
class RequestListView(ListView):
    model = ServiceRequest
    template_name = 'officer/services/request_list.html'
    context_object_name = 'servicerequests'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(household__owner_name__fname__icontains=search_query) |
                Q(household__owner_name__lname__icontains=search_query) |
                Q(service_type__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(updated_at__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        servicerequests = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(servicerequests, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['servicerequests'] = page_obj

        return context

class ViewRequest(View):
    def get(self, request, username, request_id):
        servicerequest = get_object_or_404(ServiceRequest, id=request_id)
        return render(request, 'officer/services/view_request.html', {'servicerequest': servicerequest})

@login_required
def update_request_status(request, username, servicerequest_id):
    # Fetch the service request instance or return a 404 error if not found
    servicerequest = get_object_or_404(ServiceRequest, id=servicerequest_id)

    if request.method == 'POST':
        form = ServiceRequestStatusForm(request.POST, instance=servicerequest)
        if form.is_valid():
            # Update the service request status and set the officer flag
            updated_request = form.save(commit=False)
            updated_request.status_changed_by_officer = True
            updated_request.save()

            # Get the officer who updated the service request
            updating_officer = request.user

            # Send a notification to the member who made the service request (household owner)
            member = servicerequest.household.owner_name  # Adjust this if your model has a different relationship
            Notification.objects.create(
                recipient=member,  # Assuming you have a way to get the member from the service request
                content=f"Your {servicerequest.service_type} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                created_at=timezone.now()
            )

            # Send notifications to all officers (except the one who updated the service request)
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"{servicerequest.service_type} of {member} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Service request status updated successfully!")
            return redirect('request_list', username=request.user.username)
    else:
        form = ServiceRequestStatusForm(instance=servicerequest)

    return render(request, 'officer/services/update_request.html', {
        'form': form,
        'servicerequest': servicerequest,
    })

#officer_views_appointment
class AppointmentListView(ListView):
    model = GrievanceAppointment
    template_name = 'officer/grievance/appointment_list.html'
    context_object_name = 'grievance_appointments'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(household__owner_name__fname__icontains=search_query) |
                Q(household__owner_name__lname__icontains=search_query) |
                Q(appointment_type__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        grievance_appointments = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(grievance_appointments, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['grievance_appointments'] = page_obj

        return context

class ViewAppointment(View):
    def get(self, request, username, request_id):
        grievanceappointment = get_object_or_404(GrievanceAppointment, id=request_id)
        return render(request, 'officer/grievance/view_appointment.html', {'grievanceappointment': grievanceappointment})

@login_required
def update_appointment_status(request, username, grievanceappointment_id):
    # Fetch the grievance appointment instance or return a 404 error if not found
    grievance_appointment = get_object_or_404(GrievanceAppointment, id=grievanceappointment_id)

    if request.method == 'POST':
        form = GrievanceStatusForm(request.POST, instance=grievance_appointment)
        if form.is_valid():
            # Update the grievance appointment status and set the officer flag
            updated_appointment = form.save(commit=False)
            updated_appointment.status_changed_by_officer = True
            updated_appointment.save()

            # Get the officer who updated the grievance appointment
            updating_officer = request.user

            # Send a notification to the member who made the grievance appointment (household owner)
            member = grievance_appointment.household.owner_name  # Adjust this if your model has a different relationship
            Notification.objects.create(
                recipient=member,  # Assuming you have a way to get the member from the grievance appointment
                content=f"Your appointment for {grievance_appointment.appointment_type} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                created_at=timezone.now()
            )

            # Send notifications to all officers (except the one who updated the grievance appointment)
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"Appointment of {member} for {grievance_appointment.appointment_type} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Grievance appointment status updated successfully!")
            return redirect('appointment_list', username=request.user.username)
    else:
        form = GrievanceStatusForm(instance=grievance_appointment)

    return render(request, 'officer/grievance/update_appointment.html', {
        'form': form,
        'grievance_appointment': grievance_appointment,
    })

# Officer User Management View
def manage_users(request, username):
    if not request.user.is_officer:
        return redirect('dashboard')  # Only officers can access

    # Get search query from request
    search_query = request.GET.get('search', '')

    # Fetch all users except superadmins (is_superuser=False)
    users = User.objects.filter(is_superuser=False)

    # If there's a search query, filter the users accordingly
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(fname__icontains=search_query) |
            Q(lname__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Get sorting criteria from query parameters
    sort_by = request.GET.get('sort', 'date_joined')  # Default sort by `date_joined`
    direction = request.GET.get('direction', 'desc')  # Default direction is descending

    # Sort users based on the selected column and direction
    if sort_by == 'role':
        # Custom sorting for role (is_officer, is_member)
        users = sorted(users, key=lambda u: (u.is_officer, u.is_member), reverse=(direction == 'desc'))
    elif sort_by == 'status':
        users = users.order_by('is_active' if direction == 'asc' else '-is_active')
    elif sort_by == 'date_joined':
        users = users.order_by('date_joined' if direction == 'asc' else '-date_joined')
    else:
        users = users.order_by(sort_by if direction == 'asc' else f'-{sort_by}')

    # Paginate the results
    paginator = Paginator(users, 6)  # Show 6 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare context for the template
    context = {
        'users': page_obj,
        'sort_by': sort_by,
        'direction': direction,
        'search_query': search_query,
    }

    return render(request, 'officer/usermgt/manage_users.html', context)

def toggle_user_activation(request, username, user_id):
    user = User.objects.get(id=user_id)

    # Check if the user making the request is an officer
    if request.user.is_officer:
        # Toggle the user's active status
        previous_status = user.is_active
        user.is_active = not user.is_active
        user.save()

        # Create a notification for the user whose account was toggled
        action = "activated" if user.is_active else "deactivated"
        Notification.objects.create(
            recipient=user,
            content=f"Your account has been {action} by Officer {request.user.fname} {request.user.lname}.",
            created_at=timezone.now()
        )

        # Optionally, add a success message to the request
        messages.success(request, f"User account has been {action} successfully.")

    return redirect('manage_users', username=user.username)

@login_required
def delete_user(request, username, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        # Save the deleted user's name for notification content
        deleted_user_name = f"{user.fname} {user.lname}"
        
        # Delete the user
        user.delete()

        # Notify all officers except the one performing the deletion
        officers = User.objects.filter(is_officer=True).exclude(id=request.user.id)
        for officer in officers:
            Notification.objects.create(
                recipient=officer,
                content=f"Officer {request.user.fname} {request.user.lname} deleted the account of {deleted_user_name}.",
                created_at=timezone.now()
            )

        # Redirect to manage users page
        return redirect('manage_users', username=username)

    return redirect('manage_users', username=username)

#officer_views_profile
@login_required
def officer_profile_info(request, username):
    user = request.user
    return render(request, 'officer/profile/profile_info.html', {
        'user': user
    })

@login_required
def officer_update_profile(request, username):
    user = User.objects.get(username=username)
    assigned_roles = Officer.objects.exclude(user=user).values_list('officer_position', flat=True)
    available_roles_choices = [choice for choice in Officer.ROLES_CHOICES if choice[0] not in assigned_roles]

    if request.method == 'POST':
        form = OfficerChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()  # Ensure the form is valid before saving
            return redirect('officer_profile_info', username=user.username)
        else:
            print(form.errors)  # Debugging: check form errors
    else:
        form = OfficerChangeForm(instance=user)

    return render(request, 'officer/profile/profile_update.html', {
        'form': form,
        'roles_choices': available_roles_choices
    })

@login_required
def officer_delete_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    else:
        messages.error(request, "Invalid request.")
        return redirect('officer_delete_profile', username=request.user.username)

#officer_views_calendar
def events_calendar(request, username, year=None, month=None): 
    today = date.today()

    # Check if a month is selected from the input form
    selected_month_str = request.GET.get('selected_month')
    if selected_month_str:
        # Parse the selected month (format YYYY-MM) to set year and month
        selected_date = datetime.strptime(selected_month_str, "%Y-%m")
        year = selected_date.year
        month = selected_date.month
    elif year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    # The rest of the logic remains the same as before.
    month_calendar = get_month_calendar(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    current_month = date(year, month, 1)
    prev_month_name = (date(year, prev_month, 1)).strftime('%B')
    next_month_name = (date(year, next_month, 1)).strftime('%B')

    context = {
        'calendar': month_calendar,
        'year': year,
        'month': current_month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month_name': prev_month_name,
        'next_month_name': next_month_name,
    }

    return render(request, 'officer/events/calendar.html', context)

#officer_views_notif
class OfficerNotificationsView(View):
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(recipient=request.user).all()

        return render(request, 'officer/officer_sidebar.html', {
            'notifications': notifications
        })

def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, recipient=request.user)
    notification.read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER'))

def create_payment_link(request, username, billing_id):
    # Fetch the billing object using the billing_id
    billing = get_object_or_404(Billing, id=billing_id)

    url = "https://api.paymongo.com/v1/links"
    payload = {
        "data": {
            "attributes": {
                "amount": int(billing.amount * 100),  # Convert to centavos and ensure it's an integer
                "description": f"Payment for {billing.billing_month.strftime('%B %Y')} dues",
                "remarks": "GCASH Payment",
            }
        }
    }
    secret_key = settings.PAYMONGO_SECRET_KEY
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {base64.b64encode(secret_key.encode()).decode()}",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        response_data = response.json()

        if response.status_code == 200 and "data" in response_data:
            link_status = response_data["data"]["attributes"]["status"]
            if link_status == "unpaid":
                # Update billing status
                billing.status = "Paid"
                billing.save()

                # Send notification to all officers except the one who triggered the action
                officers = User.objects.filter(is_officer=True).exclude(id=request.user.id)
                for officer in officers:
                    Notification.objects.create(
                        recipient=officer,
                        content=f"A payment link for {billing.billing_month.strftime('%B %Y')} has been created and marked as 'Paid'.",
                        created_at=timezone.now()
                    )
                # Extract the checkout URL
                checkout_url = response_data["data"]["attributes"]["checkout_url"]
                return JsonResponse({"checkout_url": checkout_url}, status=200)
            else:
                return JsonResponse({"error": "Payment link creation failed due to unexpected status."}, status=500)
        else:
            return JsonResponse({"error": "Payment link creation failed."}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def payment_status(request, billing_id):
    billing = get_object_or_404(Billing, id=billing_id)

    # You can use PayMongo's API to fetch payment details (e.g., using the reference number)
    payment_status = request.GET.get('status', 'failed')  # Assume PayMongo appends the status

    # Update the billing status accordingly
    if payment_status == 'success':
        billing.status = "Paid"
        billing.save()
        message = "Payment was successful."
    else:
        message = "Payment failed or was canceled."

    # Render a template showing the payment status
    return render(request, 'payment_status.html', {
        'billing': billing,
        'message': message,
        'previous_page': request.META.get('HTTP_REFERER', '/'),  # Optionally, pass the previous page URL
    })
