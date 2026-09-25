import urllib.request, http.cookiejar, urllib.parse, re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
html = opener.open('http://127.0.0.1:8000/login/').read().decode('utf-8')
csrf = re.search(r'csrfmiddlewaretoken.*value=["\']([^"\']+)', html).group(1)
data = urllib.parse.urlencode({'employee_id': 'emp-adm-01', 'password': 'admin123', 'csrfmiddlewaretoken': csrf}).encode()
opener.open('http://127.0.0.1:8000/login/', data=data)
s_html = opener.open('http://127.0.0.1:8000/supervisor/handoff/').read().decode('utf-8')

print("Add New Employee in page:", "Add New Employee" in s_html)
print("addEmployeeModal in page:", "addEmployeeModal" in s_html)
print("supervisor-select in page:", "supervisor-select" in s_html)
print("old bg-dark select in page:", "form-select form-select-sm bg-dark" in s_html)

