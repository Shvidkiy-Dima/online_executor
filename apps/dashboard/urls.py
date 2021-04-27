from django.urls import path
from dashboard import views


urlpatterns = [
    path('project/', views.ProjectView.as_view()),
    path('project/<int:pk>/', views.ProjectDetailView.as_view())
]