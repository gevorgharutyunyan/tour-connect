from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, IntegerField
from apps.common.models import Language, Location
from .forms import TourForm, TourDateForm, TourImageForm, TourDateFormSet, TourFilterForm
from .models import Tour, TourDate, TourImage, SavedSearch
from apps.reviews.models import Wishlist
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime


# ✅ Tour Views
# LIST VIEW: Show all active tours
class TourListView(ListView):
    model = Tour
    template_name = 'tours/tour_list.html'
    context_object_name = 'tours'
    ordering = ['-created_at']
    paginate_by = 12  # Show 12 tours per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TourFilterForm(self.request.GET)
        
        # Add query parameters to pagination links
        if self.request.GET:
            query = self.request.GET.copy()
            if 'page' in query:
                del query['page']
            context['query_params'] = query.urlencode()
        
        return context

    def get_queryset(self):
        # Start with all tours
        queryset = Tour.objects.all()
        
        # Filter for tours with future dates and available spots
        queryset = queryset.filter(
            dates__start_date__gte=timezone.now().date(),
            dates__max_spots__gt=F('dates__booked_spots')
        ).distinct()
        
        form = TourFilterForm(self.request.GET)

        # Basic search query
        if 'q' in self.request.GET:
            query = self.request.GET.get('q')
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )

        # Map bounds filter
        if all(key in self.request.GET for key in ['bounds_north', 'bounds_south', 'bounds_east', 'bounds_west']):
            try:
                north = float(self.request.GET.get('bounds_north'))
                south = float(self.request.GET.get('bounds_south'))
                east = float(self.request.GET.get('bounds_east'))
                west = float(self.request.GET.get('bounds_west'))
                queryset = queryset.filter(
                    latitude__lte=north,
                    latitude__gte=south,
                    longitude__lte=east,
                    longitude__gte=west
                )
            except (ValueError, TypeError):
                pass

        if form.is_valid():
            # Price range filter
            if form.cleaned_data.get('min_price'):
                queryset = queryset.filter(price__gte=form.cleaned_data['min_price'])
            if form.cleaned_data.get('max_price'):
                queryset = queryset.filter(price__lte=form.cleaned_data['max_price'])

            # Duration filter
            duration = form.cleaned_data.get('duration')
            if duration:
                queryset = queryset.filter(duration=duration)

            # Difficulty filter
            if form.cleaned_data.get('difficulty'):
                queryset = queryset.filter(difficulty=form.cleaned_data['difficulty'])

            # Date range filter
            if form.cleaned_data.get('start_date'):
                queryset = queryset.filter(dates__start_date__gte=form.cleaned_data['start_date'])
            if form.cleaned_data.get('end_date'):
                queryset = queryset.filter(dates__start_date__lte=form.cleaned_data['end_date'])

            # Group size filter
            if form.cleaned_data.get('group_size'):
                queryset = queryset.filter(max_participants__gte=form.cleaned_data['group_size'])

            # Languages filter
            if form.cleaned_data.get('languages'):
                queryset = queryset.filter(languages__in=form.cleaned_data['languages'])

            # Sorting
            sort_by = form.cleaned_data.get('sort_by')
            if sort_by:
                if sort_by == 'price_low':
                    queryset = queryset.order_by('price')
                elif sort_by == 'price_high':
                    queryset = queryset.order_by('-price')
                elif sort_by == 'rating':
                    queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
                elif sort_by == 'date_newest':
                    queryset = queryset.order_by('-created_at')
                elif sort_by == 'date_oldest':
                    queryset = queryset.order_by('created_at')

        return queryset.select_related('guide').prefetch_related('images', 'dates', 'languages')


# DETAIL VIEW: Show single tour details
class TourDetailView(DetailView):
    model = Tour
    template_name = 'tours/tour_detail.html'
    context_object_name = 'tour'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_in_wishlist'] = Wishlist.objects.filter(
                tourist=self.request.user,
                tour=self.object
            ).exists()
        return context


# Mixin to restrict actions only for guides
class GuideRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'guide'


