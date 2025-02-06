from apps.common.models import Language, Location
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView

from .forms import TourForm, TourDateForm, TourImageForm
from .models import Tour, TourDate, TourImage


# ✅ Tour Views
# LIST VIEW: Show all active tours
class TourListView(ListView):
    model = Tour
    template_name = 'tour/tour_list.html'
    context_object_name = 'tours'
    ordering = ['-created_at']

    def get_queryset(self):
        return Tour.objects.filter(is_active=True)


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
    success_url = reverse_lazy('tours:tour-list')  # Redirect after successful creation

    def form_valid(self, form):
        form.instance.guide = self.request.user  # Assign logged-in user as guide
        return super().form_valid(form)


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
    template_name = 'tours/tourimage_form.html'

    def form_valid(self, form):
        form.instance.tour = get_object_or_404(Tour, id=self.kwargs['tour_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.kwargs['tour_id']})


class TourImageUpdateView(LoginRequiredMixin, GuideRequiredMixin, UpdateView):
    model = TourImage
    form_class = TourImageForm
    template_name = 'tours/tourimage_form.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})


class TourImageDeleteView(LoginRequiredMixin, GuideRequiredMixin, DeleteView):
    model = TourImage
    template_name = 'tours/tourimage_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})


# ✅ TourDate Views
class TourDateCreateView(LoginRequiredMixin, GuideRequiredMixin, CreateView):
    model = TourDate
    form_class = TourDateForm
    template_name = 'tours/tourdate_form.html'

    def form_valid(self, form):
        form.instance.tour = get_object_or_404(Tour, id=self.kwargs['tour_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.kwargs['tour_id']})


class TourDateUpdateView(LoginRequiredMixin, GuideRequiredMixin, UpdateView):
    model = TourDate
    form_class = TourDateForm
    template_name = 'tours/tourdate_form.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})


class TourDateDeleteView(LoginRequiredMixin, GuideRequiredMixin, DeleteView):
    model = TourDate
    template_name = 'tours/tourdate_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('tours:tour-detail', kwargs={'pk': self.object.tour.id})
