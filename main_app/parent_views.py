from django.http import HttpResponse

def parent_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.user_type != '4':
            return HttpResponse("Unauthorized", status=403)
        return view_func(request, *args, **kwargs)
    return wrapper