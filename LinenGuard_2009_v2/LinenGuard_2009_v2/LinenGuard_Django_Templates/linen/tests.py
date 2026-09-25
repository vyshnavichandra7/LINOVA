from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserProfile, Train, Coach, LinenItem, LinenAssignment,
    LinenLifecycleEvent, CollectionSession, CollectionScan, PassengerPNR
)
from .services import (
    register_linen_item, assign_linen_item, validate_scan,
    mark_linen_returned, get_analytics_data
)


class LinenGuardSystemTests(TestCase):
    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user(username='admin_test', password='password123')
        self.attender = User.objects.create_user(username='attender_test', password='password123')
        UserProfile.objects.create(user=self.admin, role='ADMIN')
        UserProfile.objects.create(user=self.attender, role='ATTENDER')

        # Create test train and coaches
        self.train1 = Train.objects.create(
            train_number='12760',
            train_name='Demo Express',
            source='NDLS',
            destination='HYB'
        )
        self.coach_b1 = Coach.objects.create(train=self.train1, coach_number='B1', coach_type='3A')
        self.coach_b2 = Coach.objects.create(train=self.train1, coach_number='B2', coach_type='3A')

        self.train2 = Train.objects.create(
            train_number='12761',
            train_name='Dakshin SF',
            source='SC',
            destination='MAS'
        )
        self.coach_t2_b1 = Coach.objects.create(train=self.train2, coach_number='B1', coach_type='3A')

    # Test 1: Linen registration
    def test_01_linen_registration(self):
        item = register_linen_item('Blanket', 'BL-TEST-1', user=self.admin)
        self.assertIsNotNone(item)
        self.assertEqual(item.linen_code, 'BL-TEST-1')
        self.assertEqual(item.status, 'REGISTERED')
        self.assertEqual(item.linen_type, 'Blanket')

    # Test 2: Unique QR code
    def test_02_unique_qr(self):
        item1 = register_linen_item('Bedsheet', 'BS-TEST-1', user=self.admin)
        self.assertEqual(item1.qr_code, 'BS-TEST-1')
        # Attempt duplicate code, service should auto-resolve suffix
        item2 = register_linen_item('Bedsheet', 'BS-TEST-1', user=self.admin)
        self.assertNotEqual(item1.linen_code, item2.linen_code)
        self.assertTrue(item2.linen_code.startswith('BS-TEST-1-'))

    # Test 3: Assignment to train, coach, berth
    def test_03_assignment(self):
        item = register_linen_item('Blanket', 'BL-TEST-2', user=self.admin)
        asn = assign_linen_item(
            linen=item,
            train=self.train1,
            coach=self.coach_b2,
            berth='36',
            passenger_reference='PNR-1001',
            user=self.admin
        )
        item.refresh_from_db()
        self.assertEqual(item.status, 'ISSUED')
        self.assertEqual(asn.berth, '36')
        self.assertEqual(asn.assignment_status, 'ACTIVE')

    # Test 4: QR lookup
    def test_04_qr_lookup(self):
        item = register_linen_item('Towel', 'TW-TEST-1', user=self.admin)
        found = LinenItem.objects.filter(qr_code='TW-TEST-1').first()
        self.assertIsNotNone(found)
        self.assertEqual(found.id, item.id)

    # Test 5: Valid collection
    def test_05_valid_collection(self):
        item = register_linen_item('Blanket', 'BL-TEST-3', user=self.admin)
        assign_linen_item(item, self.train1, self.coach_b2, '36', user=self.admin)

        session = CollectionSession.objects.create(
            attender=self.attender,
            train=self.train1,
            coach=self.coach_b2,
            expected_quantity=1
        )

        validation = validate_scan(session, 'BL-TEST-3', self.attender)
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['result'], 'SUCCESS')

        # Mark returned
        res = mark_linen_returned(session, item, self.attender)
        self.assertTrue(res)
        item.refresh_from_db()
        self.assertEqual(item.status, 'RETURNED')
        self.assertEqual(session.scanned_quantity, 1)

    # Test 6: Wrong coach detection
    def test_06_wrong_coach(self):
        item = register_linen_item('Blanket', 'BL-TEST-4', user=self.admin)
        # Assigned to Coach B1
        assign_linen_item(item, self.train1, self.coach_b1, '12', user=self.admin)

        # Attender collecting in Coach B2
        session_b2 = CollectionSession.objects.create(
            attender=self.attender,
            train=self.train1,
            coach=self.coach_b2,
            expected_quantity=1
        )

        validation = validate_scan(session_b2, 'BL-TEST-4', self.attender)
        self.assertFalse(validation['valid'])
        self.assertEqual(validation['result'], 'WRONG_COACH')

    # Test 7: Unknown QR
    def test_07_unknown_qr(self):
        session = CollectionSession.objects.create(
            attender=self.attender,
            train=self.train1,
            coach=self.coach_b2,
            expected_quantity=1
        )
        validation = validate_scan(session, 'NON-EXISTENT-QR', self.attender)
        self.assertFalse(validation['valid'])
        self.assertEqual(validation['result'], 'UNKNOWN_QR')

    # Test 8: Duplicate scan rejection
    def test_08_duplicate_scan(self):
        item = register_linen_item('Blanket', 'BL-TEST-5', user=self.admin)
        assign_linen_item(item, self.train1, self.coach_b2, '15', user=self.admin)

        session = CollectionSession.objects.create(
            attender=self.attender,
            train=self.train1,
            coach=self.coach_b2,
            expected_quantity=1
        )
        mark_linen_returned(session, item, self.attender)

        # Rescan
        validation = validate_scan(session, 'BL-TEST-5', self.attender)
        self.assertFalse(validation['valid'])
        self.assertEqual(validation['result'], 'ALREADY_RETURNED')

    # Test 9: Missing quantity calculation
    def test_09_missing_calculation(self):
        session = CollectionSession.objects.create(
            attender=self.attender,
            train=self.train1,
            coach=self.coach_b2,
            expected_quantity=100,
            scanned_quantity=94
        )
        missing = session.calculate_discrepancy()
        self.assertEqual(missing, 6)
        self.assertEqual(session.missing_quantity, 6)
        self.assertEqual(session.status, 'DISCREPANCY')

    # Test 10: Lifecycle event creation
    def test_10_lifecycle_creation(self):
        item = register_linen_item('Blanket', 'BL-TEST-6', user=self.admin)
        events_count = item.lifecycle_events.count()
        self.assertGreaterEqual(events_count, 1)
        self.assertEqual(item.lifecycle_events.first().event_type, 'REGISTERED')

    # Test 11: Last verified checkpoint
    def test_11_last_verified_checkpoint(self):
        item = register_linen_item('Blanket', 'BL-TEST-7', user=self.admin)
        assign_linen_item(item, self.train1, self.coach_b2, '41', user=self.admin)
        checkpoint = item.get_last_verified_checkpoint()
        self.assertEqual(checkpoint['stage'], 'Issued to Passenger')
        self.assertIn('Coach B2', checkpoint['location'])
        self.assertIn('41', checkpoint['location'])

    # Test 12: Unaccounted status transitions
    def test_12_unaccounted_status(self):
        item = register_linen_item('Blanket', 'BL-TEST-8', user=self.admin)
        assign_linen_item(item, self.train1, self.coach_b2, '50', user=self.admin)
        item.status = 'UNACCOUNTED'
        item.save()
        LinenLifecycleEvent.objects.create(
            linen=item,
            event_type='UNACCOUNTED',
            location='Coach B2 / Berth 50',
            notes='Break in lifecycle.'
        )
        self.assertEqual(item.status, 'UNACCOUNTED')

    # Test 13: Dashboard counts
    def test_13_dashboard_counts(self):
        analytics = get_analytics_data()
        self.assertIn('total', analytics)
        self.assertIn('issued', analytics)
        self.assertIn('returned', analytics)
        self.assertIn('unaccounted', analytics)
        self.assertIn('trains_data', analytics)
        self.assertIn('coach_hotspots', analytics)

    # Test 14: PNR-driven Linen Assignment View
    def test_14_assign_linen_via_pnr(self):
        PassengerPNR.objects.create(
            pnr_number='PNR-1001',
            train=self.train1,
            coach=self.coach_b2,
            berth='36',
            berth_type='Lower Berth',
            source_station='New Delhi (NDLS)',
            destination_station='Hyderabad (HYB)'
        )
        self.client.login(username='attender_test', password='password123')
        item = register_linen_item('Blanket', 'BL-PNR-TEST', user=self.admin)
        response = self.client.post('/api/attendant/issue/', {
            'pnr_number': 'PNR-1001',
            'linen_codes': ['BL-PNR-TEST']
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.status, 'ISSUED')
        assignment = LinenAssignment.objects.filter(linen=item, passenger_reference='PNR-1001').first()
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.train.train_number, '12760')
        self.assertEqual(assignment.coach.coach_number, 'B2')
        self.assertEqual(assignment.berth, '36')
        self.assertEqual(assignment.source_station, 'New Delhi (NDLS)')
        self.assertEqual(assignment.destination_station, 'Hyderabad (HYB)')

    # Test 15: Laundry Generate and Attendant Direct Issue
    def test_15_laundry_generate_and_attendant_issue(self):
        laundry_user = User.objects.create_user(username='laundry_test', password='password123')
        UserProfile.objects.create(user=laundry_user, role='LAUNDRY')
        self.client.login(username='laundry_test', password='password123')

        # Generate complete kit from laundry
        gen_res = self.client.post('/api/laundry/generate/', {
            'linen_type': 'KIT',
            'count': 1
        }, content_type='application/json')
        self.assertEqual(gen_res.status_code, 200)
        data = gen_res.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['items']), 4)
        codes = [it['linen_code'] for it in data['items']]

        # Switch to attendant and check stock
        self.client.login(username='attender_test', password='password123')
        stock_res = self.client.get('/api/laundry/available-stock/')
        self.assertEqual(stock_res.status_code, 200)
        stock_data = stock_res.json()
        self.assertTrue(stock_data['success'])
        self.assertGreaterEqual(stock_data['total_count'], 4)

        # Issue to passenger
        pnr_p = PassengerPNR.objects.create(
            pnr_number='PNR-2002',
            train=self.train1,
            coach=self.coach_b1,
            berth='14',
            source_station='NDLS',
            destination_station='HYB'
        )
        issue_res = self.client.post('/api/attendant/issue/', {
            'pnr_number': 'PNR-2002',
            'linen_codes': codes
        }, content_type='application/json')
        self.assertEqual(issue_res.status_code, 200)
        pnr_p.refresh_from_db()
        self.assertEqual(pnr_p.boarding_status, 'Issued')
        for code in codes:
            it = LinenItem.objects.get(linen_code=code)
            self.assertEqual(it.status, 'ISSUED')

