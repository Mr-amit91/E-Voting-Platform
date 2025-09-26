from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from django.utils import timezone
from .forms import CustomUserCreationForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {username}!')
            login(request, user)
            return redirect('polls:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('polls:index')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
        form.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        return form


class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['get', 'post']
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile(request):
    from polls.models import Poll, Vote
    
    # Get user statistics
    user_polls = Poll.objects.filter(created_by=request.user)
    user_votes = Vote.objects.filter(user=request.user)
    
    # Calculate statistics
    stats = {
        'total_polls_created': user_polls.count(),
        'active_polls': user_polls.filter(is_active=True, end_date__gt=timezone.now()).count(),
        'total_votes_cast': user_votes.count(),
        'total_votes_received': Vote.objects.filter(choice__poll__created_by=request.user).count(),
    }
    
    # Recent polls created
    recent_polls = user_polls.order_by('-created_date')[:5]
    
    # Recent votes cast
    recent_votes = user_votes.select_related('choice__poll').order_by('-voted_at')[:5]
    
    context = {
        'stats': stats,
        'recent_polls': recent_polls,
        'recent_votes': recent_votes,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def voting_history(request):
    from polls.models import Vote
    
    user_votes = Vote.objects.filter(user=request.user).select_related(
        'choice__poll'
    ).order_by('-voted_at')
    
    context = {
        'votes': user_votes,
        'total_votes': user_votes.count(),
    }
    
    return render(request, 'accounts/voting_history.html', context)
