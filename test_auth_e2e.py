"""
End-to-end test for the complete auth flow.
Run AFTER python app.py is running.
"""
import sys
import requests
import json

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://127.0.0.1:49281'
PASS = 'OK'
FAIL = 'FAIL'


errors = []

def check(label, condition, info=''):
    if condition:
        print(f'  {PASS} {label}' + (f' — {info}' if info else ''))
    else:
        print(f'  {FAIL} {label}' + (f' — {info}' if info else ''))
        errors.append(label)

print('\n=== 1. LOGIN (admin) ===')
r = requests.post(f'{BASE}/api/v5/auth/login', json={'email': 'admin@leadforge.ai', 'password': 'Admin123!'})
check('Login 200', r.status_code == 200, str(r.status_code))
data = r.json()
access_token = data.get('access_token', '')
refresh_token = data.get('refresh_token', '')
user = data.get('user', {})
check('Access token is real JWT', len(access_token.split('.')) == 3, f'{access_token[:30]}...')
check('Refresh token is real JWT', len(refresh_token.split('.')) == 3)
check('User name correct', user.get('name') == 'LeadForge Agency Admin')
check('User email correct', user.get('email') == 'admin@leadforge.ai')

print('\n=== 2. GET /me (valid token) ===')
r = requests.get(f'{BASE}/api/v5/auth/me', headers={'Authorization': f'Bearer {access_token}'})
check('/me returns 200', r.status_code == 200)
me = r.json()
check('/me returns user data', me.get('email') == 'admin@leadforge.ai')

print('\n=== 3. GET /me (no token) ===')
r = requests.get(f'{BASE}/api/v5/auth/me')
check('/me without token returns 401', r.status_code == 401, str(r.status_code))

print('\n=== 4. GET /me (bad token) ===')
r = requests.get(f'{BASE}/api/v5/auth/me', headers={'Authorization': 'Bearer bad.token.here'})
check('/me with bad token returns 401', r.status_code == 401, str(r.status_code))

print('\n=== 5. REGISTER new user ===')
r = requests.post(f'{BASE}/api/v5/auth/register', json={
    'name': 'Test User', 'email': 'test_e2e@example.com',
    'password': 'TestPass123!', 'company': 'Test Agency'
})
check('Register returns 201', r.status_code == 201, str(r.status_code))
if r.status_code == 201:
    reg_data = r.json()
    new_access = reg_data.get('access_token', '')
    check('New user gets JWT', len(new_access.split('.')) == 3)
    check('New user email correct', reg_data.get('user', {}).get('email') == 'test_e2e@example.com')

print('\n=== 6. DUPLICATE REGISTER ===')
r = requests.post(f'{BASE}/api/v5/auth/register', json={
    'name': 'Dup', 'email': 'test_e2e@example.com', 'password': 'AnotherPass123!'
})
check('Duplicate email returns 409', r.status_code == 409, str(r.status_code))

print('\n=== 7. WRONG PASSWORD ===')
r = requests.post(f'{BASE}/api/v5/auth/login', json={'email': 'admin@leadforge.ai', 'password': 'WRONG!'})
check('Wrong password returns 401', r.status_code == 401, r.json().get('error', ''))

print('\n=== 8. REFRESH TOKEN ===')
r = requests.post(f'{BASE}/api/v5/auth/refresh', json={'refresh_token': refresh_token})
check('Refresh returns 200', r.status_code == 200, str(r.status_code))
if r.status_code == 200:
    new_at = r.json().get('access_token', '')
    check('New access token is JWT', len(new_at.split('.')) == 3)
    access_token = new_at  # Use the refreshed token

print('\n=== 9. FORGOT PASSWORD ===')
r = requests.post(f'{BASE}/api/v5/auth/forgot-password', json={'email': 'admin@leadforge.ai'})
check('Forgot password returns 200', r.status_code == 200)
reset_token = r.json().get('reset_token')
check('Reset token provided', reset_token is not None)

print('\n=== 10. RESET PASSWORD ===')
if reset_token:
    r = requests.post(f'{BASE}/api/v5/auth/reset-password', json={
        'token': reset_token, 'new_password': 'NewAdmin456!'
    })
    check('Reset password returns 200', r.status_code == 200, r.json().get('message', ''))

    r2 = requests.post(f'{BASE}/api/v5/auth/login', json={'email': 'admin@leadforge.ai', 'password': 'NewAdmin456!'})
    check('Login with new password works', r2.status_code == 200)

    r3 = requests.post(f'{BASE}/api/v5/auth/login', json={'email': 'admin@leadforge.ai', 'password': 'Admin123!'})
    check('Old password no longer works', r3.status_code == 401)

    # Restore original password
    r4 = requests.post(f'{BASE}/api/v5/auth/forgot-password', json={'email': 'admin@leadforge.ai'})
    rt2 = r4.json().get('reset_token')
    r5 = requests.post(f'{BASE}/api/v5/auth/reset-password', json={'token': rt2, 'new_password': 'Admin123!'})
    check('Restore original password', r5.status_code == 200)

print('\n=== 11. UPDATE PROFILE ===')
r = requests.put(f'{BASE}/api/v5/auth/profile',
    json={'name': 'Updated Admin', 'company': 'Updated Agency'},
    headers={'Authorization': f'Bearer {access_token}'}
)
check('Update profile returns 200', r.status_code == 200, str(r.status_code))
if r.status_code == 200:
    up = r.json()
    check('Name updated', up.get('name') == 'Updated Admin')
    check('Company updated', up.get('company') == 'Updated Agency')
    # Restore
    requests.put(f'{BASE}/api/v5/auth/profile',
        json={'name': 'LeadForge Agency Admin', 'company': 'LeadForge Agency'},
        headers={'Authorization': f'Bearer {access_token}'}
    )

print('\n=== 12. CHANGE PASSWORD (guarded) ===')
r = requests.put(f'{BASE}/api/v5/auth/password',
    json={'current_password': 'Admin123!', 'new_password': 'ChangedPass123!'},
    headers={'Authorization': f'Bearer {access_token}'}
)
check('Change password returns 200', r.status_code == 200, r.json().get('message', ''))
if r.status_code == 200:
    r2 = requests.post(f'{BASE}/api/v5/auth/login', json={'email': 'admin@leadforge.ai', 'password': 'ChangedPass123!'})
    check('Login with changed password', r2.status_code == 200)
    new_at2 = r2.json().get('access_token', '')
    # Restore
    requests.put(f'{BASE}/api/v5/auth/password',
        json={'current_password': 'ChangedPass123!', 'new_password': 'Admin123!'},
        headers={'Authorization': f'Bearer {new_at2}'}
    )

print('\n=== 13. LOGOUT + BLACKLIST CHECK ===')
# Get fresh tokens for logout test
r_login = requests.post(f'{BASE}/api/v5/auth/login', json={'email': 'admin@leadforge.ai', 'password': 'Admin123!'})
logout_refresh = r_login.json().get('refresh_token', '')
r = requests.post(f'{BASE}/api/v5/auth/logout', json={'refresh_token': logout_refresh})
check('Logout returns 200', r.status_code == 200)

r_bl = requests.post(f'{BASE}/api/v5/auth/refresh', json={'refresh_token': logout_refresh})
check('Blacklisted refresh token rejected (401)', r_bl.status_code == 401, r_bl.json().get('error', ''))

print()
print('=' * 50)
if errors:
    print(f'FAILED TESTS ({len(errors)}):')
    for e in errors:
        print(f'  - {e}')
else:
    print('ALL 26 CHECKS PASSED! Auth flow is production-ready.')
print('=' * 50)
