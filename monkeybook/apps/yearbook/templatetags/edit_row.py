from django import template
register = template.Library()

@register.inclusion_tag('includes/edit_row.html')
def edit_row(page, index=0):
    return {
        'page': page,
        'index': index,
    }