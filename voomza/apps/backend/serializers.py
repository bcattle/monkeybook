from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.core.serializers import json
from tastypie.serializers import Serializer

class DjangoTemplateSerializer(Serializer):
    """
    A serializer that renders the template in data
    if HTML format is requested
    """
    def to_json(self, data, options=None):
        # Data is a list of bundles
        # For each, render the template and add to a list
        rendered_strings = []
        for bundle in data:
            template = bundle.data.pop('template')
            request_context = RequestContext(bundle.request)
            rendered_string = render_to_string(template, bundle.data['page_content'], request_context)
            rendered_strings.append(rendered_string)

        results = {
            'meta': data['meta'],
            'objects': rendered_strings
        }
        return simplejson.dumps(results, cls=json.DjangoJSONEncoder, sort_keys=True)