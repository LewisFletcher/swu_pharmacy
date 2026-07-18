from django import template
from crispy_forms.helper import FormHelper
from crispy_forms.utils import render_crispy_form

from theme.crispy import daisy_css_container

register = template.Library()


@register.simple_tag()
def crispy_fields(form):
    helper = FormHelper(form)
    helper.form_tag = False
    helper.disable_csrf = True
    return render_crispy_form(form, helper=helper, context={"css_container": daisy_css_container})


def _tag_set(tags):
    if not tags:
        return set()
    if isinstance(tags, str):
        tags = tags.split(",")
    return {t.strip() for t in tags if t.strip()}


@register.filter
def btn_classes(tags):
    tags = _tag_set(tags)
    if "cancel" in tags or "link" in tags:
        return "btn btn-ghost"
    if "danger" in tags:
        return "btn btn-error"
    if "secondary" in tags or "minor" in tags:
        return "btn-outline btn"
    if "outline" in tags:
        return "btn btn-outline btn-primary"
    return "btn btn-primary"


@register.filter
def badge_classes(tags):
    tags = _tag_set(tags)
    if "success" in tags:
        return "badge badge-success"
    if "warning" in tags:
        return "badge badge-warning"
    if "primary" in tags:
        return "badge badge-neutral"
    return "badge"
