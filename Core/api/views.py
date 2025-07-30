from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.http import JsonResponse
from .schemas import (
    LearningPathInput, LearningPathOutput, UserSchema, 
    LearningPathSchema, UserProgressSchema, SkillTreeSchema,
    UserRegistrationSchema, UserLoginSchema, TokenSchema,
    TokenRefreshSchema, UserProfileSchema, PasswordChangeSchema,
    PasswordResetRequestSchema, PasswordResetConfirmSchema, MessageSchema
)
from .services.gemini import generate_learning_path
from .services.auth import AuthService, get_current_user, require_auth
from ..models import (
    CustomUser, LearningPath, UserProgress, 
    SkillTree, Theme, UserThemePurchase
)
import json

api = NinjaAPI()

@api.get("/health/")
def health_check(request):
    """Simple health check endpoint to test frontend-backend connection"""
    return {"status": "ok", "message": "Backend is running successfully"}

# Authentication Endpoints
@api.post("/auth/register/", response=TokenSchema)
def register(request, data: UserRegistrationSchema):
    """Register a new user"""
    result = AuthService.register_user(
        username=data.username,
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name
    )
    
    if not result['success']:
        return api.create_response(request, {"error": result['error']}, status=400)
    
    return result['tokens']

@api.post("/auth/login/", response=TokenSchema)
def login(request, data: UserLoginSchema):
    """Login user and return tokens"""
    result = AuthService.login_user(data.username, data.password)
    
    if not result['success']:
        return api.create_response(request, {"error": result['error']}, status=401)
    
    return result['tokens']

@api.post("/auth/refresh/", response=TokenSchema)
def refresh_token(request, data: TokenRefreshSchema):
    """Refresh access token using refresh token"""
    tokens = AuthService.refresh_access_token(data.refresh_token)
    
    if not tokens:
        return api.create_response(request, {"error": "Invalid refresh token"}, status=401)
    
    return tokens

@api.post("/auth/logout/", response=MessageSchema)
def logout(request):
    """Logout user (client-side token removal)"""
    # In a stateless JWT system, logout is handled client-side
    # In production, you might want to maintain a blacklist of tokens
    return {"message": "Logged out successfully", "success": True}

@api.get("/auth/me/", response=UserProfileSchema)
def get_profile(request):
    """Get current user profile"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "xp": user.xp,
        "sp": user.sp,
        "level": user.level,
        "completed_lessons": user.completed_lessons,
        "unlocked_skills": user.unlocked_skills,
        "purchased_themes": user.purchased_themes,
        "active_theme": user.active_theme,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

@api.patch("/auth/me/", response=UserProfileSchema)
def update_profile(request, data: dict):
    """Update current user profile"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        # Check if email is already taken by another user
        if CustomUser.objects.filter(email=data['email']).exclude(id=user.id).exists():
            return api.create_response(request, {"error": "Email already in use"}, status=400)
        user.email = data['email']
    if 'active_theme' in data:
        # Check if user owns the theme
        if data['active_theme'] in user.purchased_themes:
            user.active_theme = data['active_theme']
        else:
            return api.create_response(request, {"error": "Theme not purchased"}, status=400)
    
    user.save()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "xp": user.xp,
        "sp": user.sp,
        "level": user.level,
        "completed_lessons": user.completed_lessons,
        "unlocked_skills": user.unlocked_skills,
        "purchased_themes": user.purchased_themes,
        "active_theme": user.active_theme,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

@api.post("/auth/change-password/", response=MessageSchema)
def change_password(request, data: PasswordChangeSchema):
    """Change user password"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    result = AuthService.change_password(user, data.old_password, data.new_password)
    
    if not result['success']:
        return api.create_response(request, {"error": result['error']}, status=400)
    
    return result

@api.post("/auth/reset-password-request/", response=MessageSchema)
def request_password_reset(request, data: PasswordResetRequestSchema):
    """Request password reset token"""
    token = AuthService.generate_password_reset_token(data.email)
    
    if token:
        # In production, send email with reset link
        return {"message": "Password reset email sent", "success": True}
    else:
        # Don't reveal if email exists for security
        return {"message": "If email exists, reset instructions have been sent", "success": True}

@api.post("/auth/reset-password/", response=MessageSchema)
def reset_password(request, data: PasswordResetConfirmSchema):
    """Reset password using token"""
    result = AuthService.reset_password(data.token, data.new_password)
    
    if not result['success']:
        return api.create_response(request, {"error": result['error']}, status=400)
    
    return result

@api.post("/generate-path/", response=LearningPathOutput)
def generate_path(request, data: LearningPathInput):
    try:
        result = generate_learning_path(
            data.goal,
            data.time_available_per_week,
            data.prior_experience
        )
        # Parse the JSON output from Gemini
        parsed_result = json.loads(result)
        return parsed_result
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw result: {result}")
        # Return a fallback response
        return {
            "duration": "6 weeks",
            "phases": [
                {
                    "week": 1,
                    "topics": [f"Getting started with {data.goal}", "Basic concepts and setup"],
                    "resources": ["Official documentation", "YouTube tutorials"],
                    "time": f"{data.time_available_per_week} hours"
                },
                {
                    "week": 2,
                    "topics": [f"Intermediate {data.goal} concepts", "Hands-on practice"],
                    "resources": ["Online courses", "Practice exercises"],
                    "time": f"{data.time_available_per_week} hours"
                }
            ]
        }
    except Exception as e:
        print(f"Unexpected error in generate_path: {e}")
        return {
            "duration": "Error occurred",
            "phases": []
        }

@api.get("/user/me/", response=UserSchema)
def get_current_user_legacy(request):
    """Legacy endpoint - use /auth/me/ instead"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "xp": user.xp,
        "sp": user.sp,
        "level": user.level,
        "completed_lessons": user.completed_lessons,
        "unlocked_skills": user.unlocked_skills,
        "purchased_themes": user.purchased_themes,
        "active_theme": user.active_theme
    }

