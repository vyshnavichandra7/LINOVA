import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linenguard_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from linen.models import CoachHandOff

def run_tests():
    print("=== STARTING PASSENGER ROSTER VERIFICATION ===")
    client = Client()

    test_attendants = [
        ('attender', 'B2', ['Amit Patel', 'R. Sharma', 'A. Verma', 'Rajesh Kumar', 'K. Venkat', 'Sneha Sharma']),
        ('attender2', 'B1', ['Vikram Rao', 'Ananya Sen', 'Mohan Lal', 'Divya Nair', 'Karthik S']),
        ('attender3', 'B3', ['Harish Gupta', 'Meena Kumari', 'Deepak Joshi', 'Sunita Rani']),
        ('attender4', 'A1', ['Dr. Arvind Swamy', 'Preeti Menon', 'Col. R. Rathore']),
    ]

    for username, expected_coach, expected_passengers in test_attendants:
        print(f"\n--- Testing Attendant: {username} (Assigned Coach: {expected_coach}) ---")
        user = User.objects.filter(username=username).first()
        assert user, f"User {username} not found!"
        client.force_login(user)

        # 1. Test Attendant Hub (choose_action.html)
        hub_res = client.get('/attendant/hub/')
        assert hub_res.status_code == 200, f"Hub returned {hub_res.status_code}"
        hub_html = hub_res.content.decode('utf-8')
        assert f"Coach {expected_coach}" in hub_html, f"Coach {expected_coach} missing from hub for {username}"
        assert "Passenger Reservation Roster" in hub_html, "Passenger Reservation Roster missing from hub"
        
        for p_name in expected_passengers:
            assert p_name in hub_html, f"Passenger {p_name} missing from Hub roster for Coach {expected_coach}!"
        print(f"PASS: Hub displays all {len(expected_passengers)} passengers for Coach {expected_coach}.")

        # 2. Test Dedicated Roster Page (/attendant/roster/)
        roster_res = client.get('/attendant/roster/')
        assert roster_res.status_code == 200, f"Roster returned {roster_res.status_code}"
        roster_html = roster_res.content.decode('utf-8')
        assert f"Coach {expected_coach} Passenger Reservation Roster" in roster_html, "Roster header missing"
        assert "rosterSearchInput" in roster_html, "Search input missing in roster page"
        assert "filterBtnBoarding" in roster_html, "Filter buttons missing in roster page"
        
        for p_name in expected_passengers:
            assert p_name in roster_html, f"Passenger {p_name} missing from dedicated Roster page for Coach {expected_coach}!"
        print(f"PASS: Dedicated Roster page displays all {len(expected_passengers)} passengers with search and filter controls.")

        # 3. Test Coach Assignment Page (/attendant/assignment/)
        assign_res = client.get('/attendant/assignment/')
        assert assign_res.status_code == 200, f"Assignment returned {assign_res.status_code}"
        assign_html = assign_res.content.decode('utf-8')
        assert f"Coach {expected_coach} Passenger Roster" in assign_html, "Coach Passenger Roster missing from assignment page"
        for p_name in expected_passengers:
            assert p_name in assign_html, f"Passenger {p_name} missing from Assignment page roster for Coach {expected_coach}!"
        print(f"PASS: Coach Assignment screen displays passenger roster for Coach {expected_coach}.")

    print("\n=== ALL ATTENDANT PASSENGER ROSTER TESTS PASSED 100%! ===")
    return True

if __name__ == '__main__':
    run_tests()
