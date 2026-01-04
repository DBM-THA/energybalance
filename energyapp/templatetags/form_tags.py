from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def de_number(value, decimals=2):
    """
    15027.0 -> '15.027,00'
    """
    try:
        n = float(value)
    except (TypeError, ValueError):
        return ""

    d = int(decimals)
    s = f"{n:,.{d}f}"  # 15,027.00
    # US -> DE
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s
