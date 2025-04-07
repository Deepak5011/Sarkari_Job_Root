from django.urls import path
from . import views
from django.contrib import admin
from django.urls import include

app_name = 'jobs'

urlpatterns = [
    # Home and Search
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    
    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    
    # Results
    path('results/', views.result_list, name='result_list'),
    path('results/<int:pk>/', views.result_detail, name='result_detail'),
    
    # Admit Cards
    path('admit-cards/', views.admitcard_list, name='admitcard_list'),
    path('admit-cards/<int:pk>/', views.admit_card_detail, name='admitcard_detail'),
]

# Override admin index to use our custom dashboard
admin.site.index = lambda request: admin.site.admin_view(views.admin_dashboard)(request) 