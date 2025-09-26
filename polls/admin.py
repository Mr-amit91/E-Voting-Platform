from django.contrib import admin
from .models import Poll, Choice, Vote

# Register your models here.

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_by', 'start_date', 'end_date', 'is_active', 'total_votes']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['question', 'description']
    readonly_fields = ['created_date']

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'poll', 'vote_count']
    list_filter = ['poll']
    search_fields = ['choice_text']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'choice', 'voted_at']
    list_filter = ['voted_at', 'choice__poll']
    search_fields = ['user__username', 'choice__choice_text']