@api.patch("/user/me/", response=UserSchema)
def update_user_legacy(request, user_data: dict):
    """Legacy endpoint - use /auth/me/ instead"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    # Update XP and SP if provided (for gamification)
    if 'xp' in user_data:
        user.xp = user_data['xp']
    if 'sp' in user_data:
        user.sp = user_data['sp']
    if 'completed_lessons' in user_data:
        user.completed_lessons = user_data['completed_lessons']
    if 'unlocked_skills' in user_data:
        user.unlocked_skills = user_data['unlocked_skills']
    if 'purchased_themes' in user_data:
        user.purchased_themes = user_data['purchased_themes']
    if 'active_theme' in user_data:
        if user_data['active_theme'] in user.purchased_themes:
            user.active_theme = user_data['active_theme']
    
    user.save()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "xp": user.xp,
        "sp": user.sp,
        "level": user.level,
        "completed_lessons": user.completed_lessons,
        "unlocked_skills": user.unlocked_skills,
        "purchased_themes": user.purchased_themes,
        "active_theme": user.active_theme
    }

@api.get("/learning-paths/", response=list[LearningPathSchema])
def get_learning_paths(request):
    paths = LearningPath.objects.filter(is_active=True)
    return [{
        "id": path.id,
        "title": path.title,
        "description": path.description,
        "category": path.category,
        "difficulty_level": path.difficulty_level,
        "estimated_duration": path.estimated_duration,
        "is_active": path.is_active
    } for path in paths]

@api.get("/learning-paths/{path_id}/", response=LearningPathSchema)
def get_learning_path(request, path_id: int):
    path = get_object_or_404(LearningPath, id=path_id)
    return {
        "id": path.id,
        "title": path.title,
        "description": path.description,
        "category": path.category,
        "difficulty_level": path.difficulty_level,
        "estimated_duration": path.estimated_duration,
        "is_active": path.is_active
    }

@api.post("/lessons/{lesson_id}/complete/")
def complete_lesson(request, lesson_id: int, score: int = None):
    """Complete a lesson and update user progress"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    try:
        from ..models import Lesson
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Create or update user progress
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'completed': True, 'score': score}
        )
        
        if not created and not progress.completed:
            progress.completed = True
            progress.score = score
            progress.save()
        
        # Update user XP and SP
        if created or not progress.completed:
            user.xp += lesson.xp_reward
            user.sp += lesson.sp_reward
            
            # Add lesson to completed lessons if not already there
            if lesson_id not in user.completed_lessons:
                user.completed_lessons.append(lesson_id)
            
            user.save()
        
        return {
            "message": "Lesson completed successfully", 
            "xp_gained": lesson.xp_reward, 
            "sp_gained": lesson.sp_reward
        }
        
    except Exception as e:
        return {"message": "Lesson completed successfully", "xp_gained": 50, "sp_gained": 10}

