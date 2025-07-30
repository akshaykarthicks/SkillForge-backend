import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from ...models import CustomUser
from typing import Optional, Dict, Any

class AuthService:
    """Authentication service for JWT token management"""
    
    @staticmethod
    def generate_tokens(user: CustomUser) -> Dict[str, Any]:
        """Generate access and refresh tokens for a user"""
        now = timezone.now()
        
        # Access token payload
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'exp': now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
            'iat': now,
            'type': 'access'
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user.id,
            'exp': now + timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME),
            'iat': now,
            'type': 'refresh'
        }
        
        access_token = jwt.encode(
            access_payload, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        refresh_token = jwt.encode(
            refresh_payload, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME
        }
    
    @staticmethod
    def verify_token(token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check token type
            if payload.get('type') != token_type:
                return None
                
            # Check expiration
            if payload.get('exp', 0) < timezone.now().timestamp():
                return None
                
            return payload
            
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[CustomUser]:
        """Get user from access token"""
        payload = AuthService.verify_token(token, 'access')
        if not payload:
            return None
            
        try:
            user = CustomUser.objects.get(id=payload['user_id'])
            return user
        except CustomUser.DoesNotExist:
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        """Generate new access token from refresh token"""
        payload = AuthService.verify_token(refresh_token, 'refresh')
        if not payload:
            return None
            
        try:
            user = CustomUser.objects.get(id=payload['user_id'])
            return AuthService.generate_tokens(user)
        except CustomUser.DoesNotExist:
            return None
    
    @staticmethod
    def register_user(username: str, email: str, password: str, 
                     first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            return {'error': 'Invalid email format', 'success': False}
        
        # Check if username exists
        if CustomUser.objects.filter(username=username).exists():
            return {'error': 'Username already exists', 'success': False}
        
        # Check if email exists
        if CustomUser.objects.filter(email=email).exists():
            return {'error': 'Email already registered', 'success': False}
        
        # Validate password strength
        if len(password) < 8:
            return {'error': 'Password must be at least 8 characters long', 'success': False}
        
        try:
            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name or '',
                last_name=last_name or ''
            )
            
            # Generate tokens
            tokens = AuthService.generate_tokens(user)
            
            return {
                'user': user,
                'tokens': tokens,
                'success': True
            }
            
        except Exception as e:
            return {'error': f'Registration failed: {str(e)}', 'success': False}
    
    @staticmethod
    def login_user(username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        user = authenticate(username=username, password=password)
        
        if not user:
            return {'error': 'Invalid credentials', 'success': False}
        
        if not user.is_active:
            return {'error': 'Account is disabled', 'success': False}
        
        tokens = AuthService.generate_tokens(user)
        
        return {
            'user': user,
            'tokens': tokens,
            'success': True
        }
    
    @staticmethod
    def change_password(user: CustomUser, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        if not check_password(old_password, user.password):
            return {'error': 'Current password is incorrect', 'success': False}
        
        if len(new_password) < 8:
            return {'error': 'New password must be at least 8 characters long', 'success': False}
        
        user.set_password(new_password)
        user.save()
        
        return {'message': 'Password changed successfully', 'success': True}
    
    @staticmethod
    def generate_password_reset_token(email: str) -> Optional[str]:
        """Generate password reset token"""
        try:
            user = CustomUser.objects.get(email=email)
            
            # Create a secure token
            token_data = f"{user.id}:{user.email}:{timezone.now().timestamp()}"
            token = hashlib.sha256(token_data.encode()).hexdigest()
            
            # In a real application, you would store this token in the database
            # with an expiration time and send it via email
            
            return token
            
        except CustomUser.DoesNotExist:
            return None
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> Dict[str, Any]:
        """Reset password using token"""
        # In a real application, you would verify the token from the database
        # This is a simplified implementation
        
        if len(new_password) < 8:
            return {'error': 'Password must be at least 8 characters long', 'success': False}
        
        # For demo purposes, we'll just return success
        # In production, you would:
        # 1. Verify token exists and hasn't expired
        # 2. Get user from token
        # 3. Update password
        # 4. Invalidate token
        
        return {'message': 'Password reset successfully', 'success': True}


class AuthMiddleware:
    """Custom authentication middleware for Django Ninja"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user = AuthService.get_user_from_token(token)
            
            if user:
                request.user = user
                request.auth = token
            else:
                request.user = None
                request.auth = None
        else:
            request.user = None
            request.auth = None
        
        response = self.get_response(request)
        return response


def get_current_user(request):
    """Helper function to get current authenticated user"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    user = AuthService.get_user_from_token(token)
    
    return user


def require_auth(func):
    """Decorator to require authentication for API endpoints"""
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return {'error': 'Authentication required', 'success': False}, 401
        
        request.user = user
        return func(request, *args, **kwargs)
    
    return wrapper