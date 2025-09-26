from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from .models import Poll, Choice, Vote
from .forms import PollCreationForm, ChoiceFormSet

# Create your views here.

@login_required
def index(request):
    # Get search query
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    polls = Poll.objects.filter(is_active=True)
    
    # Apply search filter
    if search_query:
        polls = polls.filter(
            Q(question__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(created_by__username__icontains=search_query)
        )
    
    # Apply status filter
    now = timezone.now()
    if status_filter == 'active':
        polls = polls.filter(start_date__lte=now, end_date__gte=now)
    elif status_filter == 'upcoming':
        polls = polls.filter(start_date__gt=now)
    elif status_filter == 'closed':
        polls = polls.filter(end_date__lt=now)
    
    # Order by creation date
    polls = polls.order_by('-created_date')
    
    context = {
        'polls': polls,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'polls/index.html', context)


@login_required
def detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    
    # Check if user has already voted
    user_vote = Vote.objects.filter(user=request.user, choice__poll=poll).first()
    
    context = {
        'poll': poll,
        'user_vote': user_vote,
        'voting_open': poll.is_voting_open()
    }
    return render(request, 'polls/detail.html', context)


@login_required
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    
    if not poll.is_voting_open():
        messages.error(request, 'Voting for this poll is closed.')
        return redirect('polls:detail', poll_id=poll.id)
    
    # Check if user has already voted
    existing_vote = Vote.objects.filter(user=request.user, choice__poll=poll).first()
    if existing_vote:
        messages.warning(request, 'You have already voted in this poll.')
        return redirect('polls:results', poll_id=poll.id)
    
    try:
        selected_choice = poll.choices.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, 'You must select a valid choice.')
        return redirect('polls:detail', poll_id=poll.id)
    
    try:
        vote = Vote(user=request.user, choice=selected_choice)
        vote.save()
        messages.success(request, 'Your vote has been recorded!')
    except IntegrityError:
        messages.error(request, 'An error occurred while recording your vote.')
        return redirect('polls:detail', poll_id=poll.id)
    
    return redirect('polls:results', poll_id=poll.id)


@login_required
def results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    
    # Check if user has voted
    user_vote = Vote.objects.filter(user=request.user, choice__poll=poll).first()
    
    context = {
        'poll': poll,
        'user_vote': user_vote
    }
    return render(request, 'polls/results.html', context)


@login_required
def create_poll(request):
    if request.method == 'POST':
        poll_form = PollCreationForm(request.POST)
        choice_formset = ChoiceFormSet(request.POST)
        
        if poll_form.is_valid() and choice_formset.is_valid():
            with transaction.atomic():
                # Save the poll
                poll = poll_form.save(commit=False)
                poll.created_by = request.user
                poll.start_date = timezone.now()
                poll.save()
                
                # Save choices
                valid_choices = 0
                for choice_form in choice_formset:
                    if choice_form.cleaned_data and not choice_form.cleaned_data.get('DELETE', False):
                        if choice_form.cleaned_data.get('choice_text'):
                            choice = choice_form.save(commit=False)
                            choice.poll = poll
                            choice.save()
                            valid_choices += 1
                
                if valid_choices < 2:
                    messages.error(request, 'A poll must have at least 2 choices.')
                    poll.delete()
                    return render(request, 'polls/create_poll.html', {
                        'poll_form': poll_form,
                        'choice_formset': choice_formset,
                    })
                
                messages.success(request, 'Poll created successfully!')
                return redirect('polls:detail', poll_id=poll.id)
    else:
        poll_form = PollCreationForm()
        choice_formset = ChoiceFormSet(queryset=Choice.objects.none())
    
    return render(request, 'polls/create_poll.html', {
        'poll_form': poll_form,
        'choice_formset': choice_formset,
    })


@login_required
def my_polls(request):
    user_polls = Poll.objects.filter(created_by=request.user).order_by('-created_date')
    return render(request, 'polls/my_polls.html', {'polls': user_polls})


@login_required
def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id, created_by=request.user)
    
    # Check if poll is still active for editing
    if not poll.is_voting_open():
        messages.error(request, 'Cannot edit a closed poll.')
        return redirect('polls:my_polls')
    
    if request.method == 'POST':
        poll_form = PollCreationForm(request.POST, instance=poll)
        choice_formset = ChoiceFormSet(request.POST, queryset=poll.choices.all())
        
        if poll_form.is_valid() and choice_formset.is_valid():
            with transaction.atomic():
                poll = poll_form.save()
                
                # Save choices
                valid_choices = 0
                for choice_form in choice_formset:
                    if choice_form.cleaned_data:
                        if choice_form.cleaned_data.get('DELETE', False):
                            if choice_form.instance.pk:
                                choice_form.instance.delete()
                        elif choice_form.cleaned_data.get('choice_text'):
                            choice = choice_form.save(commit=False)
                            choice.poll = poll
                            choice.save()
                            valid_choices += 1
                
                if valid_choices < 2:
                    messages.error(request, 'A poll must have at least 2 choices.')
                    return render(request, 'polls/edit_poll.html', {
                        'poll_form': poll_form,
                        'choice_formset': choice_formset,
                        'poll': poll,
                    })
                
                messages.success(request, 'Poll updated successfully!')
                return redirect('polls:detail', poll_id=poll.id)
    else:
        poll_form = PollCreationForm(instance=poll)
        choice_formset = ChoiceFormSet(queryset=poll.choices.all())
    
    return render(request, 'polls/edit_poll.html', {
        'poll_form': poll_form,
        'choice_formset': choice_formset,
        'poll': poll,
    })


@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id, created_by=request.user)
    
    if request.method == 'POST':
        poll_title = poll.question
        poll.delete()
        messages.success(request, f'Poll "{poll_title}" has been deleted successfully.')
        return redirect('polls:my_polls')
    
    return render(request, 'polls/delete_poll.html', {'poll': poll})


from django.http import JsonResponse

def api_poll_results(request, poll_id):
    """API endpoint for real-time poll results"""
    poll = get_object_or_404(Poll, pk=poll_id)
    
    choices_data = []
    for choice in poll.choices.all():
        choices_data.append({
            'id': choice.id,
            'text': choice.choice_text,
            'description': choice.description,
            'vote_count': choice.vote_count(),
            'percentage': choice.vote_percentage(),
        })
    
    data = {
        'poll_id': poll.id,
        'question': poll.question,
        'total_votes': poll.total_votes(),
        'choices': choices_data,
        'is_voting_open': poll.is_voting_open(),
    }
    
    return JsonResponse(data)
