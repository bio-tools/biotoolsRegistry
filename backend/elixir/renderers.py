from rest_framework import renderers

class XMLSchemaRenderer(renderers.BaseRenderer):
    media_type = 'text/xml'
    format = 'text'

    def render(self, data, media_type=None, renderer_context=None):
        return data