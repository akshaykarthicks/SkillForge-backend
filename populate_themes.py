#!/usr/bin/env python
"""
Script to populate the database with default themes
Run this after running migrations
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from Core.models import Theme

def populate_themes():
    """Create default themes in the database"""
    
    themes_data = [
        {
            'theme_id': 'default',
            'title': 'Default Theme',
            'description': 'The classic light theme with clean design.',
            'preview_icon': '☀️',
            'sp_cost': 0,
            'is_active': True
        },
        {
            'theme_id': 'dark',
            'title': 'Dark Theme',
            'description': 'Switch to a sleek dark theme perfect for late-night learning sessions.',
            'preview_icon': '🌙',
            'sp_cost': 100,
            'is_active': True
        },
        {
            'theme_id': 'cyberpunk',
            'title': 'Cyberpunk Theme',
            'description': 'Experience a futuristic neon-lit interface with cyberpunk aesthetics.',
            'preview_icon': '🌆',
            'sp_cost': 150,
            'is_active': True
        }
    ]
    
    for theme_data in themes_data:
        theme, created = Theme.objects.get_or_create(
            theme_id=theme_data['theme_id'],
            defaults=theme_data
        )
        
        if created:
            print(f"Created theme: {theme.title}")
        else:
            print(f"Theme already exists: {theme.title}")

if __name__ == '__main__':
    populate_themes()
    print("Theme population completed!")