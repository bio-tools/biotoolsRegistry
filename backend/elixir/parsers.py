from rest_framework import parsers

class XMLSchemaParser(parsers.BaseParser):
    """
    XMLSchemaParser text parser.
    """
    media_type = 'text/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()