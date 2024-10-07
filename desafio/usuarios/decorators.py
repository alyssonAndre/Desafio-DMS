from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

def locador_required(view_func):
    @login_required(redirect_field_name='login')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.userprofile.is_locador:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
