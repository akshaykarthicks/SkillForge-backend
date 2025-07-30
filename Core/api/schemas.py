from ninja import Schema
from typing import List, Optional
from datetime import datetime

class LearningPathInput(Schema):
    goal: str
    time_available_per_week: int
    prior_experience: str

class LearningPhase(Schema):
    week: int
    topics: List[str]
    resources: List[str]
    time: str

class LearningPathOutput(Schema):
    duration: str
    phases: List[LearningPhase]

class UserSchema(Schema):
    id: int
    username: str
    email: str
    xp: int
    sp: int
    level: int
    completed_lessons: List[int]
    unlocked_skills: List[int]
    purchased_themes: List[str]
    active_theme: str

class LearningPathSchema(Schema):
    id: int
    title: str
    description: str
    category: str
    difficulty_level: str
    estimated_duration: str
    is_active: bool

class UserProgressSchema(Schema):
    total_lessons: int
    completed_lessons: int
    current_streak: int
    total_xp: int
    total_sp: int
    level: int
    progress_percentage: int

class SkillNodeSchema(Schema):
    id: int
    title: str
    description: str
    node_type: str
    sp_cost: int
    prerequisites: List[int]
    unlocked: bool
    position_x: float
    position_y: float

class SkillTreeSchema(Schema):
    id: int
    title: str
    description: str
    nodes: List[SkillNodeSchema]

# Authentication Schemas
class UserRegistrationSchema(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLoginSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefreshSchema(Schema):
    refresh_token: str

class UserProfileSchema(Schema):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    xp: int
    sp: int
    level: int
    completed_lessons: List[int]
    unlocked_skills: List[int]
    purchased_themes: List[str]
    active_theme: str
    created_at: datetime
    updated_at: datetime

class PasswordChangeSchema(Schema):
    old_password: str
    new_password: str

class PasswordResetRequestSchema(Schema):
    email: str

class PasswordResetConfirmSchema(Schema):
    token: str
    new_password: str

class MessageSchema(Schema):
    message: str
    success: bool = True

# Shop Schemas
class ThemeSchema(Schema):
    theme_id: str
    title: str
    description: str
    preview_icon: str
    sp_cost: int
    is_purchased: bool
    is_active: bool

class ShopThemesResponse(Schema):
    themes: List[ThemeSchema]
    user_sp: int

class ThemePurchaseResponse(Schema):
    message: str
    remaining_sp: int

class ThemeActivateResponse(Schema):
    message: str
    active_theme: str
