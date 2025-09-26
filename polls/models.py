from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Poll(models.Model):
    question = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question
    
    def is_voting_open(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.is_active
    
    def total_votes(self):
        return Vote.objects.filter(choice__poll=self).count()


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.choice_text
    
    def vote_count(self):
        return self.vote_set.count()
    
    def vote_percentage(self):
        total = self.poll.total_votes()
        if total == 0:
            return 0
        return (self.vote_count() / total) * 100


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} voted for {self.choice.choice_text}"
