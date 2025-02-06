from django import forms
from .models import Tour, TourDate, TourImage
from apps.common.models import Language, Location


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        exclude = ['guide', 'created_at', 'updated_at']
        languages = forms.ModelMultipleChoiceField(
            queryset=Language.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True
        )

        location = forms.ModelChoiceField(
            queryset=Location.objects.all(),
            empty_label="Select a Location",
            required=True
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'included_services': forms.Textarea(attrs={'rows': 2}),
            'excluded_services': forms.Textarea(attrs={'rows': 2}),
            'cancellation_policy': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        guide = kwargs.pop('guide', None)  # Get the guide instance
        super().__init__(*args, **kwargs)
        if guide:
            # Ensure the guide can only select their own locations
            self.fields['location'].queryset = guide.locations.all()


class TourDateForm(forms.ModelForm):
    class Meta:
        model = TourDate
        fields = ['start_date', 'end_date', 'start_time', 'available_spots', 'price_override', 'is_available']


class TourImageForm(forms.ModelForm):
    class Meta:
        model = TourImage
        fields = ['image', 'caption', 'is_primary']
