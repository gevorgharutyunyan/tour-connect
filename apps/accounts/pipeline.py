# apps/accounts/pipeline.py
from django.contrib.auth import get_user_model
from django.contrib.auth import login

User = get_user_model()

def associate_existing_user(backend, details, user=None, *args, **kwargs):
    """
    If an existing user with the same email is found, link the Google account instead of creating a duplicate.
    """
    if user:
        return {'user': user}

    email = details.get('email')
    if email:
        try:
            existing_user = User.objects.get(email=email)
            return {'user': existing_user}
        except User.DoesNotExist:
            return


def save_profile(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user is None:
        return

    request = strategy.request

    if not hasattr(user, 'backend'):
        user.backend = 'social_core.backends.google.GoogleOAuth2'  # Specify the backend

    login(request, user, backend=user.backend)  # Pass the backend explicitly

    if not user.user_type:
        strategy.session_set('user_id', user.id)
        return strategy.redirect('/accounts/google-select-user-type/')

    return
