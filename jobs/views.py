from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Job, Result, AdmitCard, Category, UserProfile, JobApplication
from .forms import UserProfileForm, JobApplicationForm

def home(request):
    """Home page with latest jobs, results, and admit cards"""
    # Get category filter from query parameters
    category = request.GET.get('category')
    search_query = request.GET.get('q', '')
    
    # Base querysets
    jobs = Job.objects.filter(is_active=True)
    results = Result.objects.filter(is_active=True)
    admit_cards = AdmitCard.objects.filter(is_active=True)
    
    # Apply category filter if specified
    if category:
        try:
            category_id = int(category)
            jobs = jobs.filter(category_id=category_id)
            results = results.filter(category_id=category_id)
            admit_cards = admit_cards.filter(category_id=category_id)
        except ValueError:
            pass
    
    # Apply search filter if specified
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(organization__icontains=search_query) |
            Q(location__icontains=search_query)
        )
        results = results.filter(
            Q(title__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
        admit_cards = admit_cards.filter(
            Q(exam_name__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
    
    context = {
        'latest_jobs': jobs.order_by('-created_at')[:6],
        'latest_results': results.order_by('-result_date')[:6],
        'latest_admit_cards': admit_cards.order_by('-admit_card_date')[:6],
        'categories': Category.objects.all(),
        'selected_category': category,
        'search_query': search_query
    }
    return render(request, 'jobs/home.html', context)

def job_list(request):
    """List all active jobs with filtering and search"""
    # Get category filter from query parameters
    category = request.GET.get('category')
    search_query = request.GET.get('q', '')
    location = request.GET.get('location')
    salary = request.GET.get('salary')
    job_types = request.GET.getlist('job_type')
    experience = request.GET.get('experience')
    sort = request.GET.get('sort')
    
    # Base queryset
    jobs = Job.objects.filter(is_active=True)
    
    # Apply category filter if specified
    if category:
        try:
            category_id = int(category)
            jobs = jobs.filter(category_id=category_id)
        except ValueError:
            pass
    
    # Apply search filter if specified
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(organization__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Filter by location
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Filter by salary
    if salary:
        min_salary, max_salary = map(int, salary.split('-'))
        jobs = jobs.filter(salary_range__gte=min_salary, salary_range__lte=max_salary)
    
    # Filter by job type
    if job_types:
        jobs = jobs.filter(job_type__in=job_types)
    
    # Filter by experience
    if experience:
        jobs = jobs.filter(experience_level=experience)
    
    # Sort jobs
    if sort == 'latest':
        jobs = jobs.order_by('-created_at')
    elif sort == 'salary_high':
        jobs = jobs.order_by('-salary_range')
    elif sort == 'salary_low':
        jobs = jobs.order_by('salary_range')
    
    # Pagination
    paginator = Paginator(jobs, 12)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'categories': Category.objects.all(),
        'selected_category': category,
        'search_query': search_query,
        'location': location,
        'salary': salary,
        'job_types': job_types,
        'experience': experience
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, pk):
    """Detailed view of a specific job"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    job.views_count += 1
    job.save()
    
    # Check if user has applied
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(applicant__user=request.user, job=job).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'related_jobs': Job.objects.filter(category=job.category, is_active=True).exclude(pk=pk)[:3]
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def apply_job(request, pk):
    """Handle job application"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if JobApplication.objects.filter(applicant=user_profile, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = user_profile
            application.job = job
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', pk=pk)
    else:
        form = JobApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/apply_job.html', context)

def result_list(request):
    """List all active results with filtering and search"""
    # Get category filter from query parameters
    category = request.GET.get('category')
    search_query = request.GET.get('q', '')
    
    # Base queryset
    results = Result.objects.filter(is_active=True)
    
    # Apply category filter if specified
    if category:
        try:
            category_id = int(category)
            results = results.filter(category_id=category_id)
        except ValueError:
            pass
    
    # Apply search filter if specified
    if search_query:
        results = results.filter(
            Q(title__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(results, 12)
    page = request.GET.get('page')
    results = paginator.get_page(page)
    
    context = {
        'results': results,
        'categories': Category.objects.all(),
        'selected_category': category,
        'search_query': search_query
    }
    return render(request, 'jobs/result_list.html', context)

def result_detail(request, pk):
    """Detailed view of a specific result"""
    result = get_object_or_404(Result, pk=pk, is_active=True)
    result.views_count += 1
    result.save()
    
    context = {
        'result': result,
        'related_results': Result.objects.filter(category=result.category, is_active=True).exclude(pk=pk)[:3]
    }
    return render(request, 'jobs/result_detail.html', context)

def admitcard_list(request):
    """List all active admit cards with filtering and search"""
    # Get category filter from query parameters
    category = request.GET.get('category')
    search_query = request.GET.get('q', '')
    
    # Base queryset
    admit_cards = AdmitCard.objects.filter(is_active=True)
    
    # Apply category filter if specified
    if category:
        try:
            category_id = int(category)
            admit_cards = admit_cards.filter(category_id=category_id)
        except ValueError:
            pass
    
    # Apply search filter if specified
    if search_query:
        admit_cards = admit_cards.filter(
            Q(exam_name__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(admit_cards, 12)
    page = request.GET.get('page')
    admit_cards = paginator.get_page(page)
    
    # Get latest results and jobs for sidebar
    latest_results = Result.objects.filter(is_active=True).order_by('-result_date')[:5]
    latest_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'admit_cards': admit_cards,
        'categories': Category.objects.all(),
        'selected_category': category,
        'search_query': search_query,
        'latest_results': latest_results,
        'latest_jobs': latest_jobs
    }
    return render(request, 'jobs/admitcard_list.html', context)

def admit_card_detail(request, pk):
    """Detailed view of a specific admit card"""
    admit_card = get_object_or_404(AdmitCard, pk=pk, is_active=True)
    admit_card.views_count += 1
    admit_card.save()
    
    context = {
        'admit_card': admit_card,
        'related_admit_cards': AdmitCard.objects.filter(category=admit_card.category, is_active=True).exclude(pk=pk)[:3]
    }
    return render(request, 'jobs/admit_card_detail.html', context)

def search(request):
    """Global search functionality"""
    search_query = request.GET.get('q', '')
    category = request.GET.get('category')
    job_type = request.GET.get('job_type')
    location = request.GET.get('location')
    
    jobs = Job.objects.filter(is_active=True)
    results = Result.objects.filter(is_active=True)
    admit_cards = AdmitCard.objects.filter(is_active=True)
    
    # Apply filters
    if category:
        try:
            category_id = int(category)
            jobs = jobs.filter(category_id=category_id)
            results = results.filter(category_id=category_id)
            admit_cards = admit_cards.filter(category_id=category_id)
        except ValueError:
            pass
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(organization__icontains=search_query) |
            Q(location__icontains=search_query)
        )
        results = results.filter(
            Q(title__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
        admit_cards = admit_cards.filter(
            Q(exam_name__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
    
    # Pagination for jobs
    paginator = Paginator(jobs, 12)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    # Get popular categories
    popular_categories = Category.objects.annotate(
        job_count=Count('job')
    ).order_by('-job_count')[:5]
    
    context = {
        'jobs': jobs,
        'results': results[:10],
        'admit_cards': admit_cards[:10],
        'query': search_query,
        'selected_category': category,
        'selected_job_type': job_type,
        'selected_location': location,
        'categories': Category.objects.all(),
        'popular_categories': popular_categories
    }
    return render(request, 'jobs/search.html', context)

@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    # Get counts for each qualification level
    categories = Category.objects.all()
    category_stats = []
    
    for category in categories:
        stats = {
            'name': category.name,
            'total_jobs': Job.objects.filter(category=category).count(),
            'active_jobs': Job.objects.filter(category=category, is_active=True).count(),
            'total_results': Result.objects.filter(category=category).count(),
            'total_admit_cards': AdmitCard.objects.filter(category=category).count()
        }
        category_stats.append(stats)
    
    context = {
        'category_stats': category_stats,
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'total_results': Result.objects.count(),
        'total_admit_cards': AdmitCard.objects.count(),
        'total_applications': JobApplication.objects.count(),
        'recent_applications': JobApplication.objects.order_by('-applied_at')[:5]
    }
    return render(request, 'admin/dashboard.html', context)
