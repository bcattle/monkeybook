from django import template
register = template.Library()

@register.inclusion_tag('navbar_features.html', takes_context=True)
def navbar(context, active=None, inverse=False, empty=False):
    """
    Shows the navbar,
    `active` :   is the index of which link to show active (if any)
        options --   'inbox', 'hardcover', 'standard', 'view'
    `inverse` :  whether to show the navbar in black
    """
    return {
        'user': context['request'].user,
        'active': active,
        'inverse': inverse,
        'empty': empty
    }

@register.inclusion_tag('navbar_js.html', takes_context=True)
def navbar_js(context):
    return {
        'user': context['request'].user,
    }

