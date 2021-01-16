from django.shortcuts import render


def my_custom_page_not_found_view(request, exception, template_name='404.html'):
    return render(request, template_name)


def my_custom_error_view(request, *args, **argv):
    return render(request, '500.html', status=500)
