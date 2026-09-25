from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('SUPERVISOR', 'Supervisor'),
        ('ADMIN', 'Supervisor (Admin)'),
        ('ATTENDANT', 'Attendant'),
        ('ATTENDER', 'Train Attendant'),
        ('LAUNDRY', 'Laundry Staff'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SUPERVISOR')
    badge_number = models.CharField(max_length=50, blank=True, null=True)
    zone = models.CharField(max_length=100, default='South Central Railway (SCR)')

    def get_normalized_role(self):
        if self.role in ['ADMIN', 'SUPERVISOR']:
            return 'SUPERVISOR'
        if self.role in ['ATTENDER', 'ATTENDANT']:
            return 'ATTENDANT'
        if self.role == 'LAUNDRY':
            return 'LAUNDRY'
        return 'ATTENDANT'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Train(models.Model):
    train_number = models.CharField(max_length=20, unique=True)
    train_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    class Meta:
        ordering = ['train_number']

    def __str__(self):
        return f"{self.train_number} - {self.train_name}"


class Coach(models.Model):
    COACH_TYPE_CHOICES = [
        ('1A', 'AC 1st Class (1A)'),
        ('2A', 'AC 2 Tier (2A)'),
        ('3A', 'AC 3 Tier (3A)'),
        ('3E', 'AC 3 Economy (3E)'),
        ('SL', 'Sleeper (SL)'),
    ]
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='coaches')
    coach_number = models.CharField(max_length=10)  # e.g. B1, B2, A1
    coach_type = models.CharField(max_length=20, choices=COACH_TYPE_CHOICES, default='3A')

    class Meta:
        ordering = ['train', 'coach_number']
        unique_together = ('train', 'coach_number')

    def __str__(self):
        return f"{self.train.train_number} / Coach {self.coach_number} ({self.coach_type})"


class LinenItem(models.Model):
    LINEN_TYPE_CHOICES = [
        ('Bedsheet', 'Bedsheet'),
        ('Blanket', 'Blanket'),
        ('Towel', 'Towel'),
        ('Pillow Cover', 'Pillow Cover'),
    ]

    STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('IN_LAUNDRY', 'In Laundry'),
        ('DISPATCHED', 'Dispatched'),
        ('IN_TRANSIT', 'In Transit'),
        ('LOADED_TO_TRAIN', 'Loaded to Train'),
        ('ASSIGNED', 'Assigned'),
        ('ISSUED', 'Issued'),
        ('COLLECTION_PENDING', 'Collection Pending'),
        ('RETURNED', 'Returned'),
        ('RECEIVED_AT_LAUNDRY', 'Received at Laundry'),
        ('WASHING', 'Washing'),
        ('READY_FOR_REISSUE', 'Ready for Reissue'),
        ('UNACCOUNTED', 'Unaccounted'),
        ('INVESTIGATION_REQUIRED', 'Investigation Required'),
    ]

    linen_code = models.CharField(max_length=50, unique=True, db_index=True)
    qr_code = models.CharField(max_length=100, unique=True, db_index=True)
    linen_type = models.CharField(max_length=50, choices=LINEN_TYPE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='REGISTERED')
    current_location = models.CharField(max_length=200, default='Central Railway Laundry')
    settlement_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('CHARGED', 'Charged'), ('WAIVED', 'Waived')],
        default='PENDING'
    )
    settlement_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.linen_code} ({self.linen_type}) - {self.status}"

    @property
    def latest_assignment(self):
        return self.assignments.order_by('-issued_at').first()

    def get_last_verified_checkpoint(self):
        """
        Calculates the last verified checkpoint and stage where the physical item was verified.
        Never blames or accuses anyone; strictly identifies the last confirmed operational stage.
        """
        verified_event_types = [
            'REGISTERED', 'LAUNDRY_RECEIVED', 'DISPATCHED', 'TRAIN_LOADED',
            'COACH_ASSIGNED', 'BERTH_ASSIGNED', 'ISSUED_TO_PASSENGER',
            'RETURNED_BY_PASSENGER', 'COLLECTED_BY_ATTENDER',
            'RECEIVED_AT_LAUNDRY', 'WASHING', 'READY_FOR_REISSUE'
        ]
        
        last_event = self.lifecycle_events.filter(
            event_type__in=verified_event_types
        ).order_by('-timestamp', '-id').first()

        if not last_event:
            return {
                'stage': 'Registration',
                'location': self.current_location or 'Central Laundry',
                'timestamp': self.created_at,
                'performed_by': 'System Auto',
                'next_expected': 'Laundry Processing / Train Loading',
                'notes': 'Item was registered in system.'
            }

        next_expected_map = {
            'REGISTERED': 'Laundry Processing / Dispatch',
            'LAUNDRY_RECEIVED': 'Washing / Quality Inspection',
            'DISPATCHED': 'Train Loading & Distribution',
            'TRAIN_LOADED': 'Coach Allocation',
            'COACH_ASSIGNED': 'Berth Setup / Passenger Issuance',
            'BERTH_ASSIGNED': 'Issued to Passenger',
            'ISSUED_TO_PASSENGER': 'Attender Collection at Destination/End-of-Trip',
            'RETURNED_BY_PASSENGER': 'Attender QR Scan Confirmation',
            'COLLECTED_BY_ATTENDER': 'Laundry Handover at Terminal',
            'RECEIVED_AT_LAUNDRY': 'Commercial Washing Cycle',
            'WASHING': 'Sanitization & Packaging for Reissue',
            'READY_FOR_REISSUE': 'Next Train Dispatch'
        }

        location_str = last_event.location
        if last_event.coach and last_event.berth:
            location_str = f"Coach {last_event.coach.coach_number} / Berth {last_event.berth}"
        elif last_event.coach:
            location_str = f"Coach {last_event.coach.coach_number}"
        elif last_event.train:
            location_str = f"Train {last_event.train.train_number}"

        return {
            'event': last_event,
            'stage': last_event.get_event_type_display(),
            'location': location_str or self.current_location,
            'timestamp': last_event.timestamp,
            'performed_by': last_event.performed_by.username if last_event.performed_by else 'Staff / Attender',
            'next_expected': next_expected_map.get(last_event.event_type, 'Attender Collection'),
            'notes': last_event.notes or 'Routine operational checkpoint passed.'
        }


