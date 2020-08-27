"""
Provides XML rendering support.
"""
from __future__ import unicode_literals

from django.utils import six
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import force_text
from rest_framework.renderers import BaseRenderer
from lxml import etree as lxmletree
from rest_framework.exceptions import ParseError
import json

class XMLSchemaRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    item_tag_name = 'list-item'
    root_tag_name = 'root'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        stream = StringIO() 

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, {})

        self._to_xml(xml, data)

        xml.endElement(self.root_tag_name)
        xml.endDocument()

        #raise AssertionError(type(stream.getvalue()));
        generic_xml = stream.getvalue()

        if data.get('count') != None and data.get('list') != None:
            # deal with multiple tools
            xmlfile = 'multiple.xslt';
        else:
            # deal with a single tool
            xmlfile = 'framework_XML_to_biotoolsSchema_3.3.0_XML_xslt1.0.xslt';


        try:
            xslt1 = lxmletree.parse('/elixir/application/backend/elixir/biotoolsSchema/' + xmlfile)
            transform1 = lxmletree.XSLT(xslt1)
            dom = lxmletree.fromstring(generic_xml)
            newdom = transform1(dom)

            # removing empty elements
            xslt2 = lxmletree.parse("/elixir/application/backend/elixir/biotoolsSchema/removeEmptyElements.xslt")
            transform2 = lxmletree.XSLT(xslt2)
            newdom2 = transform2(newdom)

        except (lxmletree.XMLSyntaxError, Exception) as e:
            raise ParseError('XML error - %s. Please notify registry-support@elixir-dk.org if you see this error. ' % e)

        return lxmletree.tostring(newdom2)

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement(self.item_tag_name, {})
                self._to_xml(xml, item)
                xml.endElement(self.item_tag_name)

        elif isinstance(data, dict):
            for key, value in six.iteritems(data):
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(force_text(data))


from rdflib import ConjunctiveGraph
from elixir.biotools_to_bioschemas import rdfize
from boltons.iterutils import remap
import ast

class JSONLDRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'jsonld'

    def render(self, data, media_type=None, renderer_context=None):
        # return smart_text(data, encoding=self.charset)
        data['biotoolsID'] = data["biotoolsID"].lower()
        
        
        # this was the initial way
        # jsonld = rdfize(data)


        # but we might change to this to remove empty properties
        #   when Alban's code will work. Now it won't because it doesn't test for empty arrays
        # tool = json.loads(json.dumps(data.serializer._data))
        # drop_false = lambda path, key, value: bool(value)
        # tool_cleaned = remap(tool, visit=drop_false)

        jsonld = rdfize(data)
        

        temp_graph = ConjunctiveGraph()
        temp_graph.parse(data=jsonld, format="json-ld")
        return temp_graph.serialize(
            format="json-ld",
            auto_compact=True
        )

