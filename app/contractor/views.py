from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def can_behave_as_contractor(user):
    return user.is_superuser or user.groups.filter(name='Contractor').exists()

def contractor_view(request):
    context = {}
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    if can_behave_as_contractor(request.user):
        return render(request, 'contractor/index.html', context)
    raise PermissionDenied
