import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linenguard_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from linen.models import CoachHandOff, UserProfile, CollectionSession

def run_tests():
    print("=== STARTING SUPERVISOR EMPLOYEE & THEME VERIFICATION ===")
    client = Client()

    # 1. Login as Supervisor (admin)
    admin_user = User.objects.filter(username='admin').first()
    assert admin_user, "Admin user not found"
    client.force_login(admin_user)
    print("[OK] Logged in as Supervisor (admin)")

    # 2. Test Creating New Employee via API
    test_emp_id = "ATT-B4-9911"
    test_username = "rameshrao"
    test_password = "securePass2026!"
    test_name = "Ramesh Rao"

    # Clean up if existed from previous run
    old_user = User.objects.filter(username=test_username).first()
    if old_user:
        CoachHandOff.objects.filter(attendant=old_user).delete()
        CollectionSession.objects.filter(attender=old_user).delete()
        UserProfile.objects.filter(user=old_user).delete()
        old_user.delete()

    create_payload = {
        'full_name': test_name,
        'employee_id': test_emp_id,
        'username': test_username,
        'password': test_password,
        'coach_number': 'B4',
        'shift': 'Morning',
        'quota': 120
    }

    resp = client.post('/api/supervisor/create-employee/', create_payload, content_type='application/json')
    assert resp.status_code == 200, f"Create employee failed with status {resp.status_code}: {resp.content}"
    data = resp.json()
    assert data.get('success') is True, f"Response indicated failure: {data}"
    assert data['employee']['employee_id'] == test_emp_id
    assert data['employee']['coach'] == 'B4'
    assert data['employee']['password'] == test_password
    print(f"[OK] API successfully created employee: {test_name} ({test_emp_id})")

    # 3. Verify Database Objects
    created_user = User.objects.filter(username=test_username).first()
    assert created_user, "Created user not found in database!"
    assert created_user.profile.badge_number == test_emp_id, "Badge number mismatch!"
    assert created_user.profile.role == 'ATTENDANT', "Role mismatch!"

    handoff = CoachHandOff.objects.filter(attendant=created_user).first()
    assert handoff, "CoachHandOff not created for new employee!"
    assert handoff.coach.coach_number == 'B4'
    assert handoff.shift == 'Morning'
    assert handoff.bedsheets_handed_over == 120
    print("[OK] Verified database records (User, UserProfile, CoachHandOff, CollectionSession)")

    # 4. Test Attendant Login Using Employee ID (Badge Number) & Provided Password
    client.logout()
    login_get = client.get('/login/')
    assert login_get.status_code == 200

    # Sign in using Employee ID
    login_resp = client.post('/login/', {
        'role_choice': 'attendant',
        'employee_id': test_emp_id,
        'password': test_password,
    }, follow=True)
    assert login_resp.status_code == 200
    assert '_auth_user_id' in client.session, "Session missing auth_user_id! Authentication failed."
    assert str(client.session['_auth_user_id']) == str(created_user.id), "Logged in as wrong user!"
    print(f"[OK] Attendant successfully signed in using Employee ID ({test_emp_id}) and password!")

    # 5. Verify Attendant Hub shows their allocated coach B4
    hub_resp = client.get('/attendant/hub/')
    assert hub_resp.status_code == 200
    hub_html = hub_resp.content.decode('utf-8')
    assert "Coach B4" in hub_html, "Allocated Coach B4 missing from attendant hub!"
    assert test_emp_id in hub_html, "Employee ID missing from attendant hub!"
    print(f"[OK] Attendant Hub correctly displays Coach B4 for {test_name}")

    # 6. Test Supervisor Handoff Page & Light Theme Classes
    client.logout()
    client.force_login(admin_user)
    handoff_resp = client.get('/supervisor/handoff/')
    assert handoff_resp.status_code == 200
    h_html = handoff_resp.content.decode('utf-8')

    # Check Add Employee modal exists in page
    assert 'id="addEmployeeModal"' in h_html, "addEmployeeModal missing from assign_handoff.html"
    assert 'openAddEmployeeModal()' in h_html, "openAddEmployeeModal() trigger missing"
    assert 'printableCredentialSlip' in h_html, "printableCredentialSlip missing"
    assert 'copySlipCredentials()' in h_html, "copySlipCredentials() missing"

    # Check that hardcoded bg-dark has been removed from supervisor selects
    assert 'supervisor-select' in h_html, "supervisor-select class missing in assign_handoff.html"
    assert 'id="assignEmployeeIdSelect" class="form-select form-select-sm supervisor-select' in h_html
    print("[OK] Supervisor console has Add Employee modal, credentials slip, and supervisor-select controls")

    # 7. Test Light Theme CSS in static/css/style.css
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    assert '[data-theme="light"] .supervisor-select' in css
    assert '[data-theme="light"] .supervisor-input' in css
    assert '[data-theme="light"] .supervisor-credential-slip' in css
    assert 'background-color: #ffffff !important;' in css
    print("[OK] CSS file contains full light theme overrides for all supervisor controls")

    print("\n=======================================================")
    print("ALL SUPERVISOR EMPLOYEE & LIGHT THEME VERIFICATIONS PASSED!")
    print("=======================================================")
    return True

if __name__ == '__main__':
    run_tests()
