from django import template
register = template.Library()

@register.inclusion_tag('navbar_features.html')
def navbar(active=None, inverse=False):
    """
    Shows the navbar,
    `active` :   is the index of which link to show active (if any)
        options --   'inbox', 'hardcover', 'standard', 'view'
    `inverse` :  whether to show the navbar in black
    """
    return {
        'active': active,
        'inverse': inverse,
    }