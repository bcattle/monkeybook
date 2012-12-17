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
        options = options or {}
        request = data.request
        data = self.to_simple(data, options)

        # Data is a list of bundles
        # For each, render the template and add to a list
        if 'error_message' in data:
            return simplejson.dumps(data, cls=json.DjangoJSONEncoder, sort_keys=True, ensure_ascii=False, indent=4)

        if hasattr(data, 'keys'):
            data = [data]

        for bundle in data:
            template = bundle.pop('template')
            request_context = RequestContext(request)
            bundle['rendered'] = render_to_string(template, bundle.pop('page_content'), request_context)

        return simplejson.dumps(data, cls=json.DjangoJSONEncoder, sort_keys=True, ensure_ascii=False)

