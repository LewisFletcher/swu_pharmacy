from .crispy import daisy_css_container


def css_container(request):
    return {"css_container": daisy_css_container}
