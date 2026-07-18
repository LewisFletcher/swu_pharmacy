from dal_alight.widgets import AlightWidgetMixin
from django import template

register = template.Library()


@register.filter
def is_autocomplete(field):
    '''True if the bound field's widget is a django-autocomplete-light (alight) widget.'''
    return isinstance(field.field.widget, AlightWidgetMixin)
