from django.shortcuts import redirect

# Paths that must stay reachable even for a signed-in user with no practice yet:
# auth pages (so they can even log in/out), the practice setup page itself
# (so they can create one), and the invite-accept link (so they can join one).
EXEMPT_PATH_PREFIXES = (
    '/admin/',
    '/accounts/',
    '/static/',
    '/media/',
    '/__reload__/',
    '/__debug__/',
    '/pharmacy/practice/setup/',
    '/pharmacy/practice/invite/',
)


class PracticeRequiredMiddleware:
    '''Blocks every page behind a "set up your practice" wall until the
    logged-in user has a practice, except for a short exempt list.

    NOTE: this only gates *access*, it doesn't scope querysets to a practice.
    That's a deliberate, separate follow-up (see project notes).
    '''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if (
            user
            and user.is_authenticated
            and not user.is_superuser
            and not user.practice_id
            and not request.path.startswith(EXEMPT_PATH_PREFIXES)
        ):
            return redirect('pharmacy:practice-setup')
        return self.get_response(request)
