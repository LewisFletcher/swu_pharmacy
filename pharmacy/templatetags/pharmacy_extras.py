from dal_alight.widgets import AlightWidgetMixin
from django import template

register = template.Library()


@register.filter
def is_autocomplete(field):
    '''True if the bound field's widget is a django-autocomplete-light (alight) widget.'''
    return isinstance(field.field.widget, AlightWidgetMixin)


@register.filter
def can_manage(actor, target):
    '''True if `actor` may change `target`'s practice role or remove them.'''
    return actor.can_manage(target)


@register.filter
def grantable_roles(user):
    '''The (value, label) practice-role choices `user` is allowed to grant.'''
    return [(value, label) for value, label in user.PracticeRole.choices if user.can_grant_role(value)]
