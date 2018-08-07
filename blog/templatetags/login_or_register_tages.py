from django import template

from ..forms import LoginForm, RegForm
register = template.Library()


@register.simple_tag
def get_login():
    return LoginForm()


@register.simple_tag
def get_register():
    return RegForm()
