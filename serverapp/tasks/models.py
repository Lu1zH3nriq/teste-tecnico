from django.db import models
from django.contrib.auth.models import User
from core.models import UserOwnedModel


class Task(UserOwnedModel):
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Brief description of the task"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the task"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the task"
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the task"
    )
    
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the task should be completed"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the task was marked as completed"
    )
    
    is_completed = models.BooleanField(
        default=False,
        help_text="Whether the task is completed"
    )
    
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags for categorization"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['owner', 'priority']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.is_completed:
            self.is_completed = True
            if not self.completed_at:
                from django.utils import timezone
                self.completed_at = timezone.now()
        elif self.status != 'completed' and self.is_completed:
            self.is_completed = False
            self.completed_at = None
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if not self.due_date or self.is_completed:
            return False
        
        from django.utils import timezone
        return timezone.now() > self.due_date
    
    @property
    def days_until_due(self):
        if not self.due_date:
            return None
        
        from django.utils import timezone
        delta = self.due_date - timezone.now()
        return delta.days
    
    def get_tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
