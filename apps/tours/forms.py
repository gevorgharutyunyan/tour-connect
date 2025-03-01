from django import forms
from .models import Tour, TourDate, TourImage
from django_countries.fields import CountryField
from django.forms import inlineformset_factory, BaseInlineFormSet
from apps.common.models import Language

class TourForm(forms.ModelForm):
    location_name = forms.CharField(max_length=100, required=True)
    location_country = CountryField().formfield(required=False)
    languages = forms.CharField(max_length=255, required=True, help_text="Enter languages separated by commas.")

    class Meta:
        model = Tour
        exclude = ['guide', 'created_at', 'updated_at', 'location', 'languages']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'included_services': forms.Textarea(attrs={'rows': 2}),
            'excluded_services': forms.Textarea(attrs={'rows': 2}),
            'cancellation_policy': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TourDateForm(forms.ModelForm):
    class Meta:
        model = TourDate
        fields = ['start_date', 'start_time', 'available_spots', 'price_override', 'is_available']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class BaseTourDateFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['start_time'].widget = forms.TimeInput(attrs={'type': 'time'})

TourDateFormSet = inlineformset_factory(
    Tour,
    TourDate,
    form=TourDateForm,
    formset=BaseTourDateFormSet,
    fields=('start_date', 'start_time', 'available_spots', 'price_override', 'is_available'),
    extra=1,
    can_delete=True
)

class TourImageForm(forms.ModelForm):
    class Meta:
        model = TourImage
        fields = ['image', 'caption', 'is_primary']

class TourFilterForm(forms.Form):
    min_price = forms.DecimalField(required=False, label='Minimum Price')
    max_price = forms.DecimalField(required=False, label='Maximum Price')
    min_participants = forms.IntegerField(required=False, label='Minimum Participants')
    max_participants = forms.IntegerField(required=False, label='Maximum Participants')
    difficulty = forms.ChoiceField(
        choices=[('', 'Any')] + list(Tour.DIFFICULTY_CHOICES),
        required=False,
        label='Difficulty Level'
    )
    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        required=False,
        label='Languages',
        widget=forms.CheckboxSelectMultiple
    )
    available_only = forms.BooleanField(
        required=False,
        initial=True,
        label='Show only available tours'
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('price_asc', 'Price (Low to High)'),
            ('price_desc', 'Price (High to Low)'),
            ('duration_asc', 'Duration (Shortest to Longest)'),
            ('duration_desc', 'Duration (Longest to Shortest)'),
        ],
        required=False,
        label='Sort by'
    )
