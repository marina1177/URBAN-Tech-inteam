from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

def main_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    if user.groups.filter(name='Contractor').exists():
        return redirect('/contractor')
    if user.groups.filter(name='Governor').exists():
        return redirect('/governor')
    if user.groups.filter(name='Citizen').exists():
        return redirect('/citizen')
    if user.is_superuser:
        return redirect('/admin')
    raise PermissionDenied

def error_forbidden(request, exception=None):
    return HttpResponse('<h1>You are not allowed to view this content</h1>', status=403)
