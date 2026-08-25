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

@register.filter
def telefono_whatsapp(value):

    if value is None:
        return ""

    numero = str(value).strip()

    # Quitar espacios, guiones y paréntesis
    numero = (
        numero
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # ==========================================
    # YA VIENE COMO +569XXXXXXXX
    # ==========================================

    if numero.startswith("+569"):
        return numero


    # ==========================================
    # VIENE COMO 569XXXXXXXX
    # ==========================================

    if numero.startswith("569"):
        return "+" + numero


    # ==========================================
    # VIENE COMO 9XXXXXXXX
    # Ej: 912345678
    # ==========================================

    if numero.startswith("9") and len(numero) == 9:
        return "+56" + numero


    # ==========================================
    # OTROS CASOS
    # ==========================================

    return numero

@register.filter
def telefono_whatsapp_url(value):

    if value is None:
        return ""

    numero = str(value).strip()

    numero = (
        numero
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    if numero.startswith("569"):
        return numero

    if numero.startswith("9") and len(numero) == 9:
        return "56" + numero

    return numero