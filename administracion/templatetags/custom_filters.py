from django import template

register = template.Library()

@register.filter
def get_atributo(obj, atributo):

    field_name = atributo.lower().replace(" ", "_")

    if isinstance(obj, dict):
        return obj.get(field_name, '')

    return getattr(obj, field_name, '')


@register.filter
def to_str(value):
    return str(value)