#!/usr/bin/env python
"""
Simple script to create users for SkillForge
Usage: python create_user.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from Core.models import CustomUser

def create_user():
    """Interactive user creation"""
    
    print("🎯 SkillForge User Creation Tool")
    print("=" * 40)
    
    # Get user input
    username = input("Enter username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return
    
    # Check if user exists
    if CustomUser.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists!")
        return
    
    email = input("Enter email: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        return
    
    password = input("Enter password: ").strip()
    if len(password) < 6:
        print("❌ Password must be at least 6 characters!")
        return
    
    first_name = input("Enter first name (optional): ").strip()
    last_name = input("Enter last name (optional): ").strip()
    
    # Optional: Set initial XP and SP
    try:
        xp = int(input("Enter initial XP (default 0): ") or "0")
        sp = int(input("Enter initial SP (default 100): ") or "100")
    except ValueError:
        xp, sp = 0, 100
    
    try:
        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            xp=xp,
            sp=sp
        )
        
        print("\n✅ User created successfully!")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"XP: {user.xp}")
        print(f"SP: {user.sp}")
        print(f"Level: {user.level}")
        print(f"Purchased themes: {user.purchased_themes}")
        
        print(f"\n🚀 User can now login to SkillForge!")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")

if __name__ == '__main__':
    create_user()