from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from .models import (
    LinenItem, CollectionSession, Coach, Train,
    PassengerPNR, LinenAssignment, LinenLifecycleEvent, CoachHandOff, UserProfile
)
from .services import (
    validate_scan, mark_linen_returned, record_scan_attempt,
    laundry_receive_item, laundry_start_wash, laundry_ready_reissue,
    get_analytics_data, lookup_pnr, register_linen_item, generate_qr_data_url,
    assign_linen_item, register_manufacturer_linen, generate_laundry_linen_items
)


def role_allowed(user, *roles):
    """
    Strict server-side RBAC validator.
    Normalized roles: 'SUPERVISOR', 'ATTENDANT', 'LAUNDRY'
    """
    if not user or not user.is_authenticated:
        return False
    profile = getattr(user, 'profile', None)
    current_role = profile.get_normalized_role() if profile else ('SUPERVISOR' if user.is_staff else None)
    
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
            
    return current_role in normalized_targets


# ============================================================
# ATTENDANT APIS (Attendant role ONLY)
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_collection_scan(request):
    """
    Validates scanned QR code against active coach session.
    Enforced for Attendant only.
    """
    if not role_allowed(request.user, 'ATTENDANT'):
        return Response({'valid': False, 'message': 'Attendant access required.'}, status=403)

    session_id = request.data.get('session_id')
    qr_code = request.data.get('qr_code', '').strip().upper()

    if not session_id or not qr_code:
        return Response({'valid': False, 'result': 'UNKNOWN_QR', 'message': 'Missing session ID or QR code.'}, status=400)

    session = get_object_or_404(CollectionSession, id=session_id)
    validation = validate_scan(session, qr_code, request.user)

    linen = validation['linen']
    assignment = validation['assignment']

    record_scan_attempt(
        collection_session=session,
        qr_code_str=qr_code,
        result=validation['result'],
        message=validation['message'],
        user=request.user,
        linen=linen
    )

    data = {
        'valid': validation['valid'],
        'result': validation['result'],
        'message': validation['message'],
        'qr_code': qr_code,
    }

    if linen:
        data.update({
            'linen_code': linen.linen_code,
            'linen_type': linen.linen_type,
            'status': linen.status,
            'current_location': linen.current_location,
        })
    if assignment:
        data.update({
            'train': assignment.train.train_number,
            'coach': assignment.coach.coach_number,
            'berth': assignment.berth,
            'pnr': assignment.passenger_reference,
            'issued_at': timezone.localtime(assignment.issued_at).strftime('%I:%M %p') if assignment.issued_at else '',
            'expected_collection': timezone.localtime(assignment.expected_collection_time).strftime('%I:%M %p') if assignment.expected_collection_time else '',
        })

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_returned(request):
    """
    Deliberate confirmation to mark a scanned item returned.
    Never auto-accepted on scan — must be explicitly tapped.
    """
    if not role_allowed(request.user, 'ATTENDANT'):
        return Response({'success': False, 'message': 'Attendant access required.'}, status=403)

    session_id = request.data.get('session_id')
    linen_code = request.data.get('linen_code', '').strip().upper()

    if not session_id or not linen_code:
        return Response({'success': False, 'message': 'Missing session ID or linen code.'}, status=400)

    session = get_object_or_404(CollectionSession, id=session_id)
    linen = get_object_or_404(LinenItem, linen_code=linen_code)

    if linen.status == 'RETURNED':
        return Response({'success': False, 'message': f'Linen {linen.linen_code} is already marked as returned.'})

    mark_linen_returned(session, linen, request.user)

    return Response({
        'success': True,
        'message': f'Linen {linen.linen_code} ({linen.linen_type}) successfully marked as RETURNED.',
        'linen_code': linen.linen_code,
        'linen_type': linen.linen_type,
        'scanned_quantity': session.scanned_quantity,
        'expected_quantity': session.expected_quantity,
        'remaining_quantity': max(0, session.expected_quantity - session.scanned_quantity),
        'timestamp': timezone.localtime(timezone.now()).strftime('%I:%M %p')
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_attendant_issue_linen(request):
    """
    Deliberate assignment of scanned linen to passenger berth.
    Never auto-assigned — requires explicit manual verification check.
    """
    if not role_allowed(request.user, 'ATTENDANT'):
        return Response({'success': False, 'message': 'Attendant access required.'}, status=403)

    pnr_number = request.data.get('pnr_number', '').strip().upper()
    linen_codes = request.data.get('linen_codes') or [request.data.get('linen_code', '')]
    linen_codes = [str(code).strip().upper() for code in linen_codes if str(code).strip()]

    if not pnr_number or not linen_codes:
        return Response({'success': False, 'message': 'Missing PNR number or linen codes.'}, status=400)
    if len(set(linen_codes)) != len(linen_codes):
        return Response({'success': False, 'message': 'Select one or more different linen items.'}, status=400)

    try:
        passenger = PassengerPNR.objects.get(pnr_number__iexact=pnr_number)
    except PassengerPNR.DoesNotExist:
        return Response({'success': False, 'message': f'Passenger PNR {pnr_number} not found.'}, status=404)

    linen_items = []
    for linen_code in linen_codes:
        linen = LinenItem.objects.filter(
            Q(linen_code__iexact=linen_code) | Q(qr_code__iexact=linen_code)
        ).first()
        if not linen:
            return Response({
                'success': False,
                'inventory_verified': False,
                'message': f"Cannot issue: Linen QR '{linen_code}' is not in depot inventory."
            }, status=400)
        if linen.linen_type in {item.linen_type for item in linen_items}:
            return Response({'success': False, 'message': 'Select one item of each linen type.'}, status=400)
        if linen.status not in ['REGISTERED', 'READY_FOR_REISSUE']:
            active_assignment = linen.assignments.filter(assignment_status='ACTIVE').first()
            berth_loc = f"Berth {active_assignment.berth} (PNR {active_assignment.passenger_reference})" if active_assignment else "another passenger"
            return Response({
                'success': False,
                'inventory_verified': True,
                'message': f"Cannot issue: Linen '{linen.linen_code}' is already issued to {berth_loc}."
            }, status=400)
        linen_items.append(linen)

    with transaction.atomic():
        for linen in linen_items:
            assign_linen_item(
                linen=linen,
                train=passenger.train,
                coach=passenger.coach,
                berth=passenger.berth,
                passenger_reference=passenger.pnr_number,
                source_station=passenger.source_station,
                destination_station=passenger.destination_station,
                user=request.user
            )

    # Update passenger boarding status
    passenger.boarding_status = 'Issued'
    passenger.save()

    return Response({
        'success': True,
        'inventory_verified': True,
        'message': f"Linen set successfully assigned to Berth {passenger.berth} (PNR {passenger.pnr_number}).",
        'linen_codes': [linen.linen_code for linen in linen_items],
        'linen_types': [linen.linen_type for linen in linen_items],
        'berth': passenger.berth,
        'pnr_number': passenger.pnr_number,
    })


# ============================================================
# LAUNDRY APIS (Laundry role ONLY)
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_laundry_register(request):
    """
    Scans manufacturer-attached QR code directly into depot inventory.
    Accessible ONLY to Laundry staff.
    """
    if not role_allowed(request.user, 'LAUNDRY'):
        return Response({'success': False, 'message': 'Laundry access required.'}, status=403)

    linen_type = request.data.get('linen_type', 'Bedsheet').strip()
    manufacturer_qr = request.data.get('manufacturer_qr') or request.data.get('custom_code') or request.data.get('qr_code', '')
    manufacturer_qr = manufacturer_qr.strip().upper()

    if not manufacturer_qr:
        return Response({'success': False, 'message': 'Please scan or enter the manufacturer QR code.'}, status=400)

    item, created = register_manufacturer_linen(
        manufacturer_qr=manufacturer_qr,
        linen_type=linen_type,
        user=request.user
    )

    qr_data_url = generate_qr_data_url(item.linen_code, item.linen_type)

    today_count = LinenItem.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    inventory_count = LinenItem.objects.filter(
        status__in=['REGISTERED', 'READY_FOR_REISSUE', 'IN_LAUNDRY']
    ).count()

    action_text = "registered into depot inventory" if created else "already verified in depot inventory"

    return Response({
        'success': True,
        'created': created,
        'message': f"✓ Manufacturer Linen {item.linen_code} ({item.linen_type}) {action_text}!",
        'linen_code': item.linen_code,
        'linen_type': item.linen_type,
        'status': item.get_status_display(),
        'location': item.current_location,
        'qr_data_url': qr_data_url,
        'today_count': today_count,
        'inventory_count': inventory_count,
        'timestamp': timezone.localtime(timezone.now()).strftime('%H:%M:%S'),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_laundry_generate(request):
    """
    Generates new unique linen items directly from Laundry login into Depot stock.
    Creates items with status READY_FOR_REISSUE so they are immediately available
    for Train Attendants to issue to passengers.
    """
    if not role_allowed(request.user, 'LAUNDRY'):
        return Response({'success': False, 'message': 'Laundry access required.'}, status=403)

    linen_type = request.data.get('linen_type', 'Bedsheet').strip()
    try:
        count = int(request.data.get('count', 1))
        count = max(1, min(count, 50))  # Cap between 1 and 50
    except (ValueError, TypeError):
        count = 1

    created_items = generate_laundry_linen_items(
        linen_type=linen_type,
        count=count,
        user=request.user
    )

    today_count = LinenItem.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    inventory_count = LinenItem.objects.filter(
        status__in=['REGISTERED', 'READY_FOR_REISSUE', 'IN_LAUNDRY']
    ).count()

    items_data = [
        {
            'linen_code': item.linen_code,
            'linen_type': item.linen_type,
            'status': item.get_status_display(),
            'location': item.current_location,
            'created_at': timezone.localtime(item.created_at).strftime('%H:%M:%S'),
        }
        for item in created_items
    ]

    summary_text = (
        f"Generated 1 Complete Linen Set (4 items)"
        if linen_type in ['KIT', 'COMPLETE_KIT', 'SET', 'ALL']
        else f"Generated {len(created_items)} {linen_type} item(s)"
    )

    return Response({
        'success': True,
        'message': f"✓ {summary_text} successfully added to depot stock and ready for attendants!",
        'items': items_data,
        'count': len(created_items),
        'today_count': today_count,
        'inventory_count': inventory_count,
        'timestamp': timezone.localtime(timezone.now()).strftime('%H:%M:%S'),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_available_linen_stock(request):
    """
    Returns all linen items currently available in depot stock ready for coach issuance.
    Accessible to Attendants, Laundry, and Supervisors.
    """
    available_items = LinenItem.objects.filter(
        status__in=['REGISTERED', 'READY_FOR_REISSUE']
    ).order_by('-created_at')

    by_type = {
        'Bedsheet': [],
        'Blanket': [],
        'Towel': [],
        'Pillow Cover': [],
    }

    items_list = []
    for item in available_items:
        data = {
            'id': item.id,
            'linen_code': item.linen_code,
            'linen_type': item.linen_type,
            'status': item.status,
            'created_at': timezone.localtime(item.created_at).strftime('%I:%M %p, %d %b'),
        }
        items_list.append(data)
        if item.linen_type in by_type:
            by_type[item.linen_type].append(data)

    return Response({
        'success': True,
        'total_count': len(items_list),
        'by_type': by_type,
        'items': items_list,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_laundry_receive(request):
    if not role_allowed(request.user, 'LAUNDRY'):
        return Response({'success': False, 'message': 'Laundry access required.'}, status=403)

    qr_code = request.data.get('qr_code', '').strip().upper()
    if not qr_code:
        return Response({'success': False, 'message': 'Please enter or scan a QR code.'}, status=400)

    success, msg = laundry_receive_item(qr_code, request.user)
    return Response({'success': success, 'message': msg})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_laundry_wash(request):
    if not role_allowed(request.user, 'LAUNDRY'):
        return Response({'success': False, 'message': 'Laundry access required.'}, status=403)

    qr_code = request.data.get('qr_code', '').strip().upper()
    if not qr_code:
        return Response({'success': False, 'message': 'Please enter or scan a QR code.'}, status=400)

    success, msg = laundry_start_wash(qr_code, request.user)
    return Response({'success': success, 'message': msg})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_laundry_reissue(request):
    if not role_allowed(request.user, 'LAUNDRY'):
        return Response({'success': False, 'message': 'Laundry access required.'}, status=403)

    qr_code = request.data.get('qr_code', '').strip().upper()
    if not qr_code:
        return Response({'success': False, 'message': 'Please enter or scan a QR code.'}, status=400)

    success, msg = laundry_ready_reissue(qr_code, request.user)
    return Response({'success': success, 'message': msg})


# ============================================================
# SUPERVISOR APIS (Supervisor role ONLY)
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_supervisor_assign_attendant(request):
    """
    Supervisor assigns/reassigns an attendant in their zone to a specific coach and shift.
    Updates CoachHandOff and syncs collection session.
    """
    if not role_allowed(request.user, 'SUPERVISOR'):
        return Response({'success': False, 'message': 'Supervisor access required.'}, status=403)

    attendant_id = request.data.get('attendant_id') or request.data.get('employee_id')
    coach_number = request.data.get('coach_number', '').strip().upper()
    shift = request.data.get('shift', 'Morning').strip()
    train_id = request.data.get('train_id')
    bedsheets_count = request.data.get('bedsheets_handed_over', 100)

    if not attendant_id or not coach_number:
        return Response({'success': False, 'message': 'Attendant ID and Coach Number are required.'}, status=400)

    attendant_user = None
    if str(attendant_id).isdigit():
        attendant_user = User.objects.filter(id=int(attendant_id)).first()
    if not attendant_user:
        attendant_user = User.objects.filter(
            Q(profile__badge_number__iexact=str(attendant_id).strip()) |
            Q(username__iexact=str(attendant_id).strip())
        ).first()

    if not attendant_user:
        return Response({'success': False, 'message': f'Attendant with ID/badge "{attendant_id}" not found.'}, status=404)

    if train_id:
        train = get_object_or_404(Train, id=train_id)
    else:
        train = Train.objects.filter(train_number='12760').first() or Train.objects.first()

    coach = Coach.objects.filter(train=train, coach_number=coach_number).first()
    if not coach:
        coach = Coach.objects.create(train=train, coach_number=coach_number, coach_type='3A')

    try:
        sheets = max(0, int(bedsheets_count))
    except (ValueError, TypeError):
        sheets = 100

    # Look for existing handoff for this attendant today
    handoff = CoachHandOff.objects.filter(attendant=attendant_user, date=timezone.now().date()).first()
    if handoff:
        handoff.train = train
        handoff.coach = coach
        handoff.shift = shift
        handoff.bedsheets_handed_over = sheets
        handoff.status = 'CONFIRMED'
        handoff.save()
    else:
        handoff = CoachHandOff.objects.create(
            attendant=attendant_user,
            train=train,
            coach=coach,
            shift=shift,
            bedsheets_handed_over=sheets,
            status='CONFIRMED',
            date=timezone.now().date()
        )

    # Sync collection session to match this coach
    session = CollectionSession.objects.filter(attender=attendant_user, status='IN_PROGRESS').first()
    if session:
        session.train = train
        session.coach = coach
        session.expected_quantity = sheets
        session.save()
    else:
        CollectionSession.objects.create(
            attender=attendant_user,
            train=train,
            coach=coach,
            journey_date=timezone.now().date(),
            expected_quantity=sheets,
            status='IN_PROGRESS'
        )

    return Response({
        'success': True,
        'message': f"✓ Successfully allocated {attendant_user.get_full_name() or attendant_user.username} to Coach {coach.coach_number} ({shift} Shift).",
        'handoff_id': handoff.id,
        'attendant_id': attendant_user.id,
        'attendant_name': attendant_user.get_full_name() or attendant_user.username,
        'coach': coach.coach_number,
        'shift': handoff.shift,
        'bedsheets_handed_over': handoff.bedsheets_handed_over,
        'status': handoff.status,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_supervisor_update_handoff(request):
    """
    Supervisor updates the manual bedsheet count, coach, shift, or status for an attendant row.
    Autosaves per row.
    """
    if not role_allowed(request.user, 'SUPERVISOR'):
        return Response({'success': False, 'message': 'Supervisor access required.'}, status=403)

    handoff_id = request.data.get('handoff_id')
    count_val = request.data.get('bedsheets_handed_over')
    status_val = request.data.get('status')
    coach_number = request.data.get('coach_number')
    shift_val = request.data.get('shift')

    if not handoff_id:
        return Response({'success': False, 'message': 'Missing handoff_id.'}, status=400)

    handoff = get_object_or_404(CoachHandOff, id=handoff_id)
    if count_val is not None:
        try:
            handoff.bedsheets_handed_over = max(0, int(count_val))
        except (ValueError, TypeError):
            return Response({'success': False, 'message': 'Invalid count number.'}, status=400)

    if coach_number:
        clean_c = coach_number.strip().upper()
        c_obj = Coach.objects.filter(train=handoff.train, coach_number=clean_c).first()
        if not c_obj:
            c_obj = Coach.objects.create(train=handoff.train, coach_number=clean_c, coach_type='3A')
        handoff.coach = c_obj

    if shift_val in ['Morning', 'Evening', 'Night']:
        handoff.shift = shift_val

    if status_val in ['PENDING', 'CONFIRMED']:
        handoff.status = status_val

    handoff.save()

    # Sync with attendant's active collection session if present
    session = CollectionSession.objects.filter(
        attender=handoff.attendant,
        status='IN_PROGRESS'
    ).first()
    if session:
        session.train = handoff.train
        session.coach = handoff.coach
        session.expected_quantity = handoff.bedsheets_handed_over
        session.save()

    return Response({
        'success': True,
        'message': f"✓ Updated hand-off for {handoff.attendant.username}: Coach {handoff.coach.coach_number}, {handoff.shift} Shift, {handoff.bedsheets_handed_over} sheets.",
        'handoff_id': handoff.id,
        'coach': handoff.coach.coach_number,
        'shift': handoff.shift,
        'bedsheets_handed_over': handoff.bedsheets_handed_over,
        'status': handoff.status,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_supervisor_create_employee(request):
    """
    Allows a Supervisor to register a new Attendant employee:
    - Provides Full Name, Employee ID (Badge Number), Username, Password.
    - Sets initial Coach Allocation, Shift, and Linen Quota.
    - Creates the User, UserProfile, CoachHandOff, and CollectionSession.
    - Returns credentials summary for sharing with the attendant.
    """
    if not role_allowed(request.user, 'SUPERVISOR'):
        return Response({'success': False, 'message': 'Supervisor access required.'}, status=403)

    full_name = request.data.get('full_name', '').strip()
    employee_id = request.data.get('employee_id', '').strip().upper()
    username = request.data.get('username', '').strip().lower()
    password = request.data.get('password', '').strip()
    coach_number = request.data.get('coach_number', 'B2').strip().upper()
    shift = request.data.get('shift', 'Morning').strip()
    quota = request.data.get('quota', 100)

    if not full_name:
        return Response({'success': False, 'message': 'Please provide the employee full name.'}, status=400)

    if not employee_id:
        return Response({'success': False, 'message': 'Please provide an Employee ID / Badge Number.'}, status=400)

    # If username is empty, derive from employee_id or full_name
    if not username:
        base_user = employee_id.lower().replace('-', '').replace(' ', '')
        username = base_user
        idx = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_user}{idx}"
            idx += 1

    # Check if employee_id or username already exists
    if UserProfile.objects.filter(badge_number__iexact=employee_id).exists():
        return Response({'success': False, 'message': f'Employee ID "{employee_id}" is already registered to another staff member.'}, status=400)

    if User.objects.filter(username__iexact=username).exists():
        return Response({'success': False, 'message': f'Username "{username}" is already in use. Please choose another.'}, status=400)

    if not password:
        password = 'attender123'

    try:
        quota_int = max(10, min(500, int(quota)))
    except (ValueError, TypeError):
        quota_int = 100

    # Parse first and last name
    name_parts = full_name.split(None, 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    # Get supervisor's zone
    profile = getattr(request.user, 'profile', None)
    supervisor_zone = profile.zone if profile and profile.zone else 'South Central Railway (SCR)'

    # 1. Create User
    new_user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password
    )

    # 2. Create / Update UserProfile
    u_profile, _ = UserProfile.objects.get_or_create(user=new_user)
    u_profile.role = 'ATTENDANT'
    u_profile.badge_number = employee_id
    u_profile.zone = supervisor_zone
    u_profile.save()

    # 3. Associate with Train & Coach
    train = Train.objects.filter(train_number='12760').first() or Train.objects.first()
    coach = Coach.objects.filter(train=train, coach_number=coach_number).first()
    if not coach:
        coach = Coach.objects.create(train=train, coach_number=coach_number, coach_type='3A')

    # 4. Create Initial CoachHandOff
    handoff = CoachHandOff.objects.create(
        attendant=new_user,
        train=train,
        coach=coach,
        shift=shift if shift in ['Morning', 'Evening', 'Night'] else 'Morning',
        bedsheets_handed_over=quota_int,
        status='CONFIRMED',
        date=timezone.now().date()
    )

    # 5. Initialize CollectionSession
    CollectionSession.objects.create(
        attender=new_user,
        train=train,
        coach=coach,
        journey_date=timezone.now().date(),
        expected_quantity=quota_int,
        status='IN_PROGRESS'
    )

    return Response({
        'success': True,
        'message': f"✓ Attendant {full_name} ({employee_id}) successfully registered and allocated to Coach {coach.coach_number}.",
        'employee': {
            'id': new_user.id,
            'full_name': full_name,
            'employee_id': employee_id,
            'username': username,
            'password': password,
            'coach': coach.coach_number,
            'shift': handoff.shift,
            'quota': quota_int,
            'zone': supervisor_zone,
            'handoff_id': handoff.id,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_supervisor_settlement_decision(request):
    """
    Saves settlement decision (Pending / Charged / Waived) for a missing linen item.
    """
    if not role_allowed(request.user, 'SUPERVISOR'):
        return Response({'success': False, 'message': 'Supervisor access required.'}, status=403)

    linen_code = request.data.get('linen_code', '').strip().upper()
    settlement_status = request.data.get('settlement_status', 'PENDING').upper()
    amount = request.data.get('amount', 0)

    item = get_object_or_404(LinenItem, linen_code=linen_code)
    if settlement_status in ['PENDING', 'CHARGED', 'WAIVED']:
        item.settlement_status = settlement_status
    try:
        item.settlement_amount = float(amount)
    except (ValueError, TypeError):
        pass
    item.save()

    LinenLifecycleEvent.objects.create(
        linen=item,
        event_type='INVESTIGATION_REQUIRED',
        timestamp=timezone.now(),
        location='Supervisor Settlement Terminal',
        performed_by=request.user,
        notes=f"Settlement decision recorded: {item.settlement_status} (INR {item.settlement_amount})."
    )

    return Response({
        'success': True,
        'linen_code': item.linen_code,
        'settlement_status': item.settlement_status,
        'settlement_amount': str(item.settlement_amount),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    if not role_allowed(request.user, 'SUPERVISOR'):
        return Response({'message': 'Supervisor access required.'}, status=403)

    data = get_analytics_data()
    return Response(data)


@api_view(['GET'])
def api_get_coaches(request, train_id):
    coaches = Coach.objects.filter(train_id=train_id).values('id', 'coach_number', 'coach_type')
    return Response(list(coaches))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_lookup_pnr(request, pnr_number):
    clean_pnr = pnr_number.strip().upper()
    if not clean_pnr:
        return Response({'success': False, 'message': 'PNR number required'}, status=400)

    data = lookup_pnr(clean_pnr)
    return Response({'success': True, 'pnr': data})
