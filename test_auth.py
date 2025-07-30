#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from django.contrib.auth import authenticate
from Core.models import CustomUser

# Get admin user
try:
    user = CustomUser.objects.get(username='admin')
    print(f'User: {user.username}')
    print(f'Email: {user.email}')
    print(f'Is active: {user.is_active}')
    print(f'Has usable password: {user.has_usable_password()}')
    
    # Test common passwords
    test_passwords = ['admin', 'admin123', 'password', '123456', 'admin@123']
    print('\nTesting passwords:')
    for pwd in test_passwords:
        auth_user = authenticate(username='admin', password=pwd)
        print(f'Password "{pwd}": {"✅ SUCCESS" if auth_user else "❌ FAILED"}')
        
    # Set a known password for testing
    print('\nSetting password to "admin123" for testing...')
    user.set_password('admin123')
    user.save()
    
    # Test the new password
    auth_user = authenticate(username='admin', password='admin123')
    print(f'New password test: {"✅ SUCCESS" if auth_user else "❌ FAILED"}')
    
except CustomUser.DoesNotExist:
    print('Admin user not found!')
