from django.contrib import messages
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

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


# Views that create/change/delete data. Viewers are blocked from all of these.
# The finer-grained rules ("staff can't grant/remove admins") live in the
# views themselves, since they need to compare against a specific target user.
WRITE_VIEW_NAMES = {
    'pharmacy:prescription-add',
    'pharmacy:prescription-review',
    'pharmacy:prescription-review-label-pdf',
    'pharmacy:prescription-edit',
    'pharmacy:prescription-delete',
    'pharmacy:medication-add',
    'pharmacy:medication-edit',
    'pharmacy:medication-delete',
    'pharmacy:doctor-add',
    'pharmacy:doctor-edit',
    'pharmacy:doctor-delete',
    'pharmacy:client-add',
    'pharmacy:client-edit',
    'pharmacy:client-delete',
    'pharmacy:practice-edit',
    'pharmacy:practice-invite-send',
    'pharmacy:practice-staff-remove',
    'pharmacy:practice-staff-role',
}

# Of the views above, these are further restricted to admins only.
ADMIN_ONLY_VIEW_NAMES = {
    'pharmacy:practice-edit',
    'pharmacy:prescription-delete',
}


class PracticeRoleMiddleware:
    '''Enforces the two blanket role rules: viewers can't reach any write
    view, and non-admin staff can't edit the practice's own info.'''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and not user.is_superuser and user.practice_id:
            try:
                view_name = resolve(request.path).view_name
            except Resolver404:
                view_name = None

            if view_name in WRITE_VIEW_NAMES:
                if user.is_practice_viewer:
                    messages.error(request, "Viewers can't make changes.")
                    return redirect('landing')
                if view_name in ADMIN_ONLY_VIEW_NAMES and not user.is_practice_admin:
                    messages.error(request, "Only practice admins can do that.")
                    return redirect('landing')

        return self.get_response(request)
