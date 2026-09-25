import os
import sys
import django

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linenguard_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from linen.models import Coach, Train, PassengerPNR, CoachHandOff, UserProfile, LinenItem

def run_tests():
    print("=" * 60)
    print("STARTING LINOVA SYSTEM VERIFICATION")
    print("=" * 60)

    # 1. Verify Logo Files
    logo_jpg = os.path.exists('static/img/logo.jpeg')
    logo_png = os.path.exists('static/img/logo.png')
    print(f"[TEST 1] Logo JPG exists: {logo_jpg}, Logo PNG exists: {logo_png}")
    assert logo_jpg, "logo.jpeg missing"
    assert logo_png, "logo.png missing"

    # 2. Verify Theme Script
    theme_js = os.path.exists('static/js/theme.js')
    print(f"[TEST 2] theme.js exists: {theme_js}")
    assert theme_js, "theme.js missing"

    # 3. Verify Theme Toggle in Templates
    for t_path in ['templates/base.html', 'templates/base_attendant.html', 'templates/supervisor/base_supervisor.html']:
        with open(t_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_toggle = 'theme-toggle-btn' in content
            has_theme_js = 'theme.js' in content
            has_logo = 'logo.jpeg' in content or 'logo.png' in content
            print(f"[TEST 3] {t_path}: Toggle={has_toggle}, Script={has_theme_js}, Logo={has_logo}")
            assert has_toggle and has_theme_js and has_logo, f"Verification failed for {t_path}"

    # 4. Verify Authentication by Employee ID
    client = Client()
    login_resp = client.post('/login/', {
        'role_choice': 'attendant',
        'employee_id': 'ATT-B1-4019',
        'password': 'attender123'
    }, follow=True)
    print(f"[TEST 4] Attendant Login via Employee ID (ATT-B1-4019): status={login_resp.status_code}")
    assert login_resp.status_code == 200

    # 5. Verify Supervisor Assignment API by Employee ID
    admin_user = User.objects.get(username='admin')
    client.force_login(admin_user)

    assign_resp = client.post('/api/supervisor/assign-coach/', {
        'employee_id': 'ATT-B1-4019',
        'coach_number': 'B1',
        'shift': 'Evening',
        'bedsheets_handed_over': 120
    }, content_type='application/json')
    print(f"[TEST 5] Supervisor Assign Coach B1 to ATT-B1-4019: status={assign_resp.status_code}, data={assign_resp.json()}")
    assert assign_resp.status_code == 200
    assert assign_resp.json()['success'] is True
    assert assign_resp.json()['coach'] == 'B1'

    # 6. Verify Attendant Profile Reflects Coach B1 and Passenger Roster
    att_user = User.objects.get(profile__badge_number='ATT-B1-4019')
    client.force_login(att_user)

    hub_resp = client.get('/attendant/hub/')
    print(f"[TEST 6] Attendant Profile Hub status={hub_resp.status_code}")
    assert hub_resp.status_code == 200
    hub_content = hub_resp.content.decode('utf-8')
    assert 'Coach B1' in hub_content, "Assigned coach B1 not in attendant hub"
    assert 'Evening Shift' in hub_content, "Assigned Evening Shift not in attendant hub"
    assert 'ATT-B1-4019' in hub_content, "Employee ID not shown in profile"
    assert 'Vikram Rao' in hub_content, "Coach B1 passenger Vikram Rao missing from roster"
    assert 'Ananya Sen' in hub_content, "Coach B1 passenger Ananya Sen missing from roster"
    print("✓ Coach B1 passengers successfully displayed on attendant's profile!")

    # 7. Reassign to Coach B3 and Verify Immediate Reflection
    client.force_login(admin_user)
    reassign_resp = client.post('/api/supervisor/assign-coach/', {
        'employee_id': 'ATT-B1-4019',
        'coach_number': 'B3',
        'shift': 'Night',
        'bedsheets_handed_over': 150
    }, content_type='application/json')
    print(f"[TEST 7] Supervisor Reassigned ATT-B1-4019 to Coach B3: status={reassign_resp.status_code}, data={reassign_resp.json()}")
    assert reassign_resp.status_code == 200
    assert reassign_resp.json()['coach'] == 'B3'

    # 8. Check Attendant Profile for Coach B3
    client.force_login(att_user)
    hub_resp_b3 = client.get('/attendant/hub/')
    hub_content_b3 = hub_resp_b3.content.decode('utf-8')
    assert 'Coach B3' in hub_content_b3, "Assigned coach B3 not in attendant hub"
    assert 'Night Shift' in hub_content_b3, "Assigned Night Shift not in attendant hub"
    assert 'Harish Gupta' in hub_content_b3, "Coach B3 passenger Harish Gupta missing from roster"
    assert 'Meena Kumari' in hub_content_b3, "Coach B3 passenger Meena Kumari missing from roster"
    print("✓ Coach B3 passengers successfully displayed on attendant's profile after reassignment!")

    # 9. Verify Linen Issuance Operation for one passenger with registered depot linen
    pnr_b3 = 'PNR-6611'
    ready_linen = LinenItem.objects.filter(status='READY_FOR_REISSUE').first()
    if not ready_linen:
        ready_linen = LinenItem.objects.create(
            linen_code='BS-2026-04825',
            qr_code='BS-2026-04825',
            linen_type='Bedsheet',
            status='READY_FOR_REISSUE',
            current_location='Depot Stock'
        )
    else:
        ready_linen.status = 'READY_FOR_REISSUE'
        ready_linen.save()

    issue_resp = client.post('/api/attendant/issue/', {
        'pnr_number': pnr_b3,
        'linen_code': ready_linen.linen_code
    }, content_type='application/json')
    print(f"[TEST 9] Linen Issuance to Passenger {pnr_b3}: status={issue_resp.status_code}, data={issue_resp.json()}")
    assert issue_resp.status_code == 200
    assert issue_resp.json()['success'] is True

    print("=" * 60)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
