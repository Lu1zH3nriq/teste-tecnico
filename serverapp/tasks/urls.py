from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list_create, name='task_list_create'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/toggle/', views.task_toggle_complete, name='task_toggle_complete'),
    path('<int:task_id>/share/', views.task_share, name='task_share'),
    path('<int:task_id>/shared-users/', views.task_shared_users, name='task_shared_users'),
    path('<int:task_id>/remove-user/', views.task_remove_user, name='task_remove_user'),
]
