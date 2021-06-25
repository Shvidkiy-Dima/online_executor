from django.urls import path
from dashboard import views


urlpatterns = [
    path('project/', views.ProjectView.as_view()),
    path('project/<int:pk>/', views.ProjectDetailView.as_view()),

    path('module/', views.ModuleCreateView.as_view()),
    path('module/<uuid:pk>/', views.ModuleDetailView.as_view()),
    path('module/<uuid:pk>/run/', views.ModuleRunView.as_view()),

    path('package/', views.PackageView.as_view()),
    path('package/<int:pk>/', views.PackageDetailView.as_view()),



]


user_api_urlpatterns = [
    path('<str:project_name>/<uuid:pk>/', views.ModuleRunApiView.as_view())
]