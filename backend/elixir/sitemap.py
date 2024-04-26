from elixir.models import *
from lxml import etree
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from rest_framework.decorators import renderer_classes
from django.views.decorators.csrf import csrf_exempt
from elixirapp import settings

from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView



class GoogleSitemapRenderer(BaseRenderer):
    media_type = 'application/xml'
    format = 'xml'
    charset = 'iso-8859-1'

    def render(self, data, media_type=None, renderer_context=None):
        root = ET.Element('urlset')
        root.attrib['xmlns'] = 'http://www.sitemaps.org/schemas/sitemap/0.9'
        root.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        root.attrib['xsi:schemaLocation'] = 'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd'

        # add landing page
        url = ET.SubElement(root, 'url')
        loc = ET.SubElement(url, 'loc')
        loc.text = escape(settings.URL_FRONT)

        # add pages for each resource
        for el in Resource.objects.filter(visibility=1):
            url = ET.SubElement(root, 'url')
            loc = ET.SubElement(url, 'loc')
            loc.text = escape(settings.URL_FRONT + el.biotoolsID)
            lastmod = ET.SubElement(url, 'lastmod')
            lastmod.text = el.lastUpdate.isoformat()

        return ET.tostring(root)


class Sitemap(APIView):
    """
    Generate the sitemap
    """
    renderer_classes = (GoogleSitemapRenderer,)


    def get(self, request, format=None):
        return Response()