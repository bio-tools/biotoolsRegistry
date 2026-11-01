"""Generate/check the local resource descriptor before backend activation."""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from elixir.resource_ui import DIRECTORY, SchemaUnavailable, build_descriptor, compatibility, sources


class Command(BaseCommand):
    help = 'Generate or check the resource UI descriptor; reject incompatible transitions.'

    def add_arguments(self, parser):
        parser.add_argument('--schema', default=str(getattr(settings, 'RESOURCE_SCHEMA_PATH', DIRECTORY / 'biotools_3.3.0-singletool.xsd')))
        parser.add_argument('--policy', default=str(getattr(settings, 'RESOURCE_UI_POLICY_PATH', DIRECTORY / 'registry-ui-policy.json')))
        parser.add_argument('--schema-version', default=getattr(settings, 'RESOURCE_SCHEMA_VERSION', '3.3.0'))
        parser.add_argument('--output', default=str(getattr(settings, 'RESOURCE_UI_DESCRIPTOR_PATH', DIRECTORY / 'resource-ui.generated.json')))
        parser.add_argument('--against', help='Previously activated descriptor for compatibility checking.')
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--write', action='store_true')
        mode.add_argument('--check', action='store_true')

    def handle(self, *args, **options):
        try:
            sources.cache_clear()
            candidate = build_descriptor(*sources(options['schema'], options['policy'], options['schema_version']))
            output = Path(options['output'])
            baseline = Path(options['against']) if options['against'] else output
            if baseline.exists():
                errors = compatibility(json.loads(baseline.read_text()), candidate)
                if errors:
                    raise CommandError('Activation blocked:\n' + '\n'.join(errors))
            elif options['against']:
                raise CommandError('Previous descriptor does not exist: ' + str(baseline))
            rendered = json.dumps(candidate, indent=2, sort_keys=True) + '\n'
            if options['check']:
                if not output.exists() or output.read_text() != rendered:
                    raise CommandError('Descriptor drift: regenerate and review resource-ui.generated.json.')
                self.stdout.write('Resource descriptor matches selected sources: ' + candidate['revision'])
            elif options['write']:
                # Replace only after all generation and compatibility checks succeed.
                temporary = output.with_suffix(output.suffix + '.tmp')
                temporary.write_text(rendered)
                temporary.replace(output)
                self.stdout.write('Generated resource descriptor: ' + candidate['revision'])
            else:
                self.stdout.write(rendered)
        except (OSError, ValueError, KeyError, TypeError, SchemaUnavailable) as exc:
            raise CommandError(str(exc.__cause__ or exc)) from exc
