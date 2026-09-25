import io
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserProfile, Train, Coach, LinenItem, LinenAssignment, PassengerPNR,
    LinenLifecycleEvent, CollectionSession, CollectionScan, CoachHandOff
)
from .forms import LinenRegistrationForm, LinenAssignmentForm, StartCollectionForm
from .services import (
    generate_qr_data_url, register_linen_item, assign_linen_item,
    validate_scan, mark_linen_returned, record_scan_attempt,
    laundry_receive_item, laundry_start_wash, laundry_ready_reissue,
    get_analytics_data, lookup_pnr, get_or_create_coach_handoff,
    get_next_linen_code, get_coach_passengers, get_deboarding_passengers
)
import qrcode
from PIL import Image, ImageDraw


# ============================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================================

def role_required(*roles):
    """
    Strict server-side RBAC decorator for Django views.
    Roles: 'SUPERVISOR', 'ATTENDANT', 'LAUNDRY'
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            current_role = profile.get_normalized_role() if profile else ('SUPERVISOR' if request.user.is_staff else None)

            normalized_targets = set()
            for r in roles:
                r_upper = r.upper()
                if r_upper in ['ADMIN', 'SUPERVISOR']:
                    normalized_targets.add('SUPERVISOR')
                elif r_upper in ['ATTENDER', 'ATTENDANT']:
                    normalized_targets.add('ATTENDANT')
                elif r_upper == 'LAUNDRY':
                    normalized_targets.add('LAUNDRY')
                else:
                    normalized_targets.add(r_upper)

            if current_role not in normalized_targets:
                messages.warning(
                    request,
                    f"Access restricted: {current_role or 'Unassigned'} cannot access this workspace."
                )
                return redirect(role_home(request.user))
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def role_home(user):
    """
    Returns the designated primary landing URL for a given user role.
    """
    if not user or not user.is_authenticated:
        return 'login'
    profile = getattr(user, 'profile', None)
    role = profile.get_normalized_role() if profile else ('SUPERVISOR' if user.is_staff else None)
    return {
        'ATTENDANT': 'attendant_hub',
        'LAUNDRY': 'laundry_register',
        'SUPERVISOR': 'supervisor_handoff',
    }.get(role, 'login')


def root_dispatcher(request):
    """
    Dispatches root URL to either authenticated home or sign-in page.
    """
    if request.user.is_authenticated:
        return redirect(role_home(request.user))
    return redirect('login')


# ============================================================
# 4.1 SIGN IN
# ============================================================

def demo_login(request):
    """
    Screen 4.1: Sign In
    - Two fields: Employee ID, Password
    - Three equal-width role tiles: Attendant / Laundry / Supervisor
    - Universal theme toggle & language switch
    - Primary button: "Sign in"
    """
    if request.user.is_authenticated:
        return redirect(role_home(request.user))

    selected_role = request.GET.get('role', 'attendant').lower()

    if request.method == 'POST':
        role_selected = request.POST.get('role_choice', 'attendant').lower()
        emp_id = request.POST.get('employee_id', '').strip()
        pwd = request.POST.get('password', '').strip()

        # Handle 1-click or typed sign in
        username_map = {
            'attendant': 'attender',
            'attender': 'attender',
            'att-b2-8821': 'attender',
            'laundry': 'laundry',
            'lnd-stn-401': 'laundry',
            'supervisor': 'admin',
            'admin': 'admin',
            'emp-adm-01': 'admin',
        }

        # Resolve target user directly from badge_number or username
        matched_user = None
        target_username = None
        if emp_id:
            cleaned_id = emp_id.strip()
            # Direct match by username or badge_number
            u_obj = User.objects.filter(
                Q(profile__badge_number__iexact=cleaned_id) |
                Q(username__iexact=cleaned_id)
            ).first()
            if u_obj:
                matched_user = u_obj
                target_username = u_obj.username
            else:
                target_username = username_map.get(cleaned_id.lower(), cleaned_id)
        else:
            target_username = username_map.get(role_selected, 'attender')

        # Try authenticating with supplied or demo password candidates
        user = None
        passwords_to_try = [pwd] if pwd else []
        passwords_to_try.extend(['attender123', 'admin123', 'laundry123', f"{target_username}123"])

        for p_cand in passwords_to_try:
            if not p_cand:
                continue
            user = authenticate(request, username=target_username, password=p_cand)
            if user:
                break

        if not user and matched_user:
            for p_cand in ['attender123', 'admin123', 'laundry123', f"{matched_user.username}123"]:
                user = authenticate(request, username=matched_user.username, password=p_cand)
                if user:
                    break

        if user:
            login(request, user)
            messages.success(request, f"Signed in successfully as {user.username}.")
            return redirect(role_home(user))
        else:
            messages.error(request, "Invalid Employee ID or Password. (Demo passwords: attender123, admin123, laundry123)")

    context = {
        'selected_role': selected_role,
    }
    return render(request, 'auth/login.html', context)


def demo_logout(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect('login')


# ============================================================
# 4. ATTENDANT APP SCREENS (Attendant role ONLY)
# ============================================================

@role_required('ATTENDANT')
def attendant_assignment(request):
    """
    Screen 4.2: Coach Assignment
    - Confirms a coach already assigned by the supervisor.
    """
    handoff = get_or_create_coach_handoff(request.user)
    passengers = get_coach_passengers(handoff.train, handoff.coach)

    if request.method == 'POST':
        # Attendant confirms shift
        handoff.status = 'CONFIRMED'
        handoff.save()

        # Ensure collection session is active for coach
        session, _ = CollectionSession.objects.get_or_create(
            attender=request.user,
            train=handoff.train,
            coach=handoff.coach,
            journey_date=timezone.now().date(),
            defaults={
                'expected_quantity': handoff.bedsheets_handed_over,
                'status': 'IN_PROGRESS'
            }
        )
        return redirect('attendant_hub')

    context = {
        'handoff': handoff,
        'passengers': passengers,
        'train_chars': list(handoff.train.train_number),
    }
    return render(request, 'attendant/coach_assignment.html', context)


@role_required('ATTENDANT')
def attendant_hub(request):
    """
    Screen 4.3: Choose Action (Hub screen & Profile Dashboard)
    - Automatically displays the employee's assigned coach and duty.
    - Displays passengers deboarding in the next 20 minutes for priority linen sweep & QR scan.
    - Displays the complete passenger list for that particular coach for issuing linen operations.
    """
    handoff = get_or_create_coach_handoff(request.user)
    passengers = get_coach_passengers(handoff.train, handoff.coach)
    deboarding_passengers = get_deboarding_passengers(handoff.train, handoff.coach)
    today = timezone.now().date()

    issued_today = LinenAssignment.objects.filter(
        train=handoff.train,
        coach=handoff.coach,
        journey_date=today
    ).count()

    if issued_today == 0:
        issued_today = 42
        collected_today = 38
    else:
        collected_today = LinenAssignment.objects.filter(
            train=handoff.train,
            coach=handoff.coach,
            assignment_status='RETURNED',
            journey_date=today
        ).count()

    available_linen = LinenItem.objects.filter(
        status__in=['REGISTERED', 'READY_FOR_REISSUE']
    ).order_by('-created_at')
    available_count = available_linen.count()
    bedsheet_count = available_linen.filter(linen_type='Bedsheet').count()
    blanket_count = available_linen.filter(linen_type='Blanket').count()
    towel_count = available_linen.filter(linen_type='Towel').count()
    pillow_count = available_linen.filter(linen_type='Pillow Cover').count()

    context = {
        'handoff': handoff,
        'passengers': passengers,
        'deboarding_passengers': deboarding_passengers,
        'deboarding_count': len(deboarding_passengers),
        'upcoming_station': 'Secunderabad Junction (SC)',
        'upcoming_eta_minutes': 18,
        'issued_today': issued_today,
        'collected_today': collected_today,
        'available_linen': available_linen[:15],
        'available_count': available_count,
        'bedsheet_count': bedsheet_count,
        'blanket_count': blanket_count,
        'towel_count': towel_count,
        'pillow_count': pillow_count,
    }
    return render(request, 'attendant/choose_action.html', context)


@role_required('ATTENDANT')
def attendant_roster(request):
    """
    Screen 4.3b: Passenger Roster Chart (Attendant Login)
    - Full reservation chart and passenger roster for the attendant's assigned coach.
    - Provides real-time search (by berth, name, or PNR), filter by status (All, Boarding now, Issued, Deboarding soon).
    - Displays berth number, type, passenger name, age/gender, masked PNR, origin/destination, and assigned linen items.
    """
    handoff = get_or_create_coach_handoff(request.user)
    passengers = get_coach_passengers(handoff.train, handoff.coach)
    deboarding_passengers = get_deboarding_passengers(handoff.train, handoff.coach)

    total_passengers = len(passengers)
    issued_count = sum(1 for p in passengers if p.get('status') == 'Issued' or p.get('has_issued_linen'))
    boarding_count = sum(1 for p in passengers if p.get('status') == 'Boarding now')
    deboarding_count = len(deboarding_passengers)

    context = {
        'handoff': handoff,
        'passengers': passengers,
        'deboarding_passengers': deboarding_passengers,
        'total_passengers': total_passengers,
        'issued_count': issued_count,
        'boarding_count': boarding_count,
        'deboarding_count': deboarding_count,
        'upcoming_station': 'Secunderabad Junction (SC)',
        'upcoming_eta_minutes': 18,
    }
    return render(request, 'attendant/roster.html', context)


@role_required('ATTENDANT')
def attendant_issue(request):
    """
    Screen 4.4: Issue Linen
    - Passenger list sorted by berth, PNR masked to last 4 digits.
    - Default view: Full-window passenger roster list (col-12) with one-tap action to issue linen.
    - Scan mode (?scan=1&passenger_id=N): Opens camera QR scanner and manual verification for selected passenger.
    """
    handoff = get_or_create_coach_handoff(request.user)
    passengers = get_coach_passengers(handoff.train, handoff.coach)
    code_from_url = request.GET.get('code', '').strip().upper()
    target_passenger_id = request.GET.get('passenger_id')
    scan_mode = (request.GET.get('scan') == '1') and bool(target_passenger_id)

    if not target_passenger_id:
        unissued = next((p for p in passengers if p.get('status') != 'Issued' and not p.get('has_issued_linen')), None)
        selected_passenger = unissued or (passengers[0] if passengers else None)
    else:
        selected_passenger = next(
            (p for p in passengers if str(p['id']) == target_passenger_id),
            passengers[0] if passengers else None
        )

    available_linen = LinenItem.objects.filter(
        status__in=['REGISTERED', 'READY_FOR_REISSUE']
    ).order_by('-created_at')
    available_count = available_linen.count()
    bedsheet_count = available_linen.filter(linen_type='Bedsheet').count()
    blanket_count = available_linen.filter(linen_type='Blanket').count()
    towel_count = available_linen.filter(linen_type='Towel').count()
    pillow_count = available_linen.filter(linen_type='Pillow Cover').count()

    context = {
        'handoff': handoff,
        'passengers': passengers,
        'available_linen': available_linen,
        'available_count': available_count,
        'bedsheet_count': bedsheet_count,
        'blanket_count': blanket_count,
        'towel_count': towel_count,
        'pillow_count': pillow_count,
        'sample_code': code_from_url or 'BS-2026-04825',
        'preselected_code': code_from_url,
        'scan_mode': scan_mode,
        'selected_passenger': selected_passenger,
    }
    return render(request, 'attendant/issue_linen.html', context)


@role_required('ATTENDANT')
def attendant_alert(request):
    """
    Screen 4.5: Board / Deboard Alert
    - Deboarding due soon: full-screen takeover — icon, "DEBOARDING SHORTLY" eyebrow,
      passenger count + destination + ETA ("2 passengers deboarding in next 20 mins at Secunderabad"),
      shows exact deboarding passengers list and one button "Start collecting".
    - Passenger boarding: a lighter, non-blocking card below a divider —
      "[N] passengers boarding — at the next station — issue linen when ready",
      routes back to Issue Linen.
    """
    handoff = get_or_create_coach_handoff(request.user)
    deboarding_passengers = get_deboarding_passengers(handoff.train, handoff.coach)
    context = {
        'handoff': handoff,
        'deboarding_passengers': deboarding_passengers,
        'deboarding_count': len(deboarding_passengers),
        'upcoming_station': 'Secunderabad Junction (SC)',
        'upcoming_eta_minutes': 18,
    }
    return render(request, 'attendant/alert.html', context)


@role_required('ATTENDANT')
def attendant_collect(request):
    """
    Screen 4.6: Collect Item
    - Full-width scan target with corner-bracket styling.
    - Manual-entry button always visible below it ("Enter linen ID manually").
    - After a scan: a confirmation card showing the scanned item's type, ID, and berth.
    - One button, labeled exactly: "Confirm". Do NOT auto-accept on scan.
    - Two-number tally below (Collected / Remaining) — plain numbers, not split-flap.
    """
    handoff = get_or_create_coach_handoff(request.user)
    deboarding_passengers = get_deboarding_passengers(handoff.train, handoff.coach)
    session, _ = CollectionSession.objects.get_or_create(
        attender=request.user,
        train=handoff.train,
        coach=handoff.coach,
        journey_date=timezone.now().date(),
        status='IN_PROGRESS',
        defaults={
            'expected_quantity': handoff.bedsheets_handed_over,
        }
    )

    collected_count = session.scanned_quantity
    expected_count = session.expected_quantity
    remaining_count = max(0, expected_count - collected_count)

    # Optional query params to pre-fill target from deboarding list
    target_code = request.GET.get('code', '')
    target_berth = request.GET.get('berth', '')
    if not target_code:
        target_code = deboarding_passengers[0]['primary_code'] if deboarding_passengers else 'BL-20561'

    context = {
        'handoff': handoff,
        'session': session,
        'collected_count': collected_count,
        'remaining_count': remaining_count,
        'demo_qr': target_code,
        'target_berth': target_berth,
        'deboarding_passengers': deboarding_passengers,
        'deboarding_count': len(deboarding_passengers),
    }
    return render(request, 'attendant/collect_item.html', context)



@role_required('ATTENDANT')
def attendant_end_report(request):
    """
    Screen 4.7: End-of-Coach Report (Optional)
    - Four color-coded numbers: Expected / Returned / Damaged / Missing.
    - Missing items listed with "last seen at [checkpoint], [time]" phrasing — factual, not accusatory.
    - One button: "Submit sweep report".
    """
    handoff = get_or_create_coach_handoff(request.user)
    missing_items = LinenItem.objects.filter(
        status__in=['UNACCOUNTED', 'INVESTIGATION_REQUIRED']
    ).prefetch_related('lifecycle_events')[:6]

    missing_reports = []
    for item in missing_items:
        cp = item.get_last_verified_checkpoint()
        missing_reports.append({
            'code': item.linen_code,
            'type': item.linen_type,
            'stage': cp.get('stage', 'Unknown'),
            'location': cp.get('location', 'Coach B2'),
            'time': timezone.localtime(cp.get('timestamp')).strftime('%H:%M, %d %b') if cp.get('timestamp') else 'Recent',
        })

    context = {
        'handoff': handoff,
        'expected': 100,
        'returned': 94,
        'damaged': 0,
        'missing': 6,
        'missing_reports': missing_reports,
    }
    return render(request, 'attendant/end_report.html', context)


# ============================================================
# 5. LAUNDRY APP SCREENS (Laundry role ONLY)
# ============================================================

@role_required('LAUNDRY')
def laundry_register(request):
    """
    Screen 5.1: Register New Linen (Manufacturer QR Code Intake)
    - Directly scan manufacturer QR codes attached to incoming linen items.
    - Category selector (Bedsheet / Blanket / Towel / Pillow Cover).
    - Status tile: "[N] items registered today" & total inventory count.
    - Live feed of recently registered manufacturer items in depot stock.
    """
    default_type = 'Bedsheet'
    today = timezone.now().date()
    today_count = LinenItem.objects.filter(created_at__date=today).count()
    total_inventory = LinenItem.objects.filter(
        status__in=['REGISTERED', 'READY_FOR_REISSUE', 'IN_LAUNDRY']
    ).count()

    recent_items = LinenItem.objects.filter(
        status__in=['REGISTERED', 'READY_FOR_REISSUE', 'IN_LAUNDRY']
    ).order_by('-created_at')[:8]

    # Sample manufacturer codes ready for testing
    sample_codes = [
        {'code': 'MFG-BS-90214', 'type': 'Bedsheet'},
        {'code': 'MFG-BS-90215', 'type': 'Bedsheet'},
        {'code': 'MFG-BL-40118', 'type': 'Blanket'},
        {'code': 'MFG-TW-33102', 'type': 'Towel'},
        {'code': 'MFG-PC-12095', 'type': 'Pillow Cover'},
    ]

    context = {
        'default_type': default_type,
        'today_count': today_count,
        'total_inventory': total_inventory,
        'recent_items': recent_items,
        'sample_codes': sample_codes,
        'sample_qr': 'MFG-BS-90214',
    }
    return render(request, 'laundry/register_linen.html', context)


@role_required('LAUNDRY')
def laundry_intake(request):
    """
    Screen 5.2: Laundry Intake Scan
    - Same scan-target and manual-entry components as attendant app (identical styling).
    - After scan: confirmation card ("Received at laundry", item type + ID).
    - Two stat tiles: Received today / In washing.
    - Button: "Move to washing".
    """
    today = timezone.now().date()
    received_today = LinenItem.objects.filter(
        status='RECEIVED_AT_LAUNDRY',
        updated_at__date=today
    ).count() or 42
    in_washing = LinenItem.objects.filter(status='WASHING').count() or 18
    returned_items = LinenItem.objects.filter(
        status='RETURNED'
    ).order_by('-updated_at')[:50]

    context = {
        'received_today': received_today,
        'in_washing': in_washing,
        'returned_items': returned_items,
        'demo_code': 'BS-10245',
    }
    return render(request, 'laundry/intake_scan.html', context)


# ============================================================
# 6. SUPERVISOR CONSOLE SCREENS (Supervisor role ONLY)
# Dark theme with 2.5% instrument grid
# ============================================================

@role_required('SUPERVISOR')
def supervisor_handoff(request):
    """
    Screen 6.1: Assign & Hand Off Linen (Zone Employees Coach & Shift Allocation)
    - Displays all attendants in the supervisor's zone.
    - Supervisor can assign each employee to which coach and decide their shift.
    - Header: shift + train context + "[N] bedsheets received from laundry · [N] allocated so far".
    - Table: Attendant | Coach | Shift | Bedsheets handed over | Status | Quick Allocate.
    """
    today = timezone.now().date()
    profile = getattr(request.user, 'profile', None)
    supervisor_zone = getattr(profile, 'zone', 'South Central Railway (SCR)') if profile else 'South Central Railway (SCR)'

    train = Train.objects.filter(train_number='12760').first() or Train.objects.first()
    coaches = Coach.objects.filter(train=train).order_by('coach_number')

    # Get all attendants in this supervisor's zone
    zone_attendants = User.objects.filter(
        profile__role__in=['ATTENDER', 'ATTENDANT'],
        profile__zone=supervisor_zone
    ).select_related('profile').order_by('id')

    # Ensure handoffs exist for each attendant in the zone
    handoffs = []
    default_coaches = ['B2', 'B1', 'B3', 'A1']
    for idx, att in enumerate(zone_attendants):
        h = CoachHandOff.objects.filter(attendant=att, date=today).order_by('-updated_at', '-id').first()
        if not h:
            c_num = default_coaches[idx % len(default_coaches)]
            c = Coach.objects.filter(train=train, coach_number=c_num).first() or coaches.first()
            h = CoachHandOff.objects.create(
                attendant=att,
                train=train,
                coach=c,
                shift='Morning' if idx % 2 == 0 else 'Evening',
                bedsheets_handed_over=100,
                status='CONFIRMED',
                date=today
            )
        handoffs.append(h)

    total_received_from_laundry = 450
    allocated_so_far = sum(h.bedsheets_handed_over for h in handoffs)

    context = {
        'supervisor_zone': supervisor_zone,
        'train': train,
        'coaches': coaches,
        'handoffs': handoffs,
        'zone_attendants': zone_attendants,
        'total_received': total_received_from_laundry,
        'allocated_so_far': allocated_so_far,
        'active_nav': 'handoff',
    }
    return render(request, 'supervisor/assign_handoff.html', context)


@role_required('SUPERVISOR')
def supervisor_dashboard(request):
    """
    Screen 6.2: Operations Dashboard (Optional)
    - Left nav includes "Assign & hand off" alongside Dashboard, Trains, Missing linen, Settlement, Sync review, Reports.
    - Row of headline KPI stats rendered as split-flap readouts: Total linen, Issued, Returned, Unaccounted, Damaged, Sync conflicts.
    - Operational-priorities table: Train | Coach | Loss rate | Risk tag (Low/Medium/High).
    - Simple CSS bar-row component for "loss by route" — not a Chart.js chart.
    """
    analytics = get_analytics_data()

    # Route loss data for simple CSS bar-row component
    route_loss_data = [
        {'route': 'NDLS ➔ HYB (Train 12760)', 'loss_rate': 6.0, 'missing': 6, 'risk': 'HIGH'},
        {'route': 'HYB ➔ NDLS (Train 12762)', 'loss_rate': 4.0, 'missing': 4, 'risk': 'MEDIUM'},
        {'route': 'SC ➔ MAS (Train 12761)', 'loss_rate': 1.0, 'missing': 1, 'risk': 'LOW'},
        {'route': 'MAS ➔ SC (Train 12763)', 'loss_rate': 0.8, 'missing': 1, 'risk': 'LOW'},
    ]

    context = {
        'analytics': analytics,
        'route_loss_data': route_loss_data,
        'active_nav': 'dashboard',
        # Split flap lists for headline numbers
        'total_chars': list(f"{analytics['total']:04d}"),
        'issued_chars': list(f"{analytics['issued']:04d}"),
        'returned_chars': list(f"{analytics['returned']:04d}"),
        'unaccounted_chars': list(f"{analytics['unaccounted']:02d}"),
        'damaged_chars': list("00"),
        'conflicts_chars': list("00"),
    }
    return render(request, 'supervisor/dashboard.html', context)


@role_required('SUPERVISOR')
def supervisor_settlement(request):
    """
    Screen 6.3: Missing Linen & Settlement (Optional)
    - Item detail view with a horizontal checkpoint timeline:
      (Registered → Loaded → Berth assigned → Issued → Collected → Laundry return)
      Completed steps in green, last-known step in amber, remaining steps dim.
    - Settlement status dropdown (Pending/Charged/Waived), amount field, "Save decision" button.
    """
    unaccounted_items = LinenItem.objects.filter(
        status__in=['UNACCOUNTED', 'INVESTIGATION_REQUIRED']
    ).prefetch_related('lifecycle_events', 'assignments')

    selected_code = request.GET.get('code', 'BL-20562')
    selected_item = unaccounted_items.filter(linen_code=selected_code).first() or unaccounted_items.first()

    context = {
        'items': unaccounted_items,
        'selected_item': selected_item,
        'active_nav': 'settlement',
    }
    return render(request, 'supervisor/missing_settlement.html', context)


# ============================================================
# ADDITIONAL SUPERVISOR UTILITIES
# ============================================================

@role_required('SUPERVISOR')
def audit_log(request):
    events = LinenLifecycleEvent.objects.select_related('linen', 'train', 'coach', 'performed_by').order_by('-timestamp')[:100]
    scans = CollectionScan.objects.select_related('collection_session', 'linen', 'scanned_by').order_by('-scanned_at')[:100]
    return render(request, 'reports/audit_log.html', {'events': events, 'scans': scans, 'active_nav': 'reports'})


@role_required('SUPERVISOR')
def global_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        results = LinenItem.objects.filter(
            Q(linen_code__icontains=q) |
            Q(qr_code__icontains=q) |
            Q(current_location__icontains=q) |
            Q(status__icontains=q)
        ).distinct()[:50]

    return render(request, 'reports/search.html', {'query': q, 'results': results, 'active_nav': 'reports'})


@role_required('SUPERVISOR', 'ATTENDANT', 'LAUNDRY')
def linen_detail(request, linen_code):
    linen = get_object_or_404(LinenItem, linen_code=linen_code)
    qr_data_url = generate_qr_data_url(linen.linen_code, linen.linen_type)
    checkpoint = linen.get_last_verified_checkpoint()
    events = linen.lifecycle_events.all().order_by('-timestamp')
    latest_assignment = linen.latest_assignment

    context = {
        'linen': linen,
        'qr_data_url': qr_data_url,
        'checkpoint': checkpoint,
        'events': events,
        'latest_assignment': latest_assignment,
    }
    return render(request, 'linen/detail.html', context)


def linen_qr_image(request, linen_code):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(linen_code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0c2340", back_color="#ffffff").convert('RGB')

    width, height = img.size
    banner = Image.new('RGB', (width, height + 45), '#ffffff')
    banner.paste(img, (0, 0))
    draw = ImageDraw.Draw(banner)
    try:
        draw.text((15, height + 10), f"LINENGUARD - {linen_code}", fill="#0c2340")
    except Exception:
        pass

    buf = io.BytesIO()
    banner.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type="image/png")


@role_required('SUPERVISOR', 'LAUNDRY')
def linen_qr_print(request, linen_code):
    linen = get_object_or_404(LinenItem, linen_code=linen_code)
    qr_data_url = generate_qr_data_url(linen.linen_code, linen.linen_type)
    return render(request, 'linen/print_qr.html', {'linen': linen, 'qr_data_url': qr_data_url})
