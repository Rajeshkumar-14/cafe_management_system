from django.shortcuts import redirect, render

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            if user.groups.filter(name="Administration").exists():
                return redirect("administration-home")
            elif user.groups.filter(name="Staff").exists():
                return redirect("index")
            else:
                pass
        return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "authentication/403.html")

        return wrapper_func

    return decorator
