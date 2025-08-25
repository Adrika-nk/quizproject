from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None
