from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list_create, name='task_list_create'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/toggle/', views.task_toggle_complete, name='task_toggle_complete'),
    
]
