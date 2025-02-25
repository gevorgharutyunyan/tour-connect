from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from apps.common.models import Language, Location
from .forms import TourForm, TourDateForm, TourImageForm, TourDateFormSet
from .models import Tour, TourDate, TourImage


# ✅ Tour Views
# LIST VIEW: Show all active tours
class TourListView(ListView):
    model = Tour
    template_name = 'tours/tour_list.html'
    context_object_name = 'tours'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Tour.objects.filter(is_active=True)

        if 'q' in self.request.GET:
            query = self.request.GET.get('q')
            queryset = queryset.filter(title__icontains=query)

        if 'start_date' in self.request.GET and 'end_date' in self.request.GET:
            start_date = self.request.GET.get('start_date')
            end_date = self.request.GET.get('end_date')
            if start_date and end_date:
                # Filter tours with dates within the specified range
                queryset = queryset.filter(dates__start_date__range=[start_date, end_date]).distinct()

        return queryset


# DETAIL VIEW: Show single tour details
class TourDetailView(DetailView):
    model = Tour
    template_name = 'tours/tour_detail.html'
    context_object_name = 'tour'


# Mixin to restrict actions only for guides
class GuideRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'guide'


class TourCreateView(LoginRequiredMixin, CreateView):
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
            location_name = form.cleaned_data['location_name']
            location_country = form.cleaned_data['location_country']
            languages = form.cleaned_data['languages']
            location, created = Location.objects.get_or_create(name=location_name, country=location_country)
            form.instance.location = location
            languages_list = [lang.strip() for lang in languages.split(',')]
            languages = []
            for lang_name in languages_list:
                lang, created = Language.objects.get_or_create(name=lang_name)
                languages.append(lang)
            form.instance.guide = self.request.user
            self.object = form.save()
            self.object.languages.set(languages)
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
