from django import template
from django import forms
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('includes/field_with_label.html')
def field_with_label(field):
    return {
        'field': field,
    }

@register.inclusion_tag('includes/form_field_bootstrap.html')
def form_field_bootstrap(field,
                         show_label=True,
                         show_help_text=False,
#                         label_first=True,
                         prepend_val=None,
                         append_val=None):

    # Odd behavior: `show_help_text=True` comes in as '' WTF?
    #               `show_help_text='True'` -> 'True'
    if show_help_text == 'True':
        show_help_text = True

    # Will be an empty string if the field doesn't exist
    if not field:
        return

    if type(field.field.widget) == forms.widgets.CheckboxInput:
        label_class = 'checkbox'
    else:
        label_class = 'control-label'

    if prepend_val:
        prepend_str = mark_safe(prepend_val)
    else:
        prepend_str = ''

    if append_val:
        append_str = mark_safe(append_val)
    else:
        append_str = ''

    return {
        'field': field,
        'show_help_text': show_help_text,
        'show_label': show_label,
#        'label_first': label_first,
        'prepend_val': prepend_str,
        'append_val': append_str,
        'label_class': label_class,
    }
