import io
import base64
import re
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from .models import (
    LinenItem, Train, Coach, LinenAssignment,
    LinenLifecycleEvent, CollectionSession, CollectionScan,
    PassengerPNR, CoachHandOff
)


def generate_qr_data_url(linen_code, linen_type=""):
    """
    Generates a clean QR code PNG image as a base64 Data URL for direct HTML rendering.
    High contrast, crisp borders with Indian Railways / LinenGuard identifier.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(linen_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0c2340", back_color="#ffffff").convert('RGB')

    # Add a top/bottom caption banner to the image
    width, height = img.size
    banner_height = 40
    new_img = Image.new('RGB', (width, height + banner_height), color='#ffffff')
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    # Simple caption text
    caption = f"{linen_code}"
    # Draw simple text at bottom center
    try:
        # Fallback default font
        draw.text((10, height + 8), caption, fill="#0c2340")
        if linen_type:
            draw.text((width - 90, height + 8), linen_type[:10], fill="#555555")
    except Exception:
        pass

    buffer = io.BytesIO()
    new_img.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"


def register_linen_item(linen_type, linen_code=None, user=None, current_location="Central Railway Laundry"):
    """
    Registers a new linen item with a unique code and initial lifecycle event.
    """
    if not linen_code:
        # Auto-generate unique code
        prefix_map = {
            'Bedsheet': 'BS',
            'Blanket': 'BL',
            'Towel': 'TW',
            'Pillow Cover': 'PC',
        }
        prefix = prefix_map.get(linen_type, 'LN')
        last_item = LinenItem.objects.filter(linen_code__startswith=prefix).order_by('-id').first()
        next_num = 10001
        if last_item:
            try:
                digits = int(last_item.linen_code.split('-')[1])
                next_num = digits + 1
            except (IndexError, ValueError):
                pass
        linen_code = f"{prefix}-{next_num}"

    # Ensure uniqueness
    counter = 1
    base_code = linen_code
    while LinenItem.objects.filter(linen_code=linen_code).exists():
        linen_code = f"{base_code}-{counter}"
        counter += 1

    qr_code = linen_code

    linen = LinenItem.objects.create(
        linen_code=linen_code,
        qr_code=qr_code,
        linen_type=linen_type,
        status='REGISTERED',
        current_location=current_location
    )

    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='REGISTERED',
        timestamp=timezone.now(),
        location=current_location,
        performed_by=user,
        notes=f"Linen item {linen_code} registered in system as {linen_type}."
    )

    return linen


def lookup_pnr(pnr_number):
    """
    Looks up passenger booking details by PNR number.
    If PNR does not exist, intelligently provisions a realistic railway booking entry
    so that any 10-digit Indian Railways PNR or demo PNR works instantly in demonstrations.
    """
    clean_pnr = pnr_number.strip().upper()
    pnr_obj = PassengerPNR.objects.filter(pnr_number__iexact=clean_pnr).first()

    if not pnr_obj:
        # Resolve or pick default train and coach
        train = Train.objects.filter(train_number='12760').first() or Train.objects.first()
        if not train:
            train = Train.objects.create(
                train_number='12760', train_name='Demo Express',
                source='New Delhi (NDLS)', destination='Hyderabad (HYB)'
            )
        
        coach = Coach.objects.filter(train=train, coach_number='B2').first() or Coach.objects.filter(train=train).first()
        if not coach:
            coach = Coach.objects.create(train=train, coach_number='B2', coach_type='3A')

        # Generate deterministic berth number from PNR
        digits = ''.join([c for c in clean_pnr if c.isdigit()])
        berth_num = str((int(digits) % 72) + 1) if digits else "36"

        berth_types = ['Lower Berth', 'Middle Berth', 'Upper Berth', 'Side Lower', 'Side Upper']
        b_type = berth_types[int(berth_num) % len(berth_types)]

        pnr_obj = PassengerPNR.objects.create(
            pnr_number=clean_pnr,
            train=train,
            coach=coach,
            berth=berth_num,
            berth_type=b_type,
            source_station=train.source,
            destination_station=train.destination,
            journey_date=timezone.now().date(),
            departure_time="20:00",
            expected_arrival_time="06:30",
            passenger_label=f"Passenger {clean_pnr[-4:]} (M/30)",
            passenger_name=f"Passenger {clean_pnr[-4:]}",
            passenger_age=30,
            passenger_gender='Male',
            status="CNF / Confirmed"
        )

    if not pnr_obj.passenger_name:
        match = re.match(r'^(.*?)\s*\(([MF])/(\d+)\)$', pnr_obj.passenger_label or '')
        if match:
            pnr_obj.passenger_name = match.group(1).strip()
            pnr_obj.passenger_gender = {'M': 'Male', 'F': 'Female'}.get(match.group(2), '')
            pnr_obj.passenger_age = int(match.group(3))
        else:
            pnr_obj.passenger_name = pnr_obj.passenger_label or f"Passenger {clean_pnr[-4:]}"
        pnr_obj.save(update_fields=['passenger_name', 'passenger_gender', 'passenger_age'])

    ticket_image_url = pnr_obj.ticket_image.url if pnr_obj.ticket_image else generate_ticket_preview_data_url(pnr_obj)

    return {
        'id': pnr_obj.id,
        'pnr_number': pnr_obj.pnr_number,
        'train_id': pnr_obj.train.id,
        'train_number': pnr_obj.train.train_number,
        'train_name': pnr_obj.train.train_name,
        'coach_id': pnr_obj.coach.id,
        'coach_number': pnr_obj.coach.coach_number,
        'coach_type': pnr_obj.coach.coach_type,
        'berth': pnr_obj.berth,
        'berth_type': pnr_obj.berth_type,
        'source_station': pnr_obj.source_station,
        'destination_station': pnr_obj.destination_station,
        'journey_date': pnr_obj.journey_date.strftime('%Y-%m-%d'),
        'departure_time': pnr_obj.departure_time,
        'expected_arrival_time': pnr_obj.expected_arrival_time,
        'passenger_label': pnr_obj.passenger_label,
        'passenger_name': pnr_obj.passenger_name,
        'passenger_age': pnr_obj.passenger_age,
        'passenger_gender': pnr_obj.passenger_gender,
        'passenger_phone': pnr_obj.passenger_phone,
        'passenger_email': pnr_obj.passenger_email,
        'passenger_address': pnr_obj.passenger_address,
        'ticket_image_url': ticket_image_url,
        'status': pnr_obj.status,
    }


def generate_ticket_preview_data_url(pnr_obj):
    image = Image.new('RGB', (900, 420), '#ffffff')
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 900, 78), fill='#0c2340')
    draw.text((30, 20), 'INDIAN RAILWAYS - DIGITAL TICKET', fill='#ffffff')
    draw.text((30, 105), f'PNR: {pnr_obj.pnr_number}', fill='#0c2340')
    draw.text((30, 150), f'Passenger: {pnr_obj.passenger_name}', fill='#222222')
    draw.text((30, 190), f'Age / Gender: {pnr_obj.passenger_age or "-"} / {pnr_obj.passenger_gender or "-"}', fill='#222222')
    draw.text((30, 230), f'Train: {pnr_obj.train.train_number} - {pnr_obj.train.train_name}', fill='#222222')
    draw.text((30, 270), f'Route: {pnr_obj.source_station} -> {pnr_obj.destination_station}', fill='#222222')
    draw.text((30, 310), f'Coach / Berth: {pnr_obj.coach.coach_number} / {pnr_obj.berth} ({pnr_obj.berth_type})', fill='#222222')
    draw.text((30, 350), f'Journey: {pnr_obj.journey_date} | Status: {pnr_obj.status}', fill='#222222')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"


def assign_linen_item(linen, train=None, coach=None, berth=None, passenger_reference='PNR-1001',
                      source_station=None, destination_station=None, journey_date=None, user=None, expected_collection_hours=8):
    """
    Assigns linen item to a train, coach, berth, and journey via PNR reference.
    Updates status to ISSUED and logs lifecycle events with route details.
    """
    now = timezone.now()

    # If train/coach/berth not explicitly provided, fetch from PNR
    if not train or not coach or not berth:
        pnr_info = lookup_pnr(passenger_reference)
        train = Train.objects.get(id=pnr_info['train_id'])
        coach = Coach.objects.get(id=pnr_info['coach_id'])
        berth = pnr_info['berth']
        source_station = pnr_info['source_station']
        destination_station = pnr_info['destination_station']

    if not source_station:
        source_station = train.source
    if not destination_station:
        destination_station = train.destination

    if not journey_date:
        journey_date = now.date()

    expected_collection = now + timedelta(hours=expected_collection_hours)

    assignment = LinenAssignment.objects.create(
        linen=linen,
        train=train,
        coach=coach,
        berth=berth,
        passenger_reference=passenger_reference,
        source_station=source_station,
        destination_station=destination_station,
        journey_date=journey_date,
        issued_at=now,
        expected_collection_time=expected_collection,
        assignment_status='ACTIVE'
    )

    linen.status = 'ISSUED'
    linen.current_location = f"Train {train.train_number} / Coach {coach.coach_number} / Berth {berth} ({source_station} -> {destination_station})"
    linen.save()

    # Create ASSIGNED_TO_BERTH event
    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='BERTH_ASSIGNED',
        timestamp=now + timedelta(seconds=1),
        location=f"Coach {coach.coach_number} / Berth {berth}",
        train=train,
        coach=coach,
        berth=berth,
        performed_by=user,
        notes=f"Allocated to Berth {berth} in Coach {coach.coach_number} under PNR {passenger_reference}."
    )

    # Create ISSUED_TO_PASSENGER event
    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='ISSUED_TO_PASSENGER',
        timestamp=now + timedelta(seconds=2),
        location=f"Coach {coach.coach_number} / Berth {berth}",
        train=train,
        coach=coach,
        berth=berth,
        performed_by=user,
        notes=f"Issued for journey {source_station} -> {destination_station} under PNR {passenger_reference}."
    )

    return assignment


def validate_scan(collection_session, qr_code_str, user):
    """
    Comprehensive QR scan validation for Attender Collection session.
    Returns:
      {
        'valid': bool,
        'result': 'SUCCESS' | 'WRONG_COACH' | 'WRONG_TRAIN' | 'ALREADY_RETURNED' | 'NOT_ASSIGNED' | 'UNKNOWN_QR',
        'message': str,
        'linen': LinenItem | None,
        'assignment': LinenAssignment | None,
      }
    """
    clean_code = qr_code_str.strip().upper()
    try:
        linen = LinenItem.objects.get(Q(qr_code__iexact=clean_code) | Q(linen_code__iexact=clean_code))
    except LinenItem.DoesNotExist:
        return {
            'valid': False,
            'result': 'UNKNOWN_QR',
            'message': f"QR code '{clean_code}' is not registered in LinenGuard.",
            'linen': None,
            'assignment': None
        }

    # Check active or recent assignment
    assignment = linen.assignments.order_by('-issued_at').first()

    if not assignment:
        return {
            'valid': False,
            'result': 'NOT_ASSIGNED',
            'message': f"Linen {linen.linen_code} is registered ({linen.status}) but not assigned to any active journey.",
            'linen': linen,
            'assignment': None
        }

    # Check if already returned
    if linen.status == 'RETURNED' or assignment.assignment_status == 'RETURNED':
        return {
            'valid': False,
            'result': 'ALREADY_RETURNED',
            'message': f"Linen {linen.linen_code} has already been returned at {timezone.localtime(assignment.returned_at).strftime('%H:%M %p') if assignment.returned_at else 'earlier session'}.",
            'linen': linen,
            'assignment': assignment
        }

    # Check train match (compare train numbers)
    assigned_train_no = str(assignment.train.train_number).strip()
    session_train_no = str(collection_session.train.train_number).strip()
    if assigned_train_no != session_train_no:
        return {
            'valid': False,
            'result': 'WRONG_TRAIN',
            'message': f"Linen {linen.linen_code} belongs to Train {assignment.train.train_number} ({assignment.train.train_name}), not current Train {collection_session.train.train_number}.",
            'linen': linen,
            'assignment': assignment
        }

    # Check coach match (compare coach numbers e.g. 'B2' vs 'B2')
    assigned_coach_no = str(assignment.coach.coach_number).strip().upper()
    session_coach_no = str(collection_session.coach.coach_number).strip().upper()
    if assigned_coach_no != session_coach_no:
        return {
            'valid': False,
            'result': 'WRONG_COACH',
            'message': f"Linen {linen.linen_code} belongs to Coach {assignment.coach.coach_number}, but current collection is for Coach {collection_session.coach.coach_number}.",
            'linen': linen,
            'assignment': assignment
        }

    # Check duplicate scan in this exact session
    already_scanned = collection_session.scans.filter(linen=linen, result='SUCCESS').exists()
    if already_scanned:
        return {
            'valid': False,
            'result': 'DUPLICATE_SCAN',
            'message': f"Linen {linen.linen_code} was already successfully scanned in this session.",
            'linen': linen,
            'assignment': assignment
        }

    return {
        'valid': True,
        'result': 'SUCCESS',
        'message': f"Linen {linen.linen_code} verified for Coach {assignment.coach.coach_number}, Berth {assignment.berth}.",
        'linen': linen,
        'assignment': assignment
    }


def record_scan_attempt(collection_session, qr_code_str, result, message, user, linen=None):
    """
    Logs every scan attempt to CollectionScan for audit and validation feedback.
    """
    return CollectionScan.objects.create(
        collection_session=collection_session,
        linen=linen,
        scanned_qr=qr_code_str,
        scanned_at=timezone.now(),
        scanned_by=user,
        result=result,
        message=message
    )


def mark_linen_returned(collection_session, linen, user):
    """
    Executes the successful return workflow:
    1. Sets linen status = RETURNED
    2. Updates LinenAssignment returned_at & status
    3. Creates COLLECTED_BY_ATTENDER and RETURNED_BY_PASSENGER events
    4. Records SUCCESS in CollectionScan
    5. Increments session scanned_quantity
    """
    now = timezone.now()
    assignment = linen.assignments.order_by('-issued_at').first()

    linen.status = 'RETURNED'
    linen.current_location = f"Collected in Coach {collection_session.coach.coach_number} (In Transit to Laundry)"
    linen.save()

    if assignment:
        assignment.returned_at = now
        assignment.assignment_status = 'RETURNED'
        assignment.save()

    # Attender collection event
    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='COLLECTED_BY_ATTENDER',
        timestamp=now,
        location=f"Coach {collection_session.coach.coach_number}",
        train=collection_session.train,
        coach=collection_session.coach,
        berth=assignment.berth if assignment else '',
        performed_by=user,
        notes=f"Collected by Attender {user.username} during coach sweep."
    )

    # Returned by passenger event
    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='RETURNED_BY_PASSENGER',
        timestamp=now - timedelta(seconds=30),
        location=f"Coach {collection_session.coach.coach_number} / Berth {assignment.berth if assignment else ''}",
        train=collection_session.train,
        coach=collection_session.coach,
        berth=assignment.berth if assignment else '',
        performed_by=user,
        notes="Item retrieved from passenger berth."
    )

    # Record scan record
    record_scan_attempt(
        collection_session=collection_session,
        qr_code_str=linen.qr_code,
        result='SUCCESS',
        message=f"Successfully collected from Berth {assignment.berth if assignment else 'N/A'}",
        user=user,
        linen=linen
    )

    # Increment count
    collection_session.scanned_quantity += 1
    collection_session.save()

    return True


def laundry_receive_item(linen_code, user, location="Central Railway Laundry"):
    """
    Receives returned linen at the laundry facility.
    """
    try:
        linen = LinenItem.objects.get(Q(qr_code__iexact=linen_code) | Q(linen_code__iexact=linen_code))
    except LinenItem.DoesNotExist:
        return False, f"Unknown QR code '{linen_code}'."

    now = timezone.now()
    linen.status = 'RECEIVED_AT_LAUNDRY'
    linen.current_location = location
    linen.save()

    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='RECEIVED_AT_LAUNDRY',
        timestamp=now,
        location=location,
        performed_by=user,
        notes="Received at laundry intake dock. Ready for sort & wash."
    )

    return True, f"Linen {linen.linen_code} ({linen.linen_type}) successfully received at laundry."


def laundry_start_wash(linen_code, user):
    """
    Starts industrial washing cycle for received linen item.
    """
    try:
        linen = LinenItem.objects.get(Q(qr_code__iexact=linen_code) | Q(linen_code__iexact=linen_code))
    except LinenItem.DoesNotExist:
        return False, f"Unknown QR code '{linen_code}'."

    now = timezone.now()
    linen.status = 'WASHING'
    linen.current_location = "Laundry Washing Unit #3 (Thermal Disinfection)"
    linen.save()

    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='WASHING',
        timestamp=now,
        location=linen.current_location,
        performed_by=user,
        notes="Industrial high-temperature wash and sanitization in progress."
    )

    return True, f"Linen {linen.linen_code} moved to WASHING cycle."


def laundry_ready_reissue(linen_code, user):
    """
    Marks linen as sanitized, pressed, and ready for train reissue.
    """
    try:
        linen = LinenItem.objects.get(Q(qr_code__iexact=linen_code) | Q(linen_code__iexact=linen_code))
    except LinenItem.DoesNotExist:
        return False, f"Unknown QR code '{linen_code}'."

    now = timezone.now()
    linen.status = 'READY_FOR_REISSUE'
    linen.current_location = "Central Linen Depot - Ready Dispatch Racks"
    linen.save()

    LinenLifecycleEvent.objects.create(
        linen=linen,
        event_type='READY_FOR_REISSUE',
        timestamp=now,
        location=linen.current_location,
        performed_by=user,
        notes="Quality check passed. Packaged in sanitized kit for next train."
    )

    return True, f"Linen {linen.linen_code} is now READY FOR REISSUE."


def get_analytics_data():
    """
    Gathers comprehensive analytics for dashboard and reports:
    - Overall counts (Total, Issued, Returned, Unaccounted, Laundry)
    - Train-wise analytics with risk calculations
    - Coach loss hotspots
    - Linen type breakdown
    """
    total = LinenItem.objects.count()
    issued = LinenItem.objects.filter(status='ISSUED').count()
    returned = LinenItem.objects.filter(status='RETURNED').count()
    unaccounted = LinenItem.objects.filter(status__in=['UNACCOUNTED', 'INVESTIGATION_REQUIRED']).count()
    in_laundry = LinenItem.objects.filter(status__in=['IN_LAUNDRY', 'RECEIVED_AT_LAUNDRY', 'WASHING']).count()
    ready_for_reissue = LinenItem.objects.filter(status='READY_FOR_REISSUE').count()

    # Train analytics
    trains_data = []
    for train in Train.objects.all():
        sessions = CollectionSession.objects.filter(train=train)
        expected = sum(s.expected_quantity for s in sessions)
        scanned = sum(s.scanned_quantity for s in sessions)
        missing = sum(s.missing_quantity for s in sessions)

        # In case no sessions yet, count assignments
        if expected == 0:
            assignments = LinenAssignment.objects.filter(train=train)
            expected = assignments.count()
            scanned = assignments.filter(assignment_status='RETURNED').count()
            missing = assignments.filter(assignment_status='UNACCOUNTED').count()

        loss_percentage = round((missing / expected * 100), 1) if expected > 0 else 0.0

        # Risk level: 0-1% LOW, 1-5% MEDIUM, >5% HIGH
        if loss_percentage > 5.0:
            risk = 'HIGH'
            risk_class = 'danger'
        elif loss_percentage >= 1.0:
            risk = 'MEDIUM'
            risk_class = 'warning'
        else:
            risk = 'LOW'
            risk_class = 'success'

        trains_data.append({
            'train': train,
            'expected': expected,
            'returned': scanned,
            'unaccounted': missing,
            'loss_percentage': loss_percentage,
            'risk': risk,
            'risk_class': risk_class,
        })

    # Coach hotspots
    coach_hotspots = []
    for coach in Coach.objects.all().select_related('train'):
        sessions = CollectionSession.objects.filter(coach=coach)
        missing = sum(s.missing_quantity for s in sessions)
        expected = sum(s.expected_quantity for s in sessions)
        if expected == 0:
            assignments = LinenAssignment.objects.filter(coach=coach)
            expected = assignments.count()
            missing = assignments.filter(assignment_status='UNACCOUNTED').count()

        rate = round((missing / expected * 100), 1) if expected > 0 else 0.0
        
        coach_hotspots.append({
            'coach': coach,
            'train': coach.train,
            'expected': expected,
            'unaccounted': missing,
            'rate': rate,
            'is_hotspot': missing >= 3 or rate > 5.0
        })

    coach_hotspots.sort(key=lambda x: x['unaccounted'], reverse=True)

    # Linen type loss breakdown
    type_loss = []
    for ltype, label in LinenItem.LINEN_TYPE_CHOICES:
        count = LinenItem.objects.filter(linen_type=ltype, status__in=['UNACCOUNTED', 'INVESTIGATION_REQUIRED']).count()
        total_type = LinenItem.objects.filter(linen_type=ltype).count()
        type_loss.append({
            'type': label,
            'unaccounted': count,
            'total': total_type
        })

    return {
        'total': total,
        'issued': issued,
        'returned': returned,
        'unaccounted': unaccounted,
        'in_laundry': in_laundry,
        'ready_for_reissue': ready_for_reissue,
        'trains_data': trains_data,
        'coach_hotspots': coach_hotspots,
        'type_loss': type_loss,
    }


def get_or_create_coach_handoff(attendant_user):
    """
    Returns the active CoachHandOff for the attendant assigned by the supervisor.
    Prioritizes the most recently updated or created assignment.
    """
    handoff = CoachHandOff.objects.filter(
        attendant=attendant_user
    ).order_by('-updated_at', '-date', '-id').first()

    if not handoff:
        train = Train.objects.filter(train_number='12760').first() or Train.objects.first()
        coach = Coach.objects.filter(train=train, coach_number='B2').first() or Coach.objects.filter(train=train).first()
        handoff = CoachHandOff.objects.create(
            attendant=attendant_user,
            train=train,
            coach=coach,
            shift='Morning',
            bedsheets_handed_over=100,
            status='CONFIRMED',
            date=timezone.now().date()
        )
    return handoff


def register_manufacturer_linen(manufacturer_qr, linen_type='Bedsheet', user=None):
    """
    Scans directly attached manufacturer QR code into depot inventory.
    Only items registered here can be issued by attendants.
    """
    clean_code = manufacturer_qr.strip().upper()
    existing = LinenItem.objects.filter(Q(linen_code__iexact=clean_code) | Q(qr_code__iexact=clean_code)).first()
    if existing:
        # If already exists and not issued, confirm location in depot
        if existing.status in ['REGISTERED', 'READY_FOR_REISSUE', 'RETURNED']:
            existing.status = 'READY_FOR_REISSUE'
            existing.current_location = 'Central Depot Inventory - Ready for Distribution'
            existing.linen_type = linen_type
            existing.save()
        return existing, False

    item = LinenItem.objects.create(
        linen_code=clean_code,
        qr_code=clean_code,
        linen_type=linen_type,
        status='READY_FOR_REISSUE',
        current_location='Central Depot Inventory - Ready for Distribution'
    )

    LinenLifecycleEvent.objects.create(
        linen=item,
        event_type='REGISTERED',
        timestamp=timezone.now(),
        location='Central Depot Inventory - Ready for Distribution',
        performed_by=user,
        notes=f"Manufacturer QR code {clean_code} scanned into depot inventory as {linen_type}."
    )
    return item, True


def generate_laundry_linen_items(linen_type, count=1, user=None):
    """
    Generates new unique linen items from Laundry login directly into Depot stock.
    Supports single item, batch of items, or full passenger kit (Bedsheet, Blanket, Towel, Pillow Cover).
    Returns list of created LinenItem instances.
    """
    prefix_map = {
        'Bedsheet': 'BS',
        'Blanket': 'BL',
        'Towel': 'TW',
        'Pillow Cover': 'PC',
    }

    types_to_create = []
    if linen_type in ['KIT', 'COMPLETE_KIT', 'SET', 'ALL']:
        types_to_create = ['Bedsheet', 'Blanket', 'Towel', 'Pillow Cover'] * max(1, count)
    else:
        norm_type = linen_type if linen_type in prefix_map else 'Bedsheet'
        types_to_create = [norm_type] * max(1, count)

    created_items = []
    year = timezone.now().year

    for l_type in types_to_create:
        prefix = prefix_map.get(l_type, 'BS')
        counter = LinenItem.objects.filter(linen_type=l_type).count() + 1
        code_candidate = f"{prefix}-{year}-{counter:05d}"
        while LinenItem.objects.filter(Q(linen_code__iexact=code_candidate) | Q(qr_code__iexact=code_candidate)).exists():
            counter += 1
            code_candidate = f"{prefix}-{year}-{counter:05d}"

        item = LinenItem.objects.create(
            linen_code=code_candidate,
            qr_code=code_candidate,
            linen_type=l_type,
            status='READY_FOR_REISSUE',
            current_location='Central Depot Inventory - Ready for Distribution'
        )
        LinenLifecycleEvent.objects.create(
            linen=item,
            event_type='REGISTERED',
            timestamp=timezone.now(),
            location='Central Depot Inventory - Ready for Distribution',
            performed_by=user,
            notes=f"Linen ID {code_candidate} generated by Laundry intake as {l_type} (Ready for Coach Issuance)."
        )
        created_items.append(item)

    return created_items


def get_next_linen_code(linen_type):
    """
    Generates a deterministic next linen code suitable for split-flap departure board preview.
    Example: BS-2026-04825 -> BS-2026-04826
    """
    prefix_map = {
        'Bedsheet': 'BS',
        'Blanket': 'BL',
        'Towel': 'TW',
        'Pillow Cover': 'PC',
    }
    prefix = prefix_map.get(linen_type, 'BS')
    year = timezone.now().year
    count = LinenItem.objects.filter(linen_type=linen_type).count() + 1
    # Example format: BS-2026-04826
    return f"{prefix}-{year}-{count:05d}"


def get_coach_passengers(train, coach):
    """
    Fetches comprehensive passenger roster list for the given coach,
    sorted by berth number (numerically).
    Includes passenger details, masked PNR, route, age/gender,
    assigned linen status, and deboarding indicator.
    """
    passengers = list(PassengerPNR.objects.filter(train=train, coach=coach))
    # Sort numerically by berth if digits, otherwise string sort
    passengers.sort(key=lambda p: int(p.berth) if str(p.berth).isdigit() else 999)

    items = []
    for p in passengers:
        clean_pnr = p.pnr_number.strip().replace('-', '')
        masked_pnr = f"••••{clean_pnr[-4:]}" if len(clean_pnr) >= 4 else f"••••{clean_pnr}"

        # Parse age/gender if not directly set
        age = p.passenger_age
        gender = p.passenger_gender
        if not age or not gender:
            label = p.passenger_label or ''
            if '(' in label and ')' in label:
                sub = label.split('(')[-1].split(')')[0]
                if '/' in sub:
                    parts = sub.split('/')
                    if not gender:
                        gender = parts[0].strip()
                    if not age and parts[1].strip().isdigit():
                        age = int(parts[1].strip())

        # Retrieve any linen assignments for this passenger / berth
        assignments = LinenAssignment.objects.filter(
            coach=coach,
            berth=p.berth
        ).select_related('linen')

        assigned_linen = []
        for a in assignments:
            assigned_linen.append({
                'code': a.linen.linen_code,
                'type': a.linen.linen_type,
                'status': a.assignment_status,
                'is_returned': (a.assignment_status == 'RETURNED'),
            })

        has_issued_linen = (p.boarding_status == 'Issued') or any(a['status'] == 'ACTIVE' for a in assigned_linen)
        is_deboarding_soon = ('Secunderabad' in (p.destination_station or '')) or (p.expected_arrival_time == '06:20')

        items.append({
            'id': p.id,
            'pnr_number': p.pnr_number,
            'masked_pnr': masked_pnr,
            'berth': p.berth,
            'berth_type': p.berth_type,
            'passenger_name': p.passenger_name or p.passenger_label.split(' (')[0],
            'passenger_age': age,
            'passenger_gender': gender,
            'source_station': p.source_station,
            'destination_station': p.destination_station,
            'departure_time': p.departure_time,
            'expected_arrival_time': p.expected_arrival_time,
            'status': p.boarding_status or 'Boarding now',
            'ticket_status': p.status or 'CNF / Confirmed',
            'assigned_linen': assigned_linen,
            'has_issued_linen': has_issued_linen,
            'is_deboarding_soon': is_deboarding_soon,
            'primary_linen_code': assigned_linen[0]['code'] if assigned_linen else None,
        })
    return items



def get_deboarding_passengers(train, coach, minutes_threshold=20):
    """
    Identifies passengers in the given coach who are deboarding within the next 20 minutes
    (e.g., at the upcoming stop: Secunderabad Junction, ETA 06:20 / ~18 mins remaining).
    Also attaches their issued linen items so the attendant can directly sweep and scan them.
    """
    secunderabad_passengers = PassengerPNR.objects.filter(
        train=train,
        coach=coach,
        destination_station__icontains='Secunderabad'
    ).order_by('berth')

    if secunderabad_passengers.exists():
        target_passengers = list(secunderabad_passengers)
    else:
        target_passengers = list(PassengerPNR.objects.filter(train=train, coach=coach).order_by('expected_arrival_time', 'berth')[:2])

    deboarding_list = []
    for idx, p in enumerate(target_passengers):
        clean_pnr = p.pnr_number.strip().replace('-', '')
        masked_pnr = f"••••{clean_pnr[-4:]}" if len(clean_pnr) >= 4 else f"••••{clean_pnr}"
        
        # Check active linen assignments for this passenger / berth
        assignments = LinenAssignment.objects.filter(
            coach=coach,
            berth=p.berth
        ).select_related('linen')

        assigned_linen = []
        for a in assignments:
            assigned_linen.append({
                'code': a.linen.linen_code,
                'type': a.linen.linen_type,
                'status': a.assignment_status,
                'is_returned': (a.assignment_status == 'RETURNED'),
            })

        if not assigned_linen:
            continue

        primary_code = assigned_linen[0]['code'] if assigned_linen else f"BL-{p.berth}01"
        primary_type = assigned_linen[0]['type'] if assigned_linen else "Blanket"
        is_collected = any(item.get('is_returned', False) for item in assigned_linen) if assigned_linen else False

        if is_collected:
            continue

        deboarding_list.append({
            'id': p.id,
            'pnr_number': p.pnr_number,
            'masked_pnr': masked_pnr,
            'berth': p.berth,
            'berth_type': p.berth_type,
            'passenger_name': p.passenger_name or p.passenger_label,
            'destination_station': p.destination_station or 'Secunderabad (SC)',
            'expected_arrival_time': p.expected_arrival_time or '06:20',
            'minutes_remaining': 18 - (idx * 2),
            'assigned_linen': assigned_linen,
            'primary_code': primary_code,
            'primary_type': primary_type,
            'is_collected': is_collected,
            'status': 'Collected' if is_collected else 'Deboarding in 18m',
        })

    return deboarding_list


