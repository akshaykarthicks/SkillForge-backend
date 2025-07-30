from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, LearningPath, Module, Lesson, SkillTree, SkillNode,
    UserProgress, UserSkillUnlock, Theme, UserThemePurchase
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'xp', 'sp', 'level', 'is_active']
    list_filter = ['level', 'is_active', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Gamification', {'fields': ('xp', 'sp', 'level', 'completed_lessons', 'unlocked_skills')}),
        ('Themes', {'fields': ('purchased_themes', 'active_theme')}),
    )

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty_level', 'estimated_duration', 'is_active']
    list_filter = ['category', 'difficulty_level', 'is_active']
    search_fields = ['title', 'description']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'path', 'order']
    list_filter = ['path']
    ordering = ['path', 'order']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'sp_reward', 'xp_reward', 'order']
    list_filter = ['lesson_type', 'module__path']
    ordering = ['module', 'order']

@admin.register(SkillTree)
class SkillTreeAdmin(admin.ModelAdmin):
    list_display = ['title', 'path']

@admin.register(SkillNode)
class SkillNodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'skill_tree', 'node_type', 'sp_cost']
    list_filter = ['node_type', 'skill_tree']

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'score', 'completed_at']
    list_filter = ['completed', 'lesson__module__path']

@admin.register(UserSkillUnlock)
class UserSkillUnlockAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_node', 'unlocked_at']
    list_filter = ['skill_node__skill_tree']

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'theme_id', 'sp_cost', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'theme_id']

@admin.register(UserThemePurchase)
class UserThemePurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'purchased_at']
    list_filter = ['theme', 'purchased_at']
