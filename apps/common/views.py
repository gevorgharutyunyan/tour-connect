from django.shortcuts import render, redirect
from .models import Language, Location
from .forms import LanguageForm, LocationForm
from django.contrib.auth.decorators import login_required

@login_required
def add_language(request):
    if request.method == "POST":
        form = LanguageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tours:create-tour')  # Redirect to tour creation
    else:
        form = LanguageForm()
    return render(request, 'common/add_language.html', {'form': form})


@login_required
def add_location(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tours:create-tour')  # Redirect to tour creation
    else:
        form = LocationForm()
    return render(request, 'common/add_location.html', {'form': form})
