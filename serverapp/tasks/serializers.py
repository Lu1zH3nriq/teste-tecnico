from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    tags_list = serializers.ReadOnlyField(source='get_tags_list')
    owner_info = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()
    shared_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'due_date', 'completed_at', 'is_completed', 'tags',
            'tags_list', 'created_at', 'updated_at', 'owner',
            'owner_info', 'is_shared', 'shared_count',
            'is_overdue', 'days_until_due'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'completed_at', 'owner')
    
    def get_owner_info(self, obj):
        return {
            'id': obj.owner.id,
            'username': obj.owner.username,
            'first_name': obj.owner.first_name,
            'last_name': obj.owner.last_name,
            'email': obj.owner.email
        }
    
    def get_is_shared(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.owner != request.user
        return False
    
    def get_shared_count(self, obj):
        return obj.shared_with.count()
    
    def validate_tags(self, value):
        if value:
            tags = [tag.strip() for tag in value.split(',') if tag.strip()]
            return ', '.join(tags)
        return value
    
    def validate(self, attrs):
        if attrs.get('due_date'):
            from django.utils import timezone
            if attrs['due_date'] < timezone.now():
                pass
        return attrs

class TaskCreateSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        fields = [
            'title', 'description', 'priority', 'status',
            'due_date', 'tags'
        ]

class TaskUpdateSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        fields = [
            'title', 'description', 'priority', 'status',
            'due_date', 'tags'
        ]
    
    def validate_status(self, value):
        return value

class TaskListSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    tags_list = serializers.ReadOnlyField(source='get_tags_list')
    owner = serializers.StringRelatedField(read_only=True)
    owner_info = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()
    shared_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 
            'due_date', 'completed_at', 'is_completed', 'tags',
            'tags_list', 'created_at', 'updated_at', 'owner',
            'owner_info', 'is_shared', 'shared_count',
            'is_overdue', 'days_until_due'
        ]
    
    def get_owner_info(self, obj):
        return {
            'id': obj.owner.id,
            'username': obj.owner.username,
            'first_name': obj.owner.first_name,
            'last_name': obj.owner.last_name,
            'email': obj.owner.email
        }
    
    def get_is_shared(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.owner != request.user
        return False
    
    def get_shared_count(self, obj):
        return obj.shared_with.count()
