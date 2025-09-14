from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project URLs
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # Task URLs
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('project/<int:project_id>/task/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/complete/', views.complete_task, name='task_complete'),
    path('task/<int:task_id>/comment/', views.add_comment, name='add_comment'),
]