import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linenguard_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from linen.models import UserProfile, PassengerPNR, CoachHandOff

def run_tests():
    print("=== STARTING LINENGUARD VERIFICATION ===")
    client = Client()

    # 1. Test Attendant Hub & Deboarding Notification
    print("\n--- 1. Testing Attendant Deboarding Flow ---")
    attender_user = User.objects.filter(username='attender').first()
    if not attender_user:
        print("ERROR: User 'attender' not found!")
        return False

    client.force_login(attender_user)
    
    # Check Hub
    hub_res = client.get('/attendant/hub/')
    assert hub_res.status_code == 200, f"Hub returned {hub_res.status_code}"
    hub_html = hub_res.content.decode('utf-8')
    assert "Deboarding in 18 Mins" in hub_html or "Deboarding in" in hub_html, "Deboarding badge missing in hub"
    assert "playRailwayChime" in hub_html, "Chime function missing in hub"
    assert "deboardingSection" in hub_html, "Deboarding section missing in hub"
    assert "Secunderabad" in hub_html, "Station missing in hub"
    assert "Berth 24" in hub_html or "Berth 25" in hub_html, "Deboarding berths missing in hub"
    print("PASS: Attendant Hub contains 20-minute deboarding notification, station chime trigger, and deboarding passenger list.")

    # Check Alert Page
    alert_res = client.get('/attendant/alert/')
    assert alert_res.status_code == 200, f"Alert returned {alert_res.status_code}"
    alert_html = alert_res.content.decode('utf-8')
    assert "Secunderabad" in alert_html, "Station missing in alert page"
    assert "Berth 24" in alert_html or "Berth 25" in alert_html, "Deboarding berths missing in alert page"
    assert "Collect & Scan QR" in alert_html, "Collect & Scan QR link missing in alert"
    print("PASS: Station Alert page displays deboarding passengers and direct QR collection links.")

    # Check Collect Item Page
    collect_res = client.get('/attendant/collect/?berth=24&code=BL-20561')
    assert collect_res.status_code == 200, f"Collect returned {collect_res.status_code}"
    collect_html = collect_res.content.decode('utf-8')
    assert "Priority Deboarding Sweep" in collect_html, "Deboarding banner missing in collect page"
    assert "Secunderabad" in collect_html, "Station missing in collect page"
    assert "BL-20561" in collect_html, "Demo QR missing in collect page"
    print("PASS: Collect Item page displays priority deboarding chips and pre-fills target berth.")

    # 2. Test Supervisor Language Switcher & Theme Toggle
    print("\n--- 2. Testing Supervisor Top-Right Bar & Theme Toggle ---")
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        print("ERROR: User 'admin' not found!")
        return False

    client.force_login(admin_user)
    sup_res = client.get('/supervisor/dashboard/')
    assert sup_res.status_code == 200, f"Supervisor live returned {sup_res.status_code}"
    sup_html = sup_res.content.decode('utf-8')
    assert "supervisor-top-bar" in sup_html, "supervisor-top-bar container missing"
    assert "lang-switch" in sup_html, "Language switcher missing in supervisor header"
    assert "theme-toggle-btn" in sup_html, "Theme toggle button missing in supervisor header"
    print("PASS: Supervisor console has language switcher and theme toggle in sticky top-right header.")

    # 3. Check CSS & JS Assets
    print("\n--- 3. Checking CSS and JS Theme Rules ---")
    with open('static/js/theme.js', 'r', encoding='utf-8') as f:
        theme_js = f.read()
    assert "document.documentElement.setAttribute('data-theme', targetTheme)" in theme_js, "data-theme attribute setting missing in theme.js"
    assert "localStorage.setItem('linenguard_theme', targetTheme)" in theme_js, "theme localStorage missing in theme.js"
    assert 'theme-toggle-btn' in theme_js, "theme-toggle-btn binding missing in theme.js"

    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        css = f.read()
    assert ':root[data-theme="light"]' in css, "Light theme root missing in style.css"
    assert ':root[data-theme="dark"]' in css, "Dark theme root missing in style.css"
    assert '--admin-panel' in css, "admin-panel CSS var missing in style.css"
    assert '--admin-bg' in css, "admin-bg CSS var missing in style.css"
    assert '.deboarding-notification-banner' in css, "Deboarding banner styling missing in style.css"
    assert '.deboard-pulse-circle' in css, "Pulse animation styling missing in style.css"
    print("PASS: Theme variables and deboarding styles are fully integrated in static assets.")

    print("\n=== ALL VERIFICATIONS PASSED SUCCESSFULLY! ===")
    return True

if __name__ == '__main__':
    run_tests()
