import json

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join


register = template.Library()


@register.simple_tag
def modern_script():
    manifest = finders.find('modern/manifest.json')
    if not manifest:
        return ''  # Unbuilt assets leave ordinary links and forms operational.
    with open(manifest) as source:
        entry = json.load(source)['src/main.js']
    styles = format_html_join('', '<link rel="stylesheet" href="{}">',
                              ((static('modern/' + path),) for path in entry.get('css', [])))
    return format_html('{}<script type="module" src="{}"></script>',
                       styles, static('modern/' + entry['file']))
