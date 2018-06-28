from django import template
from risk_management.users.models import BusinessUnit
from risk_register.models import ClasseDeRisques

register = template.Library()


@register.inclusion_tag('risk_register/bu_menu.html')
def bu_menu(li=True, li_class="nav_item", a_class="nav-link"):
    business_units = BusinessUnit.objects.all()
    return {
        'business_units': business_units,
        'li_class': li_class,
        'a_class': a_class,
        'li': li
    }


@register.inclusion_tag('risk_register/cl_menu.html')
def cl_menu(li=True, li_class="nav_item", a_class="nav-link"):
    classes = ClasseDeRisques.objects.all()
    return {
        'classes': classes,
        'li_class': li_class,
        'a_class': a_class,
        'li': li
    }
