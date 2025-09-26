from django import forms
from .models import Poll, Choice
from django.utils import timezone
from datetime import timedelta


class PollCreationForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question', 'description', 'end_date']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your poll question', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter poll description (optional)'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default end date to 7 days from now
        if not self.instance.pk:
            default_end = timezone.now() + timedelta(days=7)
            self.fields['end_date'].initial = default_end.strftime('%Y-%m-%dT%H:%M')

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date and end_date <= timezone.now():
            raise forms.ValidationError('End date must be in the future.')
        return end_date


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'description']
        widgets = {
            'choice_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter choice text', 'required': True}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter choice description (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choice_text'].required = True


# Formset for multiple choices
ChoiceFormSet = forms.modelformset_factory(
    Choice,
    form=ChoiceForm,
    extra=2,  # Start with 2 empty forms
    min_num=2,  # Require at least 2 choices
    max_num=10,  # Allow maximum 10 choices
    can_delete=True
)