from django.test import SimpleTestCase, override_settings


class EnvironmentNoticeTests(SimpleTestCase):
    def test_notice_follows_deployment_not_debug_or_route(self):
        for deployment, debug, visible in (
                ('dev', False, True), ('staging', False, True), ('', False, True),
                ('production', False, False), ('prod', True, False)):
            with self.subTest(deployment=deployment, debug=debug), \
                    override_settings(DEPLOYMENT=deployment, DEBUG=debug, MIGRATION_PREVIEW_DEMOS=True):
                for path, routing in (('/about', {'biotools.canonical': True}),
                                      ('/', {'biotools.html': True})):
                    response = self.client.get(path, **routing)
                    self.assertEqual(response.status_code, 200)
                    if visible:
                        self.assertContains(response, 'Non-production instance.')
                        self.assertContains(response, 'href="https://bio.tools/"')
                    else:
                        self.assertNotContains(response, 'Non-production instance.')

    def test_environment_api_agrees_with_notice(self):
        for deployment, expected in (('dev', 'Development'), ('staging', 'Development'),
                                     ('production', 'Production'), ('prod', 'Production')):
            with self.subTest(deployment=deployment), override_settings(DEPLOYMENT=deployment):
                response = self.client.get('/env', HTTP_ACCEPT='application/json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected)
