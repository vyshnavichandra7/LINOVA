import os, subprocess

script = """
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*manage.py runserver*' } | Select-Object ProcessId, ParentProcessId, CommandLine | Format-List
"""
output = subprocess.check_output(["powershell", "-NoProfile", "-Command", script], text=True)
print(output)

