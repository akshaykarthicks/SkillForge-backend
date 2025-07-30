from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
import json

class CustomUser(AbstractUser):
    """Extended user model with gamification features"""
    xp = models.IntegerField(default=0)
    sp = models.IntegerField(default=0)  # Skill Points
    level = models.IntegerField(default=1)
    completed_lessons = models.JSONField(default=list)  # List of lesson IDs
    unlocked_skills = models.JSONField(default=list)    # List of skill node IDs
    purchased_themes = models.JSONField(default=lambda: ['default'])  # List of purchased theme IDs
    active_theme = models.CharField(max_length=50, default='default')  # Currently active theme
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_level(self):
        """Calculate level based on XP"""
        return min(100, (self.xp // 1000) + 1)

    def save(self, *args, **kwargs):
        self.level = self.calculate_level()
        super().save(*args, **kwargs)

class LearningPath(models.Model):
    """Learning paths/courses"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    difficulty_level = models.CharField(
        max_length=20, 
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')]
    )
    estimated_duration = models.CharField(max_length=50)  # e.g., "6 weeks"
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Module(models.Model):
    """Modules within a learning path"""
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField()  # Order within the path
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.path.title} - {self.title}"

class Lesson(models.Model):
    """Individual lessons within modules"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()  # Rich text content
    lesson_type = models.CharField(
        max_length=20,
        choices=[('lesson', 'Lesson'), ('quiz', 'Quiz'), ('project', 'Project')]
    )
    quiz_data = models.JSONField(blank=True, null=True)  # Quiz questions and answers
    sp_reward = models.IntegerField(default=10)  # Skill points reward
    xp_reward = models.IntegerField(default=50)  # Experience points reward
    order = models.IntegerField()
    estimated_time = models.IntegerField(help_text="Estimated time in minutes")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"

class SkillTree(models.Model):
    """Skill trees for learning paths"""
    path = models.OneToOneField(LearningPath, on_delete=models.CASCADE, related_name='skill_tree')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"Skill Tree: {self.title}"

class SkillNode(models.Model):
    """Individual skill nodes in the skill tree"""
    skill_tree = models.ForeignKey(SkillTree, on_delete=models.CASCADE, related_name='nodes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    node_type = models.CharField(
        max_length=20,
        choices=[('passive', 'Passive'), ('active', 'Active')]
    )
    sp_cost = models.IntegerField()  # Cost in skill points
    prerequisites = models.JSONField(default=list)  # List of required skill node IDs
    unlocked_content = models.JSONField(default=dict)  # What this skill unlocks
    position_x = models.FloatField(default=0)  # For visualization
    position_y = models.FloatField(default=0)  # For visualization
    
    def __str__(self):
        return f"{self.skill_tree.title} - {self.title}"

class UserProgress(models.Model):
    """Track user progress through lessons"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)  # Quiz score if applicable
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

class UserSkillUnlock(models.Model):
    """Track which skills users have unlocked"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    skill_node = models.ForeignKey(SkillNode, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'skill_node']
    
    def __str__(self):
        return f"{self.user.username} unlocked {self.skill_node.title}"

class Theme(models.Model):
    """Available themes in the shop"""
    theme_id = models.CharField(max_length=50, unique=True)  # e.g., 'dark', 'cyberpunk'
    title = models.CharField(max_length=200)
    description = models.TextField()
    preview_icon = models.CharField(max_length=10, default='🎨')  # Emoji icon
    sp_cost = models.IntegerField(default=0)  # Cost in skill points (0 for default theme)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class UserThemePurchase(models.Model):
    """Track user theme purchases"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'theme']
    
    def __str__(self):
        return f"{self.user.username} purchased {self.theme.title}"
