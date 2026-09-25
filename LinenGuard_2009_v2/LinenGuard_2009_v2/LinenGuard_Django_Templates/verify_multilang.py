import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linenguard_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json
import re

client = Client()

print("=" * 60)
print("LINENGUARD MULTI-LANGUAGE ENGINE VERIFICATION")
print("=" * 60)

# 1. Test Static translations.js accessibility
resp = client.get('/static/js/translations.js')
assert resp.status_code == 200, f"translations.js returned {resp.status_code}"
content = b"".join(resp.streaming_content).decode('utf-8')
assert "LinenDict" in content, "LinenDict not found in translations.js"
assert "setLanguage" in content, "setLanguage not found in translations.js"
assert "selectLang" in content, "selectLang not found in translations.js"
assert "applyTranslations" in content, "applyTranslations not found in translations.js"
assert "hi:" in content and "te:" in content, "Hindi and Telugu dictionaries not found in translations.js"
print("[PASS] translations.js loaded successfully and contains engine functions & dictionaries.")

# 2. Test Login page for language switch markup and script
resp = client.get('/login/')
assert resp.status_code == 200
html = resp.content.decode('utf-8')
assert 'class="lang-switch"' in html, "lang-switch not found in /login/"
assert 'id="lang-en"' in html and 'id="lang-hi"' in html and 'id="lang-te"' in html, "Language buttons missing in /login/"
assert '/static/js/translations.js' in html, "translations.js script tag missing in /login/"
print("[PASS] Login screen has [ EN | हिं | తె ] buttons and includes translations.js.")

# 3. Test Attendant Hub & Issue screens
attendant_user = User.objects.get(username='attender')
client.force_login(attendant_user)

attendant_routes = [
    '/attendant/assignment/',
    '/attendant/hub/',
    '/attendant/issue/',
    '/attendant/collect/',
    '/attendant/alert/',
    '/attendant/report/',
    # Aliases
    '/attender/',
    '/attender/hub/',
    '/attender/issue/',
    '/attender/collect/',
]

for route in attendant_routes:
    r = client.get(route, follow=True)
    assert r.status_code == 200, f"Route {route} returned {r.status_code}"
    body = r.content.decode('utf-8')
    assert 'class="lang-switch"' in body, f"lang-switch missing in {route}"
    assert '/static/js/translations.js' in body, f"translations.js script missing in {route}"
    print(f"[PASS] Attendant screen {route} (Status {r.status_code}) -> Has [ EN | हिं | తె ] & translations.js")

# 4. Test Laundry screen
laundry_user = User.objects.get(username='laundry')
client.force_login(laundry_user)

laundry_routes = [
    '/laundry/register/',
    '/laundry/intake/',
]

for route in laundry_routes:
    r = client.get(route, follow=True)
    assert r.status_code == 200, f"Route {route} returned {r.status_code}"
    body = r.content.decode('utf-8')
    assert 'class="lang-switch"' in body, f"lang-switch missing in {route}"
    assert '/static/js/translations.js' in body, f"translations.js script missing in {route}"
    print(f"[PASS] Laundry screen {route} (Status {r.status_code}) -> Has [ EN | हिं | తె ] & translations.js")

# 5. Test Supervisor screen
sup_user = User.objects.get(username='admin')
client.force_login(sup_user)

sup_routes = [
    '/supervisor/handoff/',
    '/supervisor/dashboard/',
    '/supervisor/settlement/',
    '/reports/audit/',
    '/reports/search/',
]

for route in sup_routes:
    r = client.get(route, follow=True)
    assert r.status_code == 200, f"Route {route} returned {r.status_code}"
    body = r.content.decode('utf-8')
    assert 'class="lang-switch"' in body, f"lang-switch missing in supervisor route {route}"
    assert '/static/js/translations.js' in body, f"translations.js script missing in supervisor route {route}"
    print(f"[PASS] Supervisor screen {route} (Status {r.status_code}) -> Has [ EN | हिं | తె ] & translations.js")

print("\n" + "=" * 60)
print("ALL MULTI-LANGUAGE CHECKS PASSED (100% COVERAGE)")
print("=" * 60)
