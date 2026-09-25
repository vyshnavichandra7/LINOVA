import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from linen.models import (
    UserProfile, Train, Coach, LinenItem, LinenAssignment,
    LinenLifecycleEvent, CollectionSession, CollectionScan, PassengerPNR, CoachHandOff
)


class Command(BaseCommand):
    help = 'Seeds complete prototype data for LinenGuard operational demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing LinenGuard Seed Data..."))

        # 1. Clean existing data for clean demo state
        CoachHandOff.objects.all().delete()
        CollectionScan.objects.all().delete()
        CollectionSession.objects.all().delete()
        LinenLifecycleEvent.objects.all().delete()
        LinenAssignment.objects.all().delete()
        PassengerPNR.objects.all().delete()
        LinenItem.objects.all().delete()
        Coach.objects.all().delete()
        Train.objects.all().delete()

        # 2. Create Demo Users with Zone Information
        users_config = [
            ('admin', 'admin123', 'admin@linenguard.railways.gov.in', 'ADMIN', 'EMP-ADM-01', 'South Central Railway (SCR)', 'V. Sharma (Supervisor)'),
            ('attender', 'attender123', 'rahul.attender@railways.gov.in', 'ATTENDER', 'ATT-B2-8821', 'South Central Railway (SCR)', 'Rahul Sharma'),
            ('attender2', 'attender123', 'sanjay.attender@railways.gov.in', 'ATTENDER', 'ATT-B1-4019', 'South Central Railway (SCR)', 'Sanjay Kumar'),
            ('attender3', 'attender123', 'vikas.attender@railways.gov.in', 'ATTENDER', 'ATT-B3-6112', 'South Central Railway (SCR)', 'Vikas Patel'),
            ('attender4', 'attender123', 'pooja.attender@railways.gov.in', 'ATTENDER', 'ATT-A1-2204', 'South Central Railway (SCR)', 'Pooja Verma'),
            ('laundry', 'laundry123', 'sunil.laundry@railways.gov.in', 'LAUNDRY', 'LND-STN-401', 'South Central Railway (SCR)', 'Sunil Rawat (Laundry)'),
        ]

        created_users = {}
        for username, password, email, role, badge, zone, full_name in users_config:
            user, created = User.objects.get_or_create(username=username, email=email)
            user.set_password(password)
            user.is_staff = (role == 'ADMIN')
            user.is_superuser = (role == 'ADMIN')
            names = full_name.split(' ', 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ''
            user.save()

            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': role, 'badge_number': badge, 'zone': zone}
            )
            created_users[username] = user
            self.stdout.write(self.style.SUCCESS(f"User created: {username} ({full_name}, Badge: {badge}, Zone: {zone})"))

        admin_user = created_users['admin']
        attender_user = created_users['attender']
        attender2_user = created_users['attender2']
        attender3_user = created_users['attender3']
        attender4_user = created_users['attender4']
        laundry_user = created_users['laundry']

        # 3. Create Trains
        trains_data = [
            ('12760', 'Demo Express', 'New Delhi (NDLS)', 'Hyderabad (HYB)'),
            ('12761', 'Dakshin Superfast', 'Secunderabad (SC)', 'Chennai Central (MAS)'),
            ('12762', 'Telangana Express', 'Hyderabad (HYB)', 'New Delhi (NDLS)'),
        ]

        train_objects = {}
        for number, name, src, dst in trains_data:
            train = Train.objects.create(
                train_number=number,
                train_name=name,
                source=src,
                destination=dst
            )
            train_objects[number] = train

        t12760 = train_objects['12760']
        t12761 = train_objects['12761']
        t12762 = train_objects['12762']

        # 4. Create Coaches
        coaches_map = {}
        for train in [t12760, t12761, t12762]:
            coaches_map[train.train_number] = {}
            for coach_num in ['B1', 'B2', 'B3']:
                c = Coach.objects.create(
                    train=train,
                    coach_number=coach_num,
                    coach_type='3A'
                )
                coaches_map[train.train_number][coach_num] = c

        # Extra coach A1 for train 12760
        cA1 = Coach.objects.create(train=t12760, coach_number='A1', coach_type='2A')
        coaches_map['12760']['A1'] = cA1

        self.stdout.write(self.style.SUCCESS("Created 3 trains and 10 coaches."))

        # 4b. Create Passenger PNR Records across multiple coaches
        pnr_demo_records = [
            # Train 12760 - Coach B2
            ('PNR-4821', t12760, coaches_map['12760']['B2'], '24', 'Lower Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'R. Sharma (M/42)', 'Issued'),
            ('PNR-7710', t12760, coaches_map['12760']['B2'], '25', 'Middle Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'A. Verma (M/31)', 'Boarding now'),
            ('PNR-1001', t12760, coaches_map['12760']['B2'], '36', 'Lower Berth', 'New Delhi (NDLS)', 'Hyderabad (HYB)', '20:15', '06:45', 'Rajesh Kumar (M/38)', 'Boarding now'),
            ('PNR-1042', t12760, coaches_map['12760']['B2'], '41', 'Middle Berth', 'New Delhi (NDLS)', 'Bhopal (BPL)', '20:15', '03:10', 'Sneha Sharma (F/29)', 'Boarding now'),
            ('PNR-1012', t12760, coaches_map['12760']['B2'], '12', 'Side Lower', 'New Delhi (NDLS)', 'Nagpur (NGP)', '20:15', '04:30', 'Amit Patel (M/45)', 'Not boarded'),
            ('2418901234', t12760, coaches_map['12760']['B2'], '38', 'Side Upper', 'New Delhi (NDLS)', 'Hyderabad (HYB)', '20:15', '06:45', 'K. Venkat (M/41)', 'Not boarded'),
            ('DEMO-B2-4901', t12760, coaches_map['12760']['B2'], '90', 'Lower Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Nisha Kapoor (F/30)', 'Boarding now'),
            ('DEMO-B2-4902', t12760, coaches_map['12760']['B2'], '91', 'Middle Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Rohan Malhotra (M/36)', 'Boarding now'),
            ('DEMO-B2-4903', t12760, coaches_map['12760']['B2'], '92', 'Upper Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Ishita Rao (F/27)', 'Boarding now'),

            # Train 12760 - Coach B1 (Allocated to Sanjay Kumar / attender2)
            ('PNR-5521', t12760, coaches_map['12760']['B1'], '12', 'Side Lower', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Vikram Rao (M/35)', 'Boarding now'),
            ('PNR-5532', t12760, coaches_map['12760']['B1'], '18', 'Lower Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Ananya Sen (F/28)', 'Boarding now'),
            ('PNR-5544', t12760, coaches_map['12760']['B1'], '24', 'Middle Berth', 'New Delhi (NDLS)', 'Hyderabad (HYB)', '20:15', '06:45', 'Mohan Lal (M/52)', 'Boarding now'),
            ('PNR-5567', t12760, coaches_map['12760']['B1'], '36', 'Upper Berth', 'New Delhi (NDLS)', 'Hyderabad (HYB)', '20:15', '06:45', 'Divya Nair (F/31)', 'Not boarded'),
            ('PNR-5589', t12760, coaches_map['12760']['B1'], '42', 'Side Upper', 'New Delhi (NDLS)', 'Nagpur (NGP)', '20:15', '04:30', 'Karthik S (M/29)', 'Not boarded'),

            # Train 12760 - Coach B3 (Allocated to Vikas Patel / attender3)
            ('PNR-6611', t12760, coaches_map['12760']['B3'], '15', 'Lower Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Harish Gupta (M/47)', 'Boarding now'),
            ('PNR-6623', t12760, coaches_map['12760']['B3'], '21', 'Middle Berth', 'New Delhi (NDLS)', 'Hyderabad (HYB)', '20:15', '06:45', 'Meena Kumari (F/40)', 'Boarding now'),
            ('PNR-6645', t12760, coaches_map['12760']['B3'], '33', 'Upper Berth', 'New Delhi (NDLS)', 'Bhopal (BPL)', '20:15', '03:10', 'Deepak Joshi (M/32)', 'Boarding now'),
            ('PNR-6678', t12760, coaches_map['12760']['B3'], '45', 'Side Lower', 'New Delhi (NDLS)', 'Nagpur (NGP)', '20:15', '04:30', 'Sunita Rani (F/55)', 'Not boarded'),

            # Train 12760 - Coach A1 (Allocated to Pooja Verma / attender4)
            ('PNR-8812', t12760, coaches_map['12760']['A1'], '04', 'Lower Berth', 'New Delhi (NDLS)', 'Hyderabad (HYB)', '20:15', '06:45', 'Dr. Arvind Swamy (M/60)', 'Boarding now'),
            ('PNR-8834', t12760, coaches_map['12760']['A1'], '08', 'Upper Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Preeti Menon (F/34)', 'Boarding now'),
            ('PNR-8856', t12760, coaches_map['12760']['A1'], '16', 'Lower Berth', 'New Delhi (NDLS)', 'Secunderabad (SC)', '20:15', '06:20', 'Col. R. Rathore (M/58)', 'Boarding now'),

            # Other trains
            ('4529810372', t12761, coaches_map['12761']['B1'], '18', 'Lower Berth', 'Secunderabad (SC)', 'Chennai Central (MAS)', '19:30', '05:40', 'M. Anjali (F/26)', 'Boarding now'),
            ('6712390845', t12762, coaches_map['12762']['B2'], '52', 'Upper Berth', 'Hyderabad (HYB)', 'New Delhi (NDLS)', '06:00', '16:30', 'Suresh Verma (M/54)', 'Boarding now'),
        ]

        for pnr_num, trn, cch, brth, btype, src, dst, dep, arr, plabel, b_status in pnr_demo_records:
            names = plabel.split(' (')[0]
            PassengerPNR.objects.create(
                pnr_number=pnr_num,
                train=trn,
                coach=cch,
                berth=brth,
                berth_type=btype,
                source_station=src,
                destination_station=dst,
                departure_time=dep,
                expected_arrival_time=arr,
                passenger_label=plabel,
                passenger_name=names,
                status='CNF / Confirmed',
                boarding_status=b_status
            )

        # 4c. Create Supervisor Hand-Off Records: Allocating zone attendants to coaches & shifts
        now = timezone.now()
        CoachHandOff.objects.create(
            attendant=attender_user,
            train=t12760,
            coach=coaches_map['12760']['B2'],
            shift='Morning',
            bedsheets_handed_over=100,
            status='CONFIRMED',
            date=now.date()
        )
        CoachHandOff.objects.create(
            attendant=attender2_user,
            train=t12760,
            coach=coaches_map['12760']['B1'],
            shift='Evening',
            bedsheets_handed_over=100,
            status='CONFIRMED',
            date=now.date()
        )
        CoachHandOff.objects.create(
            attendant=attender3_user,
            train=t12760,
            coach=coaches_map['12760']['B3'],
            shift='Night',
            bedsheets_handed_over=90,
            status='PENDING',
            date=now.date()
        )
        CoachHandOff.objects.create(
            attendant=attender4_user,
            train=t12760,
            coach=coaches_map['12760']['A1'],
            shift='Morning',
            bedsheets_handed_over=60,
            status='CONFIRMED',
            date=now.date()
        )

        # 4d. Seed Pre-Registered Manufacturer Linen Items in Depot Inventory
        manufacturer_stock = [
            ('MFG-BS-90214', 'Bedsheet'),
            ('MFG-BS-90215', 'Bedsheet'),
            ('MFG-BL-40118', 'Blanket'),
            ('MFG-TW-33102', 'Towel'),
            ('MFG-PC-12095', 'Pillow Cover'),
        ]
        for mfg_code, mfg_type in manufacturer_stock:
            m_item = LinenItem.objects.create(
                linen_code=mfg_code,
                qr_code=mfg_code,
                linen_type=mfg_type,
                status='READY_FOR_REISSUE',
                current_location='Central Depot Inventory - Ready for Distribution'
            )
            LinenLifecycleEvent.objects.create(
                linen=m_item,
                event_type='REGISTERED',
                timestamp=now,
                location='Central Railway Depot Inventory',
                performed_by=laundry_user,
                notes=f"Manufacturer QR code {mfg_code} scanned and registered into depot inventory."
            )

        self.stdout.write(self.style.SUCCESS("Created pre-seeded Passenger PNR, CoachHandOff, and Manufacturer Inventory."))

        now = timezone.now()
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)

        # 5. FLAGSHIP DEMO SCENARIO: Train 12760, Coach B2
        # Exactly 100 expected linen items in the journey.
        # 94 returned items.
        # 6 unaccounted items with specified last verified checkpoints.
        coach_b2 = coaches_map['12760']['B2']

        self.stdout.write(self.style.NOTICE("Populating Flagship Demo Scenario for Train 12760, Coach B2..."))

        # Special flagship items:
        # Item 0: BS-2026-04825 - Bedsheet in Coach B2 ready to be assigned to Berth 25!
        bs_04825 = LinenItem.objects.create(
            linen_code='BS-2026-04825',
            qr_code='BS-2026-04825',
            linen_type='Bedsheet',
            status='LOADED_TO_TRAIN',
            current_location='Train 12760 / Coach B2'
        )

        # Item 1: BL-20561 - Assigned to Berth 36, PNR-1001. Live demo item ready to scan and return!
        bl_20561 = LinenItem.objects.create(
            linen_code='BL-20561',
            qr_code='BL-20561',
            linen_type='Blanket',
            status='ISSUED',
            current_location='Train 12760 / Coach B2 / Berth 36'
        )
        LinenLifecycleEvent.objects.create(
            linen=bl_20561,
            event_type='REGISTERED',
            timestamp=two_days_ago.replace(hour=10, minute=0, second=0),
            location='Central Railway Laundry',
            performed_by=laundry_user,
            notes='Initial registration.'
        )
        LinenLifecycleEvent.objects.create(
            linen=bl_20561,
            event_type='DISPATCHED',
            timestamp=yesterday.replace(hour=18, minute=0, second=0),
            location='Laundry Dispatch Bay 4',
            performed_by=laundry_user,
            notes='Dispatched for Train 12760.'
        )
        LinenLifecycleEvent.objects.create(
            linen=bl_20561,
            event_type='TRAIN_LOADED',
            timestamp=yesterday.replace(hour=20, minute=15, second=0),
            location='New Delhi Station - Platform 8 (Train 12760)',
            train=t12760,
            performed_by=attender_user,
            notes='Loaded into rake.'
        )
        LinenLifecycleEvent.objects.create(
            linen=bl_20561,
            event_type='COACH_ASSIGNED',
            timestamp=yesterday.replace(hour=20, minute=30, second=0),
            location='Coach B2',
            train=t12760,
            coach=coach_b2,
            performed_by=attender_user,
            notes='Distributed to Coach B2 storage.'
        )
        LinenLifecycleEvent.objects.create(
            linen=bl_20561,
            event_type='BERTH_ASSIGNED',
            timestamp=yesterday.replace(hour=20, minute=32, second=0),
            location='Coach B2 / Berth 36',
            train=t12760,
            coach=coach_b2,
            berth='36',
            performed_by=attender_user,
            notes='Allocated for Berth 36 passenger.'
        )
        LinenLifecycleEvent.objects.create(
            linen=bl_20561,
            event_type='ISSUED_TO_PASSENGER',
            timestamp=yesterday.replace(hour=20, minute=35, second=0),
            location='Coach B2 / Berth 36',
            train=t12760,
            coach=coach_b2,
            berth='36',
            performed_by=attender_user,
            notes='Sanitized blanket issued under PNR-1001.'
        )
        LinenAssignment.objects.create(
            linen=bl_20561,
            train=t12760,
            coach=coach_b2,
            berth='36',
            passenger_reference='PNR-1001',
            source_station='New Delhi (NDLS)',
            destination_station='Hyderabad (HYB)',
            journey_date=yesterday.date(),
            issued_at=yesterday.replace(hour=20, minute=35, second=0),
            expected_collection_time=now.replace(hour=6, minute=30, second=0),
            assignment_status='ACTIVE'
        )

        # Ready-to-deboard passengers with real collectable linen assignments.
        deboarding_linen = [
            ('DEMO-B2-4901-LINEN', 'Bedsheet', '90', 'DEMO-B2-4901', 'Nisha Kapoor'),
            ('DEMO-B2-4902-LINEN', 'Blanket', '91', 'DEMO-B2-4902', 'Rohan Malhotra'),
            ('DEMO-B2-4903-LINEN', 'Towel', '92', 'DEMO-B2-4903', 'Ishita Rao'),
        ]
        for code, linen_type, berth, pnr, passenger_name in deboarding_linen:
            linen = LinenItem.objects.create(
                linen_code=code,
                qr_code=code,
                linen_type=linen_type,
                status='ISSUED',
                current_location=f'Train 12760 / Coach B2 / Berth {berth}'
            )
            LinenAssignment.objects.create(
                linen=linen,
                train=t12760,
                coach=coach_b2,
                berth=berth,
                passenger_reference=pnr,
                source_station='New Delhi (NDLS)',
                destination_station='Secunderabad (SC)',
                journey_date=now.date(),
                issued_at=now,
                expected_collection_time=now + timedelta(hours=1),
                assignment_status='ACTIVE'
            )

        # 6 Unaccounted demo items:
        unaccounted_configs = [
            ('BL-20562', 'Blanket', '41', 'Coach B2 / Berth 41', 'ISSUED_TO_PASSENGER', yesterday.replace(hour=20, minute=40), 'PNR-1042', 'Berth 41'),
            ('BS-10246', 'Bedsheet', '36', 'Coach B2 / Berth 36', 'ISSUED_TO_PASSENGER', yesterday.replace(hour=20, minute=35), 'PNR-1001', 'Berth 36'),
            ('TW-30422', 'Towel', '', 'Coach B2 Entrance Rack', 'COACH_ASSIGNED', yesterday.replace(hour=20, minute=30), 'PNR-BATCH-01', 'Coach B2 Storage'),
            ('PC-40113', 'Pillow Cover', '12', 'Coach B2 / Berth 12', 'ISSUED_TO_PASSENGER', yesterday.replace(hour=20, minute=20), 'PNR-1012', 'Berth 12'),
            ('BS-10247', 'Bedsheet', '24', 'Coach B2 / Berth 24', 'ISSUED_TO_PASSENGER', yesterday.replace(hour=20, minute=25), 'PNR-1024', 'Berth 24'),
            ('BL-20563', 'Blanket', '', 'Coach B2 Linen Cabinet', 'COACH_ASSIGNED', yesterday.replace(hour=20, minute=30), 'PNR-BATCH-02', 'Coach B2 Cabinet'),
        ]

        unaccounted_items = []
        for code, ltype, berth, loc, last_event_type, event_time, pnr, last_label in unaccounted_configs:
            item = LinenItem.objects.create(
                linen_code=code,
                qr_code=code,
                linen_type=ltype,
                status='UNACCOUNTED',
                current_location=loc
            )
            # Register event
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='REGISTERED',
                timestamp=two_days_ago.replace(hour=10),
                location='Central Railway Laundry',
                performed_by=laundry_user,
                notes='Registered.'
            )
            # Dispatch event
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='DISPATCHED',
                timestamp=yesterday.replace(hour=18),
                location='Laundry Dispatch Bay 4',
                performed_by=laundry_user,
                notes='Dispatched.'
            )
            # Train loaded event
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='TRAIN_LOADED',
                timestamp=yesterday.replace(hour=20, minute=15),
                location='Platform 8 (Train 12760)',
                train=t12760,
                performed_by=attender_user,
                notes='Loaded.'
            )
            # Last verified event
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type=last_event_type,
                timestamp=event_time,
                location=loc,
                train=t12760,
                coach=coach_b2,
                berth=berth if berth else None,
                performed_by=attender_user,
                notes=f"Last confirmed checkpoint at {last_label}. Next expected event was Attender Collection."
            )
            # Unaccounted event
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='UNACCOUNTED',
                timestamp=now.replace(hour=7, minute=0, second=0),
                location=loc,
                train=t12760,
                coach=coach_b2,
                berth=berth if berth else None,
                performed_by=None,
                notes='Collection window closed with no return scan detected. Flagged for review.'
            )
            # Assignment
            LinenAssignment.objects.create(
                linen=item,
                train=t12760,
                coach=coach_b2,
                berth=berth if berth else '00',
                passenger_reference=pnr,
                source_station='New Delhi (NDLS)',
                destination_station='Hyderabad (HYB)',
                journey_date=yesterday.date(),
                issued_at=event_time,
                expected_collection_time=now.replace(hour=6, minute=30, second=0),
                assignment_status='UNACCOUNTED'
            )
            unaccounted_items.append(item)

        # 93 more items in Coach B2 that were successfully returned (making 94 returned with BL-20561 when scanned, or 93 already scanned):
        # We will create 93 already returned items for Coach B2:
        types_pool = ['Bedsheet', 'Blanket', 'Towel', 'Pillow Cover']
        returned_items = []
        for i in range(1, 94):
            ltype = types_pool[i % len(types_pool)]
            pfx = {'Bedsheet': 'BS', 'Blanket': 'BL', 'Towel': 'TW', 'Pillow Cover': 'PC'}[ltype]
            code = f"{pfx}-1{i:04d}"
            berth_num = str((i % 72) + 1)

            item = LinenItem.objects.create(
                linen_code=code,
                qr_code=code,
                linen_type=ltype,
                status='RETURNED',
                current_location=f"Collected in Coach B2 (In Transit to Laundry)"
            )
            # Events
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='REGISTERED',
                timestamp=two_days_ago.replace(hour=10),
                location='Central Railway Laundry',
                performed_by=laundry_user
            )
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='ISSUED_TO_PASSENGER',
                timestamp=yesterday.replace(hour=20, minute=30),
                location=f"Coach B2 / Berth {berth_num}",
                train=t12760,
                coach=coach_b2,
                berth=berth_num,
                performed_by=attender_user
            )
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='COLLECTED_BY_ATTENDER',
                timestamp=now.replace(hour=6, minute=35) - timedelta(minutes=(94 - i) % 30),
                location='Coach B2',
                train=t12760,
                coach=coach_b2,
                berth=berth_num,
                performed_by=attender_user,
                notes='Scanned and collected.'
            )
            LinenAssignment.objects.create(
                linen=item,
                train=t12760,
                coach=coach_b2,
                berth=berth_num,
                passenger_reference=f"PNR-20{i:02d}",
                source_station='New Delhi (NDLS)',
                destination_station='Hyderabad (HYB)',
                journey_date=yesterday.date(),
                issued_at=yesterday.replace(hour=20, minute=30),
                expected_collection_time=now.replace(hour=6, minute=30),
                returned_at=now.replace(hour=6, minute=35),
                assignment_status='RETURNED'
            )
            returned_items.append(item)

        # Create the flagship CollectionSession for Train 12760, Coach B2
        session_b2 = CollectionSession.objects.create(
            attender=attender_user,
            train=t12760,
            coach=coach_b2,
            journey_date=yesterday.date(),
            started_at=now.replace(hour=6, minute=0, second=0),
            completed_at=now.replace(hour=6, minute=50, second=0),
            expected_quantity=100,
            scanned_quantity=94,
            missing_quantity=6,
            status='DISCREPANCY'
        )

        # Add CollectionScan records for some returned items
        for item in returned_items[:20]:
            CollectionScan.objects.create(
                collection_session=session_b2,
                linen=item,
                scanned_qr=item.qr_code,
                scanned_at=now.replace(hour=6, minute=20),
                scanned_by=attender_user,
                result='SUCCESS',
                message='Successfully collected and verified'
            )

        # 6. Seed other coaches and trains to showcase analytics & hotspots
        # Train 12760:
        # Coach B1: 100 items, 99 returned, 1 unaccounted (LOW risk)
        coach_b1 = coaches_map['12760']['B1']
        CollectionSession.objects.create(
            attender=attender_user,
            train=t12760,
            coach=coach_b1,
            journey_date=yesterday.date(),
            started_at=now.replace(hour=5, minute=30),
            completed_at=now.replace(hour=6, minute=15),
            expected_quantity=100,
            scanned_quantity=99,
            missing_quantity=1,
            status='DISCREPANCY'
        )
        # Coach B3: 100 items, 100 returned, 0 unaccounted
        coach_b3 = coaches_map['12760']['B3']
        CollectionSession.objects.create(
            attender=attender_user,
            train=t12760,
            coach=coach_b3,
            journey_date=yesterday.date(),
            started_at=now.replace(hour=6, minute=15),
            completed_at=now.replace(hour=7, minute=0),
            expected_quantity=100,
            scanned_quantity=100,
            missing_quantity=0,
            status='COMPLETED'
        )
        # Coach A1: 50 items, 48 returned, 2 unaccounted
        CollectionSession.objects.create(
            attender=attender_user,
            train=t12760,
            coach=cA1,
            journey_date=yesterday.date(),
            started_at=now.replace(hour=6, minute=0),
            completed_at=now.replace(hour=6, minute=45),
            expected_quantity=50,
            scanned_quantity=48,
            missing_quantity=2,
            status='DISCREPANCY'
        )

        # Train 12761: 100 expected, 99 returned, 1 unaccounted (LOW)
        CollectionSession.objects.create(
            attender=attender_user,
            train=t12761,
            coach=coaches_map['12761']['B1'],
            journey_date=yesterday.date(),
            started_at=now.replace(hour=5, minute=0),
            completed_at=now.replace(hour=5, minute=45),
            expected_quantity=100,
            scanned_quantity=99,
            missing_quantity=1,
            status='DISCREPANCY'
        )

        # Train 12762: 100 expected, 96 returned, 4 unaccounted (MEDIUM)
        CollectionSession.objects.create(
            attender=attender_user,
            train=t12762,
            coach=coaches_map['12762']['B2'],
            journey_date=yesterday.date(),
            started_at=now.replace(hour=5, minute=30),
            completed_at=now.replace(hour=6, minute=20),
            expected_quantity=100,
            scanned_quantity=96,
            missing_quantity=4,
            status='DISCREPANCY'
        )

        # 7. Seed some items in Laundry workflow (RECEIVED_AT_LAUNDRY, WASHING, READY_FOR_REISSUE)
        laundry_sample_configs = [
            ('BS-88001', 'Bedsheet', 'RECEIVED_AT_LAUNDRY', 'Central Laundry Intake Area'),
            ('BL-88002', 'Blanket', 'WASHING', 'Industrial Washer Station #2'),
            ('TW-88003', 'Towel', 'READY_FOR_REISSUE', 'Depot Dispatch Rack A'),
            ('PC-88004', 'Pillow Cover', 'READY_FOR_REISSUE', 'Depot Dispatch Rack B'),
            ('BS-88005', 'Bedsheet', 'WASHING', 'Industrial Washer Station #1'),
        ]
        for code, ltype, st, loc in laundry_sample_configs:
            item = LinenItem.objects.create(
                linen_code=code,
                qr_code=code,
                linen_type=ltype,
                status=st,
                current_location=loc
            )
            LinenLifecycleEvent.objects.create(
                linen=item,
                event_type='RECEIVED_AT_LAUNDRY',
                timestamp=now - timedelta(hours=3),
                location='Central Laundry Intake',
                performed_by=laundry_user
            )
            if st in ['WASHING', 'READY_FOR_REISSUE']:
                LinenLifecycleEvent.objects.create(
                    linen=item,
                    event_type='WASHING',
                    timestamp=now - timedelta(hours=2),
                    location='Industrial Washer Station',
                    performed_by=laundry_user
                )
            if st == 'READY_FOR_REISSUE':
                LinenLifecycleEvent.objects.create(
                    linen=item,
                    event_type='READY_FOR_REISSUE',
                    timestamp=now - timedelta(minutes=45),
                    location='Depot Dispatch Rack',
                    performed_by=laundry_user
                )

        self.stdout.write(self.style.SUCCESS("[OK] Seed demo completed successfully!"))
        self.stdout.write(self.style.SUCCESS("[OK] 100 linen items for Coach B2 (94 returned, 6 unaccounted with distinct checkpoints)."))
        self.stdout.write(self.style.SUCCESS("[OK] Live demo item BL-20561 (Blanket at B2 / Berth 36) ready to scan."))
        self.stdout.write(self.style.SUCCESS("[OK] Demo Users: admin / attender / laundry (passwords: admin123 / attender123 / laundry123)."))