class TourCreateView(LoginRequiredMixin, GuideRequiredMixin, CreateView):
    model = Tour
    form_class = TourForm
    template_name = 'tours/tour_create.html'
    success_url = reverse_lazy('tours:tour-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['tour_date_formset'] = TourDateFormSet(self.request.POST)
        else:
            # Create an empty Tour instance and pass it to the formset
            tour = Tour(guide=self.request.user)
            context['tour_date_formset'] = TourDateFormSet(instance=tour)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        tour_date_formset = context['tour_date_formset']
        
        if tour_date_formset.is_valid():
            # Set the guide
            form.instance.guide = self.request.user
            
            # Set the location
            form.instance.location = f"{form.cleaned_data['location_name']}, {form.cleaned_data['location_country'].name}"
            
            # Save the tour
            self.object = form.save()
            
            # Handle languages
            languages_list = [lang.strip() for lang in form.cleaned_data['languages'].split(',')]
            languages = []
            for lang_name in languages_list:
                lang, created = Language.objects.get_or_create(name=lang_name)
                languages.append(lang)
            self.object.languages.set(languages)
            
            # Save tour dates
            tour_date_formset.instance = self.object
            tour_date_formset.save()
            
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


# UPDATE VIEW: Guide edits their own tour
class TourUpdateView(LoginRequiredMixin, GuideRequiredMixin, UpdateView):
    model = Tour
    form_class = TourForm
    template_name = 'tours/tour_create.html'
    success_url = reverse_lazy('tours:tour-list')

    def get_queryset(self):
        return Tour.objects.filter(guide=self.request.user)  # Only allow editing own tours


# DELETE VIEW: Guide deletes their own tour
class TourDeleteView(LoginRequiredMixin, GuideRequiredMixin, DeleteView):
    model = Tour
    template_name = 'tours/tour_confirm_delete.html'
    success_url = reverse_lazy('tours:tour-list')

    def get_queryset(self):
        return Tour.objects.filter(guide=self.request.user)


# ✅ TourImage Views
class TourImageCreateView(LoginRequiredMixin, GuideRequiredMixin, CreateView):
    model = TourImage
    form_class = TourImageForm
    template_name = 'tours/tour_image_form.html'

    def form_valid(self, form):
        form.instance.tour = get_object_or_404(Tour, id=self.kwargs['tour_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.kwargs['tour_id']})


class TourImageUpdateView(LoginRequiredMixin, GuideRequiredMixin, UpdateView):
    model = TourImage
    form_class = TourImageForm
    template_name = 'tours/tour_image_form.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})


class TourImageDeleteView(LoginRequiredMixin, GuideRequiredMixin, DeleteView):
    model = TourImage
    template_name = 'tours/tour_image_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})


# ✅ TourDate Views
class TourDateCreateView(LoginRequiredMixin, GuideRequiredMixin, CreateView):
    model = TourDate
    form_class = TourDateForm
    template_name = 'tours/tour_date_form.html'

    def form_valid(self, form):
        form.instance.tour = get_object_or_404(Tour, id=self.kwargs['tour_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.kwargs['tour_id']})


class TourDateUpdateView(LoginRequiredMixin, GuideRequiredMixin, UpdateView):
    model = TourDate
    form_class = TourDateForm
    template_name = 'tours/tour_date_form.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})


class TourDateDeleteView(LoginRequiredMixin, GuideRequiredMixin, DeleteView):
    model = TourDate
    template_name = 'tours/tour_date_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})


def advanced_search(request):
    # Base queryset
    tours = Tour.objects.all()

    # Search query
    q = request.GET.get('q')
    if q:
        tours = tours.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q)
        )

    # Price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        tours = tours.filter(price__gte=min_price)
    if max_price:
        tours = tours.filter(price__lte=max_price)

    # Duration
    duration = request.GET.get('duration')
    if duration:
        if duration == '1-3':
            tours = tours.filter(duration__icontains='hour').exclude(duration__regex=r'[4-9]|1[0-9]')
        elif duration == '4-6':
            tours = tours.filter(duration__regex=r'[4-6]')
        elif duration == '7-12':
            tours = tours.filter(duration__regex=r'[7-9]|1[0-2]')
        elif duration == 'full-day':
            tours = tours.filter(duration__icontains='day')
        elif duration == 'multi-day':
            tours = tours.filter(duration__icontains='day').exclude(duration__icontains='1 day')

    # Difficulty level
    difficulty = request.GET.getlist('difficulty')
    if difficulty:
        tours = tours.filter(difficulty__in=difficulty)

    # Date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        tours = tours.filter(dates__start_date__range=[start_date, end_date])

    # Group size
    group_size = request.GET.get('group_size')
    if group_size:
        tours = tours.filter(max_participants__gte=group_size)

    # Sorting
    sort = request.GET.get('sort', 'relevance')
    if sort == 'price_low':
        tours = tours.order_by('price')
    elif sort == 'price_high':
        tours = tours.order_by('-price')
    elif sort == 'rating':
        tours = tours.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

    # Pagination
    paginator = Paginator(tours.distinct(), 12)  # 12 tours per page
    page = request.GET.get('page')
    tours = paginator.get_page(page)

    context = {
        'tours': tours,
        'today': timezone.now().date(),
    }

    return render(request, 'tours/advanced_search.html', context)

@login_required
def save_search_filters(request):
    if request.method == 'POST':
        filters = {
            'q': request.POST.get('q'),
            'min_price': request.POST.get('min_price'),
            'max_price': request.POST.get('max_price'),
            'duration': request.POST.get('duration'),
            'difficulty': request.POST.getlist('difficulty'),
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'group_size': request.POST.get('group_size'),
        }
        
        # Create a name for the saved search based on the filters
        name = f"Search from {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        
        SavedSearch.objects.create(
            user=request.user,
            name=name,
            filters=filters
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def get_saved_filters(request):
    saved_filters = SavedSearch.objects.filter(user=request.user).order_by('-created_at')
    filters = [{
        'id': f.id,
        'name': f.name,
        'filters': f.filters
    } for f in saved_filters]
    
    return JsonResponse({'filters': filters})

@login_required
def delete_saved_filter(request, filter_id):
    if request.method == 'POST':
        saved_filter = get_object_or_404(SavedSearch, id=filter_id, user=request.user)
        saved_filter.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def toggle_favorite(request, tour_id):
    if request.method == 'POST':
        tour = get_object_or_404(Tour, id=tour_id)
        if tour in request.user.favorite_tours.all():
            request.user.favorite_tours.remove(tour)
        else:
            request.user.favorite_tours.add(tour)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
