"""
Provides XML parsing support.
"""

import datetime
import decimal

from django.conf import settings
# from django.utils import six
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser

from lxml import etree as lxmletree


class XMLSchemaParser(BaseParser):
	"""
	XML parser.
	"""

	media_type = 'application/xml'

	def parse(self, stream, media_type=None, parser_context=None):
		"""
		Parses the incoming bytestream as XML and returns the resulting data.
		"""

		# Identical to biotools_3.3.0.xsd except no maxOccurs="unbounded" on the "tool" element
		with open('/elixir/application/backend/elixir/biotoolsSchema/biotools_3.3.0-singletool.xsd', 'r') as f:
			schema_root = lxmletree.XML(f.read())
		
		schema = lxmletree.XMLSchema(schema_root)
		xmlparser = lxmletree.XMLParser(schema=schema)
		xml_tree = None

		try:
			xml_string = stream.read()
			xml_tree = lxmletree.fromstring(xml_string, parser=xmlparser)
			#xml_tree = etree.parse(stream, parser=xmlparser, forbid_dtd=True)
		
			# redundant call if single-tool.xsd is used, still useful just in case
			if len(xml_tree) > 1:
				raise ParseError("Can only work with a single tool at a time")
			
			#xslt for transforming from biotoolsSchema to generic xml from django
			xslt1 = lxmletree.parse('/elixir/application/backend/elixir/biotoolsSchema/biotoolsSchema_3.3.0_XML_to_framework_XML_xslt1.0.xslt')
			transform1 = lxmletree.XSLT(xslt1)
			dom = lxmletree.fromstring(xml_string)
			newdom = transform1(dom)


			# removing empty elements
			xslt2 = lxmletree.parse("/elixir/application/backend/elixir/biotoolsSchema/removeEmptyElements.xslt")
			transform2 = lxmletree.XSLT(xslt2)
			newdom2 = transform2(newdom)
			root = newdom2.getroot()

		except (lxmletree.XMLSyntaxError, Exception) as e:
			raise ParseError('XML validation error - %s -- Note that you can only register one tool at a time.' % e)


		#raise ParseError('got here')
		# assert etree, 'XMLParser requires defusedxml to be installed'

		# parser_context = parser_context or {}
		# encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
		# parser = etree.DefusedXMLParser(encoding=encoding)
		# try:
		# 	tree = etree.parse(stream, parser=parser, forbid_dtd=True)
		# except (etree.ParseError, ValueError) as exc:
		# 	raise ParseError('XML parse error - %s' % six.text_type(exc))
		#data = self._xml_convert(tree.getroot())
		data = self._xml_convert(root)

		return data

	def _xml_convert(self, element):
		"""
		convert the xml `element` into the corresponding python object
		"""

		children = list(element)


		if len(children) == 0:
			return self._type_convert(element.text)
		else:
			# if the fist child tag is list-item means all children are list-item
			if children[0].tag == "list-item":
				data = []
				for child in children:
					# version needs to be string otherwise it gets a validation error
					if element.tag.lower() == 'version':
						child.text = str(child.text)
					data.append(self._xml_convert(child))
			else:
				data = {}
				for child in children:
					data[child.tag] = self._xml_convert(child)

			return data

	def _type_convert(self, value):
		"""
		Converts the value returned by the XMl parse into the equivalent
		Python type
		"""

		# added to fix values of properties like version which should be strings, but they can look like numbers
		if isinstance(value, str):
			return value

		if value is None:
			return value

		try:
			return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
		except ValueError:
			pass

		try:
			return int(value)
		except ValueError:
			pass

		try:
			return decimal.Decimal(value)
		except decimal.InvalidOperation:
			pass

		return value