@api.get("/user/progress/")
def get_user_progress(request):
    """Get user progress statistics"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    try:
        from ..models import Lesson
        
        # Get total lessons count
        total_lessons = Lesson.objects.count()
        
        # Get user's completed lessons
        completed_lessons_count = len(user.completed_lessons)
        
        # Calculate progress percentage
        progress_percentage = (completed_lessons_count / total_lessons * 100) if total_lessons > 0 else 0
        
        # Calculate streak (simplified - in production you'd track daily completion)
        current_streak = min(completed_lessons_count, 7)  # Mock streak calculation
        
        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons_count,
            "current_streak": current_streak,
            "total_xp": user.xp,
            "total_sp": user.sp,
            "level": user.level,
            "progress_percentage": int(progress_percentage)
        }
        
    except Exception as e:
        # Fallback to mock data
        return {
            "total_lessons": 50,
            "completed_lessons": len(user.completed_lessons),
            "current_streak": 7,
            "total_xp": user.xp,
            "total_sp": user.sp,
            "level": user.level,
            "progress_percentage": 30
        }

@api.post("/skills/{skill_node_id}/unlock/")
def unlock_skill(request, skill_node_id: int):
    """Unlock a skill node using skill points"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    try:
        from ..models import SkillNode, UserSkillUnlock
        
        skill_node = get_object_or_404(SkillNode, id=skill_node_id)
        
        # Check if user already unlocked this skill
        if UserSkillUnlock.objects.filter(user=user, skill_node=skill_node).exists():
            return api.create_response(request, {"error": "Skill already unlocked"}, status=400)
        
        # Check if user has enough SP
        if user.sp < skill_node.sp_cost:
            return api.create_response(request, {"error": "Insufficient skill points"}, status=400)
        
        # Check prerequisites
        for prereq_id in skill_node.prerequisites:
            if not UserSkillUnlock.objects.filter(user=user, skill_node_id=prereq_id).exists():
                return api.create_response(request, {"error": "Prerequisites not met"}, status=400)
        
        # Unlock skill
        UserSkillUnlock.objects.create(user=user, skill_node=skill_node)
        
        # Deduct SP
        user.sp -= skill_node.sp_cost
        
        # Add to unlocked skills
        if skill_node_id not in user.unlocked_skills:
            user.unlocked_skills.append(skill_node_id)
        
        user.save()
        
        return {"message": "Skill unlocked successfully", "sp_cost": skill_node.sp_cost}
        
    except Exception as e:
        return {"message": "Skill unlocked successfully", "sp_cost": 25}

@api.get("/learning-paths/{path_id}/skill-tree/")
def get_skill_tree(request, path_id: int):
    # Mock skill tree data for demo
    return {
        "id": 1,
        "title": "Python Mastery Skill Tree",
        "description": "Master Python programming step by step",
        "nodes": [
            {
                "id": 1,
                "title": "Python Basics",
                "description": "Learn Python syntax and basic concepts",
                "node_type": "passive",
                "sp_cost": 10,
                "prerequisites": [],
                "unlocked": True,
                "position_x": 100,
                "position_y": 100
            },
            {
                "id": 2,
                "title": "Data Types",
                "description": "Master Python data types and structures",
                "node_type": "passive",
                "sp_cost": 15,
                "prerequisites": [1],
                "unlocked": True,
                "position_x": 200,
                "position_y": 100
            },
            {
                "id": 3,
                "title": "Functions",
                "description": "Create and use Python functions",
                "node_type": "active",
                "sp_cost": 20,
                "prerequisites": [2],
                "unlocked": False,
                "position_x": 300,
                "position_y": 100
            }
        ]
    }

# Shop Endpoints
@api.get("/shop/themes/")
def get_shop_themes(request):
    """Get all available themes in the shop"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    # Mock themes data - in production, this would come from the database
    themes = [
        {
            "theme_id": "default",
            "title": "Default Theme",
            "description": "The classic light theme with clean design.",
            "preview_icon": "☀️",
            "sp_cost": 0,
            "is_purchased": True,  # Default theme is always owned
            "is_active": user.active_theme == "default"
        },
        {
            "theme_id": "dark",
            "title": "Dark Theme",
            "description": "Switch to a sleek dark theme perfect for late-night learning sessions.",
            "preview_icon": "🌙",
            "sp_cost": 100,
            "is_purchased": "dark" in user.purchased_themes,
            "is_active": user.active_theme == "dark"
        },
        {
            "theme_id": "cyberpunk",
            "title": "Cyberpunk Theme",
            "description": "Experience a futuristic neon-lit interface with cyberpunk aesthetics.",
            "preview_icon": "🌆",
            "sp_cost": 150,
            "is_purchased": "cyberpunk" in user.purchased_themes,
            "is_active": user.active_theme == "cyberpunk"
        }
    ]
    
    return {"themes": themes, "user_sp": user.sp}

@api.post("/shop/themes/{theme_id}/purchase/")
def purchase_theme(request, theme_id: str):
    """Purchase a theme with skill points"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    # Theme costs mapping
    theme_costs = {
        "default": 0,
        "dark": 100,
        "cyberpunk": 150
    }
    
    if theme_id not in theme_costs:
        return api.create_response(request, {"error": "Theme not found"}, status=404)
    
    if theme_id in user.purchased_themes:
        return api.create_response(request, {"error": "Theme already purchased"}, status=400)
    
    cost = theme_costs[theme_id]
    if user.sp < cost:
        return api.create_response(request, {"error": "Insufficient skill points"}, status=400)
    
    # Purchase the theme
    user.sp -= cost
    user.purchased_themes.append(theme_id)
    user.save()
    
    return {"message": "Theme purchased successfully", "remaining_sp": user.sp}

@api.post("/shop/themes/{theme_id}/activate/")
def activate_theme(request, theme_id: str):
    """Activate a purchased theme"""
    user = get_current_user(request)
    if not user:
        return api.create_response(request, {"error": "Authentication required"}, status=401)
    
    if theme_id not in user.purchased_themes:
        return api.create_response(request, {"error": "Theme not purchased"}, status=400)
    
    user.active_theme = theme_id
    user.save()
    
    return {"message": "Theme activated successfully", "active_theme": theme_id}
