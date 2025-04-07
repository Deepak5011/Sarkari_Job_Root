from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .models import Category, Job, Result, AdmitCard, UserProfile, JobApplication, AdminRole

@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'can_manage_users', 'can_manage_jobs', 'can_manage_results', 
                   'can_manage_admit_cards', 'can_manage_categories', 'can_manage_applications',
                   'can_view_analytics', 'created_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'userprofile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    def get_role(self, obj):
        return obj.userprofile.role.get_name_display() if obj.userprofile.role else '-'
    get_role.short_description = 'Role'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'password' in form.base_fields:
            form.base_fields['password'].help_text = _(
                "Raw passwords are not stored, so there is no way to see this "
                "user's password, but you can change the password using "
                "<a href=\"../password/\">this form</a>."
            )
        return form

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'category', 'location', 'salary_range', 
                   'job_type', 'experience_level', 'application_deadline', 'is_active')
    list_filter = ('category', 'job_type', 'experience_level', 'is_active', 'created_at')
    search_fields = ('title', 'organization', 'description')
    date_hierarchy = 'created_at'

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'category', 'result_date', 'is_active')
    list_filter = ('category', 'result_date', 'is_active', 'created_at')
    search_fields = ('title', 'organization', 'description')
    date_hierarchy = 'result_date'

@admin.register(AdmitCard)
class AdmitCardAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'organization', 'category', 'admit_card_date', 'is_active')
    list_filter = ('category', 'admit_card_date', 'is_active', 'created_at')
    search_fields = ('exam_name', 'organization', 'description')
    date_hierarchy = 'admit_card_date'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    list_filter = ('status', 'applied_at', 'job__category')
    search_fields = ('job__title', 'applicant__user__username', 'cover_letter')
    date_hierarchy = 'applied_at'

# Custom Admin Dashboard View
def admin_dashboard(request):
    # Sample data for statistics
    context = {
        'total_jobs': 150,
        'active_jobs': 45,
        'total_applications': 1250,
        'total_users': 3500,
        
        # Sample latest jobs
        'latest_jobs': [
            {
                'id': 1,
                'title': 'Software Engineer',
                'organization': 'Tech Solutions Inc.',
                'is_active': True,
            },
            {
                'id': 2,
                'title': 'Data Analyst',
                'organization': 'Data Analytics Corp',
                'is_active': True,
            },
            {
                'id': 3,
                'title': 'Project Manager',
                'organization': 'Project Management Co',
                'is_active': False,
            },
            {
                'id': 4,
                'title': 'Business Analyst',
                'organization': 'Business Solutions Ltd',
                'is_active': True,
            },
            {
                'id': 5,
                'title': 'UI/UX Designer',
                'organization': 'Design Studio',
                'is_active': True,
            },
        ],
        
        # Sample recent applications
        'recent_applications': [
            {
                'user': {'username': 'john_doe'},
                'job': {'title': 'Software Engineer'},
                'created_at': timezone.now() - timedelta(days=1),
                'status': 'pending',
                'status_color': 'warning',
                'get_status_display': lambda: 'Pending'
            },
            {
                'user': {'username': 'jane_smith'},
                'job': {'title': 'Data Analyst'},
                'created_at': timezone.now() - timedelta(days=2),
                'status': 'approved',
                'status_color': 'success',
                'get_status_display': lambda: 'Approved'
            },
            {
                'user': {'username': 'mike_wilson'},
                'job': {'title': 'Project Manager'},
                'created_at': timezone.now() - timedelta(days=3),
                'status': 'rejected',
                'status_color': 'danger',
                'get_status_display': lambda: 'Rejected'
            },
            {
                'user': {'username': 'sarah_jones'},
                'job': {'title': 'Business Analyst'},
                'created_at': timezone.now() - timedelta(days=4),
                'status': 'pending',
                'status_color': 'warning',
                'get_status_display': lambda: 'Pending'
            },
            {
                'user': {'username': 'david_brown'},
                'job': {'title': 'UI/UX Designer'},
                'created_at': timezone.now() - timedelta(days=5),
                'status': 'approved',
                'status_color': 'success',
                'get_status_display': lambda: 'Approved'
            },
        ],
    }
    
    return render(request, 'admin/dashboard.html', context)

# Custom admin site class
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(admin_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls

    def logout(self, request, extra_context=None):
        from django.contrib.auth.views import LogoutView
        return LogoutView.as_view(next_page='jobs:home')(request)

# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')

# Register models with custom admin site
admin_site.register(User, CustomUserAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Job, JobAdmin)
admin_site.register(Result, ResultAdmin)
admin_site.register(AdmitCard, AdmitCardAdmin)
admin_site.register(JobApplication, JobApplicationAdmin)
admin_site.register(AdminRole, AdminRoleAdmin)
admin_site.register(UserProfile)
