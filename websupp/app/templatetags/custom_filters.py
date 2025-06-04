from django import template

register = template.Library()

@register.filter
def split_by(value, delimiter=','):
    return value.split(delimiter)

@register.filter
def trim(value):
    return value.strip()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})