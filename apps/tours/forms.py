from django import forms
from .models import Tour, TourDate, TourImage
from django_countries.fields import CountryField
from django.forms import inlineformset_factory, BaseInlineFormSet
from apps.common.models import Language

class TourForm(forms.ModelForm):
    location_name = forms.CharField(max_length=100, required=True)
    location_country = CountryField().formfield(required=False)
    languages = forms.CharField(max_length=255, required=True, help_text="Enter languages separated by commas.")
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, required=True, help_text="Enter the latitude coordinate")
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, required=True, help_text="Enter the longitude coordinate")

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
        fields = ['start_date', 'start_time', 'max_spots', 'booked_spots']
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
    fields=('start_date', 'start_time', 'max_spots', 'booked_spots'),
    extra=1,
    can_delete=True
)

class TourImageForm(forms.ModelForm):
    image = forms.ImageField(
        required=True,
        help_text='Maximum size: 5MB'
    )
    
    class Meta:
        model = TourImage
        fields = ['image']
        
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5242880:  # 5MB in bytes
                raise forms.ValidationError("Image is too large. Maximum size is 5MB.")
        return image

class TourFilterForm(forms.Form):
    # Search query
    q = forms.CharField(required=False, label='Search')
    
    # Price range
    min_price = forms.DecimalField(required=False, label='Minimum Price')
    max_price = forms.DecimalField(required=False, label='Maximum Price')
    
    # Duration
    DURATION_CHOICES = [
        ('', 'Any Duration'),
        ('1-3', '1-3 hours'),
        ('4-6', '4-6 hours'),
        ('7-12', '7-12 hours'),
        ('full-day', 'Full Day'),
        ('multi-day', 'Multi Day')
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, required=False, label='Duration')
    
    # Difficulty level
    difficulty = forms.ChoiceField(
        choices=[('', 'Any')] + list(Tour.DIFFICULTY_CHOICES),
        required=False,
        label='Difficulty Level'
    )
    
    # Date range
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Group size
    group_size = forms.IntegerField(required=False, min_value=1, label='Minimum Group Size')
    
    # Languages
    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        required=False,
        label='Languages',
        widget=forms.CheckboxSelectMultiple
    )
    
    # Map bounds (for map-based search)
    bounds_north = forms.FloatField(required=False, widget=forms.HiddenInput())
    bounds_south = forms.FloatField(required=False, widget=forms.HiddenInput())
    bounds_east = forms.FloatField(required=False, widget=forms.HiddenInput())
    bounds_west = forms.FloatField(required=False, widget=forms.HiddenInput())
    
    # Sorting
    SORT_CHOICES = [
        ('', 'Relevance'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('rating', 'Rating'),
        ('date_newest', 'Date: Newest First'),
        ('date_oldest', 'Date: Oldest First')
    ]
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label='Sort by')
    
    # Show only available tours
    available_only = forms.BooleanField(required=False, initial=True, label='Show only available tours')