class PassengerPNR(models.Model):
    pnr_number = models.CharField(max_length=30, unique=True, db_index=True)
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='passengers')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='passengers')
    berth = models.CharField(max_length=10)
    berth_type = models.CharField(max_length=30, default='Lower Berth')
    source_station = models.CharField(max_length=100, default='New Delhi (NDLS)')
    destination_station = models.CharField(max_length=100, default='Hyderabad (HYB)')
    journey_date = models.DateField(default=timezone.now)
    departure_time = models.CharField(max_length=20, default='20:00')
    expected_arrival_time = models.CharField(max_length=20, default='06:30')
    passenger_label = models.CharField(max_length=100, default='Passenger 1 (Adult)')
    passenger_name = models.CharField(max_length=120, blank=True, default='')
    passenger_age = models.PositiveIntegerField(null=True, blank=True)
    passenger_gender = models.CharField(max_length=20, blank=True, default='')
    passenger_phone = models.CharField(max_length=30, blank=True, default='')
    passenger_email = models.EmailField(blank=True, default='')
    passenger_address = models.TextField(blank=True, default='')
    ticket_image = models.ImageField(upload_to='passenger_tickets/', blank=True, null=True)
    status = models.CharField(max_length=30, default='CNF / Confirmed')
    boarding_status = models.CharField(
        max_length=30,
        choices=[
            ('Issued', 'Issued'),
            ('Boarding now', 'Boarding now'),
            ('Not boarded', 'Not boarded'),
        ],
        default='Boarding now'
    )

    def __str__(self):
        return f"{self.pnr_number} - {self.train.train_number} / {self.coach.coach_number} / Berth {self.berth} ({self.source_station} -> {self.destination_station})"


class LinenAssignment(models.Model):
    ASSIGNMENT_STATUS_CHOICES = [
        ('ACTIVE', 'Active / In Journey'),
        ('RETURNED', 'Returned'),
        ('UNACCOUNTED', 'Unaccounted'),
    ]

    linen = models.ForeignKey(LinenItem, on_delete=models.CASCADE, related_name='assignments')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='assignments')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='assignments')
    berth = models.CharField(max_length=10)
    passenger_reference = models.CharField(max_length=50, default='PNR-1001')  # PNR reference
    source_station = models.CharField(max_length=100, default='New Delhi (NDLS)')
    destination_station = models.CharField(max_length=100, default='Hyderabad (HYB)')
    journey_date = models.DateField(default=timezone.now)
    issued_at = models.DateTimeField(default=timezone.now)
    expected_collection_time = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    assignment_status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='ACTIVE')

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.linen.linen_code} -> Train {self.train.train_number}, Coach {self.coach.coach_number}, Berth {self.berth} ({self.passenger_reference})"


class LinenLifecycleEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('REGISTERED', 'Registered in System'),
        ('LAUNDRY_RECEIVED', 'Laundry Received'),
        ('DISPATCHED', 'Dispatched from Laundry'),
        ('IN_TRANSIT', 'In Transit to Station'),
        ('TRAIN_LOADED', 'Loaded to Train'),
        ('COACH_ASSIGNED', 'Assigned to Coach'),
        ('BERTH_ASSIGNED', 'Assigned to Berth'),
        ('ISSUED_TO_PASSENGER', 'Issued to Passenger'),
        ('COLLECTION_STARTED', 'Collection Session Started'),
        ('RETURNED_BY_PASSENGER', 'Returned by Passenger'),
        ('COLLECTED_BY_ATTENDER', 'Collected by Attender'),
        ('HANDOVER_TO_LAUNDRY', 'Handover to Laundry'),
        ('RECEIVED_AT_LAUNDRY', 'Received at Laundry Station'),
        ('WASHING', 'In Washing Cycle'),
        ('READY_FOR_REISSUE', 'Ready for Reissue'),
        ('UNACCOUNTED', 'Item Unaccounted / Missing at Checkpoint'),
        ('INVESTIGATION_REQUIRED', 'Investigation Flagged'),
    ]

    linen = models.ForeignKey(LinenItem, on_delete=models.CASCADE, related_name='lifecycle_events')
    event_type = models.CharField(max_length=40, choices=EVENT_TYPE_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    location = models.CharField(max_length=200)
    train = models.ForeignKey(Train, on_delete=models.SET_NULL, null=True, blank=True)
    coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)
    berth = models.CharField(max_length=10, blank=True, null=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{timezone.localtime(self.timestamp).strftime('%H:%M %d-%b')}] {self.linen.linen_code} - {self.get_event_type_display()}"


class CollectionSession(models.Model):
    SESSION_STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DISCREPANCY', 'Discrepancy Detected'),
    ]

    attender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_sessions')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='collection_sessions')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='collection_sessions')
    journey_date = models.DateField(default=timezone.now)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    expected_quantity = models.IntegerField(default=0)
    scanned_quantity = models.IntegerField(default=0)
    missing_quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='IN_PROGRESS')

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Collection {self.train.train_number} Coach {self.coach.coach_number} ({self.status})"

    def calculate_discrepancy(self):
        self.missing_quantity = max(0, self.expected_quantity - self.scanned_quantity)
        if self.missing_quantity > 0:
            self.status = 'DISCREPANCY'
        else:
            self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()
        return self.missing_quantity


class CollectionScan(models.Model):
    RESULT_CHOICES = [
        ('SUCCESS', 'Success - Verified & Returned'),
        ('ALREADY_RETURNED', 'Warning - Already Returned'),
        ('WRONG_COACH', 'Warning - Assigned to Different Coach'),
        ('WRONG_TRAIN', 'Warning - Assigned to Different Train'),
        ('NOT_ASSIGNED', 'Warning - Linen Not Assigned'),
        ('UNKNOWN_QR', 'Error - Unknown QR Code'),
        ('DUPLICATE_SCAN', 'Warning - Duplicate Scan in Current Session'),
    ]

    collection_session = models.ForeignKey(CollectionSession, on_delete=models.CASCADE, related_name='scans')
    linen = models.ForeignKey(LinenItem, on_delete=models.SET_NULL, null=True, blank=True)
    scanned_qr = models.CharField(max_length=100, default='')
    scanned_at = models.DateTimeField(default=timezone.now)
    scanned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.CharField(max_length=30, choices=RESULT_CHOICES)
    message = models.CharField(max_length=255)

    class Meta:
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.scanned_qr} -> {self.result} at {timezone.localtime(self.scanned_at).strftime('%H:%M:%S')}"


class CoachHandOff(models.Model):
    SHIFT_CHOICES = [
        ('Morning', 'Morning'),
        ('Evening', 'Evening'),
        ('Night', 'Night'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
    ]
    attendant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='handoffs')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='handoffs')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='handoffs')
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='Morning')
    bedsheets_handed_over = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'train', 'coach']

    def __str__(self):
        return f"{self.attendant.username} - {self.train.train_number}/{self.coach.coach_number} ({self.shift}) - {self.bedsheets_handed_over} bedsheets"
