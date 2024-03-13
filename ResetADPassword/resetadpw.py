import secrets
import subprocess
import sys
import pkg_resources
import time


packages = {pkg.key for pkg in pkg_resources.working_set}
if 'pyad' not in packages:
    print('### pyad is not installed ###')
    print('### Installing pyad ###')
    time.sleep(1)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyad"])
if 'pypiwin32' not in packages:
    print('### pypiwin32 is not installed ###')
    print('### Installing pypiwin32')
    time.sleep(1)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypiwin32"])
    
from pyad import aduser, pyad_setdefaults, pyadexceptions



pyad_setdefaults(username='admin.account', password='admin.password', ldap_server="dc.domain.com")
lookup = input('Enter username (no domain prefix or suffix): ')
try:
    user = aduser.ADUser.from_cn(lookup, search_base="DC=domain, DC=com")
except pyadexceptions.invalidResults:
    print(f'Could not find {lookup}.')
    print('Exiting script')
    exit(0)
    

print(f'{"DN:":<20} {user.dn}')
print(f'{"Type:":<20} {user.type}')
print(f'{"Password last set:":<20} {user.get_password_last_set()}')
try:
    print(f'{"Password expires:":<20} {user.get_password_expired()}')
except AttributeError:
    print(f'{"Password expires:":<20} N/A')


password = secrets.token_urlsafe(12)
print(f'{"New password:":<20} {password}')
reset = input('Reset password [Y|n]: ')


if reset == '' or reset.lower().startswith('y'):
    try:
        user.set_password(password)
    except pyadexceptions.win32Exception as error:
        print(f'Error: password unchanged')
        print(error.error_info.get('message'))
        exit(0)
else:
    print('Did not receive confirmation.')
    print('Password not changed. Exiting script.')
    exit(0)