from django import template

register = template.Library()


@register.filter(name='addstr')
def addstr(arg1, arg2):
    """
    concatenate arg1 & arg2
    Ici, la seconde réponse explique que si on concatène en utilisant le filtre
    de base "add", alors il ne passe pas par str() mais convertit la totale
    en entiers s'il y a un entier, ce qui fait que par exemple :

    id="{{ "btn-edit-travel-"|add:v.obj.pk }}"

    me donnait du vide alors que via ce filtre qui fait le str() classique, tout
    fonctionne !
    http://stackoverflow.com/questions/
    4386168/how-to-concatenate-strings-in-django-templates

    Args:
        arg2: whatever, will be translated via str()
        arg1: whatever, will be translated via str()
    """
    return str(arg1) + str(arg2)


@register.filter(name='addstrp')
def addstrp(arg1, arg2):
    """
    Comme addstr() au dessus mais ajoute un espace entre les deux si nécessaire

    Args:
        arg2: whatever, will be translated via str()
        arg1: whatever, will be translated via str()
    """
    a = str(arg1)
    b = str(arg2)
    return u'{}{}{}'.format(a, ' ' if a and b else '', b)
