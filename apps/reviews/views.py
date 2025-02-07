from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from.models import Review
from.forms import ReviewForm, ReviewPhotoForm
from apps.bookings.models import Booking

@login_required
def create_review(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    try:
        review = Review.objects.get(booking=booking)
        return redirect('reviews:update_review', review.id)  # Redirect to update if review exists
    except Review.DoesNotExist:
        pass  # Proceed to create review if it doesn't exist

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        photo_form = ReviewPhotoForm(request.POST, request.FILES)
        if review_form.is_valid() and photo_form.is_valid():
            review = review_form.save(commit=False)
            review.booking = booking
            review.save()
            photo = photo_form.save(commit=False)
            photo.review = review
            photo.save()

            return redirect('reviews:review_detail', review.id)
    else:
        review_form = ReviewForm()
        photo_form = ReviewPhotoForm()

    return render(request, 'reviews/create_review.html', {
        'review_form': review_form,
        'photo_form': photo_form,
        'booking': booking
    })

@login_required
def update_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('reviews:review_detail', review.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/update_review.html', {'form': form, 'review': review})


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})

